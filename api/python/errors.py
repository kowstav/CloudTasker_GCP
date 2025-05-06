from typing import Optional

from flask import Response, jsonify


class APIError(Exception):
    """Base API Error class."""

    status_code = 500

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        payload: Optional[str] = None,
    ):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_response(self) -> tuple[Response, int]:
        response = {"error": self.message}
        if self.payload:
            response["details"] = (
                self.payload
            )  # this assumes self.payload is a dict or None
        return jsonify(response), self.status_code


class ValidationError(APIError):
    """Raised when input validation fails."""

    status_code = 400


class NotFoundError(APIError):
    """Raised when a resource is not found."""

    status_code = 404


class DatabaseError(APIError):
    """Raised when database operations fail."""

    status_code = 500
