"""Base module for Timeweb Cloud API client."""

import logging
import textwrap
from typing import Optional, Callable

import requests

from twc.__version__ import __version__, __pyversion__
from . import exceptions as exc


class TimewebCloudBase:
    """Base class for Timeweb Cloud API client."""

    # pylint: disable=method-hidden
    # pylint: disable=invalid-name

    API_BASE_URL = "https://api.timeweb.cloud"
    TIMEOUT = 100
    USER_AGENT = f"TWC-CLI/{__version__} Python {__pyversion__}"

    def __init__(
        self,
        api_token: str,
        api_base_url: Optional[str] = API_BASE_URL,
        api_path: Optional[str] = "/api/v1",
        headers: Optional[dict] = None,
        user_agent: Optional[str] = USER_AGENT,
        timeout: Optional[int] = TIMEOUT,
        hide_token: Optional[bool] = True,
        request_decorator: Optional[Callable] = None,
    ):
        self.api_token = api_token
        self.api_base_url = api_base_url
        self.api_path = api_path
        self.api_url = self.api_base_url + self.api_path
        self.api_url_v1 = self.api_base_url + "/api/v1"
        self.api_url_v2 = self.api_base_url + "/api/v2"
        self.timeout = timeout
        self.headers = requests.utils.default_headers()
        self.headers["User-Agent"] = user_agent
        self.headers["Authorization"] = f"Bearer {self.api_token}"
        self.log = logging.getLogger("api_client")
        self.hide_token = hide_token

        if headers:
            self.headers.update(headers)

        # Decorate _request()
        if request_decorator is not None:
            self._request = request_decorator(self._request)

    def _format_headers(self, headers: dict) -> str:
        """Format HTTP headers for log."""
        return "\n".join(f"{k}: {v}" for k, v in headers.items())

    def _secure_log(self, headers: dict) -> dict:
        """Replace API access token with placeholder."""
        _headers = headers.copy()
        if self.hide_token:
            _headers["Authorization"] = "Bearer <SENSITIVE_DATA_DELETED>"
        return _headers

    def _log_request(self, response: requests.Response) -> None:
        """Log HTTP requests."""
        res_body = response.text or "<NO_BODY>"
        req_body = response.request.body or "<NO_BODY>"
        if isinstance(req_body, (bytes, bytearray)):
            req_body = req_body.decode()

        self.log.debug(
            textwrap.dedent(
                """
            ---------------- Request ----------------
            {req.method} {req.url}
            {req_headers}

            {req_body}
            ---------------- Response ---------------
            {res.status_code} {res.reason} {res.url}
            {res_headers}

            {res_body}"""
            ).format(
                req=response.request,
                req_headers=self._format_headers(
                    self._secure_log(response.request.headers)
                ),
                req_body=req_body,
                res=response,
                res_headers=self._format_headers(response.headers),
                res_body=res_body,
            )
        )

    def _request(
        self,
        method: str,
        url: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        json: Optional[dict] = None,
        files: Optional[dict] = None,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        """Make request and handle errors."""

        if not timeout:
            timeout = self.timeout

        if not headers:
            headers = self.headers

        _headers = self._secure_log(headers)
        self.log.debug("Called with args: %s %s %s", method, url, _headers)

        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                params=params,
                data=data,
                json=json,
                files=files,
                timeout=timeout,
            )
        except requests.exceptions.ConnectionError as conerr:
            raise exc.NetworkError(f"Coul'd not connect to server: {conerr}")

        try:
            response.raise_for_status()
            self._log_request(response)
        except requests.HTTPError as e:
            self._log_request(response)

            # API issue: Bad response: 401 Unauthorized response haven't body
            # There is workaround about it - raise UnauthorizedError before
            # checking a JSON schema.
            if response.status_code == 401:
                raise exc.UnauthorizedError(
                    request=e.request,
                    response=e.response,
                ) from e

            try:
                error = exc.ErrResponse(**response.json())
            except requests.JSONDecodeError as err:
                raise exc.MalformedResponseError(
                    message="Response have no JSON schema or have invalid JSON syntax.",
                    request=e.request,
                    response=e.response,
                ) from err

            if response.status_code == 400:
                raise exc.BadRequestError(
                    request=e.request,
                    response=e.response,
                    status_code=error.status_code,
                    error_code=error.error_code,
                    message=error.message,
                    response_id=error.response_id,
                ) from e
            if response.status_code == 403:
                raise exc.ForbiddenError(
                    request=e.request,
                    response=e.response,
                    status_code=error.status_code,
                    error_code=error.error_code,
                    message=error.message,
                    response_id=error.response_id,
                ) from e
            if response.status_code == 404:
                raise exc.NotFoundError(
                    request=e.request,
                    response=e.response,
                    status_code=error.status_code,
                    error_code=error.error_code,
                    message=error.message,
                    response_id=error.response_id,
                ) from e
            if response.status_code == 409:
                raise exc.ConflictError(
                    request=e.request,
                    response=e.response,
                    status_code=error.status_code,
                    error_code=error.error_code,
                    message=error.message,
                    response_id=error.response_id,
                ) from e
            if response.status_code == 423:
                raise exc.LockedError(
                    request=e.request,
                    response=e.response,
                    status_code=error.status_code,
                    error_code=error.error_code,
                    message=error.message,
                    response_id=error.response_id,
                ) from e
            if response.status_code == 429:
                raise exc.TooManyRequestsError(
                    request=e.request,
                    response=e.response,
                    status_code=error.status_code,
                    error_code=error.error_code,
                    message=error.message,
                    response_id=error.response_id,
                ) from e
            if response.status_code == 500:
                raise exc.InternalServerError(
                    request=e.request,
                    response=e.response,
                    status_code=error.status_code,
                    error_code=error.error_code,
                    message=error.message,
                    response_id=error.response_id,
                ) from e
            raise exc.UnexpectedResponseError(e) from e

        return response
