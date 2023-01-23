from dataclasses import dataclass, field
from http.cookiejar import CookieJar
from typing import Any, Optional, Union

from requests import Response, Session


@dataclass
class RequestParams:
    """Params for `requests.api.request` and `BaseAPIClient`."""

    headers: Optional[dict[str, Any]] = None
    cookies: Optional[Union[dict[str, Any], CookieJar]] = None
    auth: Optional[tuple[Any, ...]] = None
    timeout: Optional[Union[float, tuple[float, float]]] = None
    allow_redirects: bool = True
    proxies: Optional[dict[str, str]] = None
    verify: bool = True
    stream: bool = False
    cert: Optional[Union[str, tuple[str, str]]] = None
    raise_for_status: bool = True

    @property
    def requests_kwargs(self) -> dict:
        """Keyword args for `requests.api.request`."""
        return dict(
            headers=self.headers,
            cookies=self.cookies,
            auth=self.auth,
            timeout=self.timeout,
            allow_redirects=self.allow_redirects,
            proxies=self.proxies,
            verify=self.verify,
            stream=self.stream,
            cert=self.cert,
        )


@dataclass
class BaseAPIClient:
    """Base class to interface with an HTTP(S) API."""

    base_url: str
    request_defaults: RequestParams = RequestParams()
    _session: Session = field(init=False)

    def __post_init__(self):
        self.base_url = self.base_url[:-1] if self.base_url.endswith("/") else self.base_url
        self._session = Session()

    def get(self, endpoint: Optional[str], request_params: Optional[RequestParams] = None) -> Response:
        """Make a GET request."""
        return self._make_request("get", endpoint, request_params)

    def delete(self, endpoint: Optional[str], request_params: Optional[RequestParams] = None) -> Response:
        """Make a DELETE request."""
        return self._make_request("delete", endpoint, request_params)

    def head(self, endpoint: Optional[str], request_params: Optional[RequestParams] = None) -> Response:
        """Make a HEAD request."""
        return self._make_request("head", endpoint, request_params)

    def options(self, endpoint: Optional[str], request_params: Optional[RequestParams] = None) -> Response:
        """Make an OPTIONS request."""
        return self._make_request("options", endpoint, request_params)

    def patch(self, endpoint: Optional[str], request_params: Optional[RequestParams] = None) -> Response:
        """Make a PATCH request."""
        return self._make_request("patch", endpoint, request_params)

    def post(self, endpoint: Optional[str], request_params: Optional[RequestParams] = None) -> Response:
        """Make a POST request."""
        return self._make_request("post", endpoint, request_params)

    def put(self, endpoint: Optional[str], request_params: Optional[RequestParams] = None) -> Response:
        """Make a PUT request."""
        return self._make_request("put", endpoint, request_params)

    def _make_request(
        self, http_method: str, endpoint: Optional[str] = None, request_params: Optional[RequestParams] = None
    ) -> Response:
        request_function = getattr(self._session, http_method)
        request_params_ = self._build_request_params(endpoint, request_params)
        response = request_function(**request_params_)
        return self._handle_response(response)

    def _build_request_params(
        self, endpoint: Optional[str], request_params: Optional[RequestParams] = None
    ) -> dict[str, Any]:
        requests_kwargs = self.request_defaults.requests_kwargs
        if request_params:
            requests_kwargs = RequestParams({**requests_kwargs, **request_params.requests_kwargs}).requests_kwargs

        return dict(url=self._build_url(endpoint), **requests_kwargs)

    def _build_url(self, endpoint: Optional[str] = None) -> str:
        return f"{self.base_url}/{endpoint}" if endpoint else self.base_url

    def _handle_response(self, response: Response) -> Response:
        if self.request_defaults.raise_for_status:
            response.raise_for_status()
        return response
