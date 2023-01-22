import pytest
from kenny import BaseAPIClient


@pytest.fixture
def requests_session(mocker):
    return mocker.patch("requests.Session")


@pytest.fixture
def base_url():
    return "https://www.fake_api.com/api"


class TestBaseAPIClient:
    def test_post_init__sets_expected_attributes(self, base_url, requests_session):
        client = BaseAPIClient(base_url)

        assert client.base_url == base_url
        assert client._session == requests_session.return_value

    def test_post_init__trims_trailing_slash_in_url(self, base_url, requests_session):
        base_url_with_trailing_slash = f"{base_url}/"

        client = BaseAPIClient(base_url_with_trailing_slash)

        assert client.base_url == base_url
