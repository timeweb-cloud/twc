class TimewebCloudException(Exception):
    """Base exception for TimewebCloud."""


class UnauthorizedError(TimewebCloudException):
    """User is unauthorized. Mostly user does not have API access token."""

    def __init__(self, *args, msg="Unauthorized", **kwargs):
        super().__init__(msg, *args, **kwargs)


class NonJSONResponseError(TimewebCloudException):
    """API respond non JSON response body, but application/json is expected."""

    def __init__(
        self, *args, msg="application/json response is expected", **kwargs
    ):
        super().__init__(msg, *args, **kwargs)


class BadResponseError(TimewebCloudException):
    """API respond error status code with application/json error message."""


class UnexpectedResponseError(TimewebCloudException):
    """API respond unexpected response. E.g. 502 Bad Gateway, etc."""
