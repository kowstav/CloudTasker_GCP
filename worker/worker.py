import json
import logging
import os
import signal
import sys
import time
from concurrent.futures import TimeoutError
from datetime import datetime

import psycopg2
from google.cloud import pubsub_v1  # type: ignore
from psycopg2.extras import Json

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Worker:
    def __init__(self):
        self.running = True
        self.subscriber = None
        self.subscription_path = None
        self.db_conn = None
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        signal.signal(signal.SIGINT, self.handle_shutdown)

    def init_pubsub(self):
        """Initialize Pub/Sub subscriber"""
        subscriber = pubsub_v1.SubscriberClient()
        subscription_path = subscriber.subscription_path(
            os.environ["PROJECT_ID"], os.environ["PUBSUB_SUBSCRIPTION"]
        )
        return subscriber, subscription_path

    def get_db_connection(self):
        """Create database connection"""
        return psycopg2.connect(
            host=os.environ["DB_HOST"],
            dbname="tasks",
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            sslmode="require",
        )

    def process_task(self, payload):
        """
        Process the task payload
        Override this method to implement actual task processing logic
        """
        # Simulating work
        time.sleep(2)
        return {"status": "success", "processed_at": datetime.utcnow().isoformat()}

    def callback(self, message):
        """Handle incoming Pub/Sub messages"""
        try:
            logger.info(f"Received message: {message.message_id}")
            # Parse message data
            data = json.loads(message.data.decode("utf-8"))
            job_id = data["job_id"]
            payload = data["payload"]
            # Update status to PROCESSING
            with self.db_conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE jobs
                    SET status = 'PROCESSING', updated_at = %s
                    WHERE id = %s
                    """,
                    (datetime.utcnow(), job_id),
                )
                self.db_conn.commit()
            # Process the task
            try:
                result = self.process_task(payload)
                status = "COMPLETED"
            except Exception as e:
                logger.error(f"Task processing failed: {str(e)}")
                result = {"error": str(e)}
                status = "FAILED"
            # Update final status
            with self.db_conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE jobs
                    SET status = %s, result = %s, updated_at = %s
                    WHERE id = %s
                    """,
                    (status, Json(result), datetime.utcnow(), job_id),
                )
                self.db_conn.commit()
            # Acknowledge the message
            message.ack()
            logger.info(f"Processed message {message.message_id} for job {job_id}")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            message.nack()

    def handle_shutdown(self, signum, frame):
        """Handle graceful shutdown"""
        logger.info("Received shutdown signal")
        self.running = False
        if self.subscriber:
            self.subscriber.stop()
        if self.db_conn:
            self.db_conn.close()
        sys.exit(0)

    def run(self):
        """Main worker loop"""
        try:
            self.subscriber, self.subscription_path = self.init_pubsub()
            self.db_conn = self.get_db_connection()

            streaming_pull_future = self.subscriber.subscribe(
                self.subscription_path, callback=self.callback
            )
            logger.info(f"Listening for messages on {self.subscription_path}")
            with self.subscriber:
                try:
                    streaming_pull_future.result()
                except TimeoutError:
                    streaming_pull_future.cancel()
                    streaming_pull_future.result()
        except Exception as e:
            logger.error(f"Worker failed: {str(e)}")
            raise
        finally:
            if self.db_conn:
                self.db_conn.close()


if __name__ == "__main__":
    worker = Worker()
    worker.run()
