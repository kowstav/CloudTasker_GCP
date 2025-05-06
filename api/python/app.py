import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import psycopg2
from flask import Flask, Response, jsonify, request
from psycopg2.extensions import connection

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db_connection() -> connection:
    """Create and return a database connection."""
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname="tasks",
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        sslmode="require",
    )


@app.route("/health", methods=["GET"])
def health_check() -> Tuple[Response, int]:
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200


@app.route("/task", methods=["POST"])
def create_task() -> Tuple[Response, int]:
    """Create a new task."""
    try:
        # Requesting JSON payload from the client
        data: Optional[Dict[str, Any]] = request.get_json()

        # Validate the received data
        if not data:
            return jsonify({"error": "No payload provided"}), 400

        # Insert task into database
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                now = datetime.utcnow()
                cur.execute(
                    """
                    INSERT INTO jobs (payload, status, created_at, updated_at)
                    VALUES (%s, 'PENDING', %s, %s)
                    RETURNING id
                    """,
                    (json.dumps(data), now, now),
                )
                job_id_row = cur.fetchone()
                if job_id_row is None:
                    return (
                        jsonify({"error": "Failed to create task, no job ID returned"}),
                        500,
                    )
                job_id = job_id_row[0]
                conn.commit()

        return jsonify({"job_id": job_id, "status": "PENDING"}), 201

    except psycopg2.DatabaseError as db_error:
        logger.error(f"Database error: {str(db_error)}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
