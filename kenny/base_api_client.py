import typing as t
from typing_extensions import Unpack
from http.cookiejar import CookieJar
from dataclasses import dataclass, field

import requests


class RequestParams(t.TypedDict):
    """Typed interface for `requests.api.request`.

    `method` param is omitted as BaseAPIClient has a class method per HTTP method.
    """

    url: str
    params: t.Optional[t.Union[dict[str, t.Any], list[tuple[t.Any, ...]], list[bytes]]]
    data: t.Optional[t.Union[dict[str, t.Any], list[tuple[t.Any, ...]], list[bytes], list[t.IO[t.Any]]]]
    json: t.Optional[t.Any]
    headers: t.Optional[dict[str, t.Any]]
    cookies: t.Optional[t.Union[dict[str, t.Any], CookieJar]]
    files: t.Optional[dict[str, t.Any]]
    auth: t.Optional[tuple[t.Any, ...]]
    timeout: t.Optional[t.Union[float, tuple[float, float]]]
    allow_redirects: bool
    proxies: t.Optional[dict[str, str]]
    verify: bool
    stream: bool
    cert: t.Optional[t.Union[str, tuple[str, str]]]


@dataclass
class BaseAPIClient:
    """Base class to interface with an HTTP(S) API."""

    base_url: str
    headers: t.Optional[dict[str, t.Any]] = None
    cookies: t.Optional[t.Union[dict[str, t.Any], CookieJar]] = None
    auth: t.Optional[tuple[t.Any, ...]] = None
    timeout: t.Optional[t.Union[float, tuple[float, float]]] = None
    allow_redirects: bool = True
    proxies: t.Optional[dict[str, str]] = None
    verify: bool = True
    stream: bool = False
    cert: t.Optional[t.Union[str, tuple[str, str]]] = None
    raise_for_status: bool = True
    _session: requests.Session = field(init=False)

    def __post_init__(self):
        self.base_url = self.base_url[:-1] if self.base_url.endswith("/") else self.base_url
        self._session = requests.Session()

    def get(
        self,
        endpoint: t.Optional[str],
        raise_for_status: t.Optional[bool] = None,
        **request_params: Unpack[RequestParams],
    ) -> requests.Response:
        """Make a GET request."""
        return self._make_request("get", endpoint, raise_for_status, **request_params)

    def _make_request(
        self,
        http_method: str,
        endpoint: t.Optional[str] = None,
        raise_for_status: t.Optional[bool] = None,
        **request_params: Unpack[RequestParams],
    ) -> requests.Response:
        request_params_ = self._build_request_params(endpoint, **request_params)
        request_function = getattr(self._session, http_method)
        response = request_function(**request_params_)
        return self._handle_response(response, raise_for_status)

    def _build_request_params(
        self, endpoint: t.Optional[str], **request_params: Unpack[RequestParams]
    ) -> RequestParams:
        for param_name, param in dict(
            url=self._build_url(endpoint),
            headers=self.headers,
            cookies=self.cookies,
            auth=self.auth,
            timeout=self.timeout,
            allow_redirects=self.allow_redirects,
            proxies=self.proxies,
            verify=self.verify,
            stream=self.stream,
            cert=self.cert,
        ).items():
            request_params.setdefault(param_name, param)  # type: ignore

        self._merge_headers(**request_params)
        return request_params

    def _build_url(self, endpoint: t.Optional[str] = None) -> str:
        return f"{self.base_url}/{endpoint}" if endpoint else self.base_url

    def _merge_headers(self, **request_params: Unpack[RequestParams]) -> dict[str, t.Any]:
        headers = self.headers or {}
        headers.update(request_params.get("headers", {}))  # type: ignore
        request_params["headers"] = headers
        return headers

    def _handle_response(self, response: requests.Response, raise_for_status: t.Optional[bool]) -> requests.Response:
        raise_for_status = raise_for_status if raise_for_status is not None else self.raise_for_status
        if raise_for_status:
            response.raise_for_status()
        return response
