from typing import TypedDict, Optional, Union, Any, IO
from typing_extensions import Unpack
from http.cookiejar import CookieJar
from dataclasses import dataclass, field

import requests


class RequestParams(TypedDict):
    """Typed interface for `requests.api.request`.

    `method` param is omitted as BaseAPIClient has a class method per HTTP method.
    """

    url: str
    params: Optional[Union[dict[str, Any], list[tuple[Any, ...]], list[bytes]]]
    data: Optional[Union[dict[str, Any], list[tuple[Any, ...]], list[bytes], list[IO[Any]]]]
    json: Optional[Any]
    headers: Optional[dict[str, Any]]
    cookies: Optional[Union[dict[str, Any], CookieJar]]
    files: Optional[dict[str, Any]]
    auth: Optional[tuple[Any, ...]]
    timeout: Optional[Union[float, tuple[float, float]]]
    allow_redirects: bool
    proxies: Optional[dict[str, str]]
    verify: bool
    stream: bool
    cert: Optional[Union[str, tuple[str, str]]]


@dataclass
class BaseAPIClient:
    """Base class to interface with an HTTP(S) API."""

    base_url: str
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
    _session: requests.Session = field(init=False)

    def __post_init__(self):
        self.base_url = self.base_url[:-1] if self.base_url.endswith("/") else self.base_url
        self._session = requests.Session()

    def get(
        self,
        endpoint: Optional[str],
        raise_for_status: Optional[bool] = None,
        **request_params: Unpack[RequestParams],
    ) -> requests.Response:
        """Make a GET reques"""
        return self._make_request("get", endpoint, raise_for_status, **request_params)

    def _make_request(
        self,
        http_method: str,
        endpoint: Optional[str] = None,
        raise_for_status: Optional[bool] = None,
        **request_params: Unpack[RequestParams],
    ) -> requests.Response:
        request_params_ = self._build_request_params(endpoint, **request_params)
        request_function = getattr(self._session, http_method)
        response = request_function(**request_params_)
        return self._handle_response(response, raise_for_status)

    def _build_request_params(
        self, endpoint: Optional[str], **request_params: Unpack[RequestParams]
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

    def _build_url(self, endpoint: Optional[str] = None) -> str:
        return f"{self.base_url}/{endpoint}" if endpoint else self.base_url

    def _merge_headers(self, **request_params: Unpack[RequestParams]) -> dict[str, Any]:
        headers = self.headers or {}
        headers.update(request_params.get("headers", {}))  # type: ignore
        request_params["headers"] = headers
        return headers

    def _handle_response(self, response: requests.Response, raise_for_status: Optional[bool]) -> requests.Response:
        raise_for_status = raise_for_status if raise_for_status is not None else self.raise_for_status
        if raise_for_status:
            response.raise_for_status()
        return response
