from worker import Worker


class CustomWorker(Worker):
    def process_task(self, payload):
        """
        Override this method to implement your specific task processing logic
        """
        # Example implementation
        if not isinstance(payload, dict):
            raise ValueError("Payload must be a dictionary")

        task_type = payload.get("type")
        task_data = payload.get("data", {})

        if task_type == "process_data":
            return self.process_data_task(task_data)
        elif task_type == "generate_report":
            return self.generate_report_task(task_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    def process_data_task(self, data):
        # Add your data processing logic here
        return {
            "status": "success",
            "processed_items": len(data),
            "summary": "Data processed successfully",
        }

    def generate_report_task(self, data):
        # Add your report generation logic here
        return {
            "status": "success",
            "report_url": "https://example.com/reports/123",
            "summary": "Report generated successfully",
        }


if __name__ == "__main__":
    worker = CustomWorker()
    worker.run()
