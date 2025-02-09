import logging
import traceback
from rest_framework.response import Response

logger = logging.getLogger(__name__)


def handle_internal_server_exception() -> Response:
    """Handles internal Server error exception

    Returns:
        Response: Http response
    """
    traceback.print_exc()
    logger.error(traceback.format_exc())
    return Response({"status": "error", "message": "Something went wrong"}, status=500)


class ValidationException(Exception):
    """Custom exception for validation errors"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
