"""API client exceptions."""

from typing import List, Union
from uuid import UUID

from requests import HTTPError, PreparedRequest, Response


class ErrResponse:
    """API error response schema."""

    def __init__(
        self,
        status_code: int = None,
        error_code: str = None,
        message: Union[str, List[str]] = None,
        response_id: UUID = None,
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.response_id = response_id


class TimewebCloudException(HTTPError):
    """Base exception for TimewebCloud."""

    def __init__(
        self,
        request: PreparedRequest = None,
        response: Response = None,
        error_code: str = None,
        status_code: str = None,
        message: Union[str, List[str]] = None,
        response_id: UUID = None,
    ):
        if message is not None:
            if isinstance(message, list):
                description = "; ".join(message)
            else:
                description = message
        else:
            description = response.reason
        super().__init__(description)
        self.request = request
        self.response = response
        self.error_code = error_code
        self.status_code = status_code
        self.message = description
        self.response_id = response_id


class UnauthorizedError(TimewebCloudException):
    """User is unauthorized. Mostly user does not have API access token."""


class MalformedResponseError(TimewebCloudException):
    """API respond non JSON response body, or with malformed JSON schema."""


class UnexpectedResponseError(TimewebCloudException):
    """API respond unexpected response. E.g. 502 Bad Gateway, etc."""


class BadRequestError(TimewebCloudException):
    """400 Bad Request."""


class ForbiddenError(TimewebCloudException):
    """403 Forbidden."""


class NotFoundError(TimewebCloudException):
    """404 Not Found."""


class ConflictError(TimewebCloudException):
    """409 Conflict."""


class LockedError(TimewebCloudException):
    """423 Locked."""


class TooManyRequestsError(TimewebCloudException):
    """429 Too Many Requests."""


class InternalServerError(TimewebCloudException):
    """500 Internal Server Error."""


class NetworkError(Exception):
    """Raises on requests.exceptions.ConnectionError."""
