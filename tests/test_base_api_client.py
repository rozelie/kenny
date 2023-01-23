import pytest

from kenny import base_api_client


@pytest.fixture
def session(mocker):
    return mocker.patch("kenny.base_api_client.Session")


@pytest.fixture
def base_url():
    return "https://www.fake_api.com/api"


class TestBaseAPIClient:
    def test_post_init__sets_expected_attributes(self, base_url, session):
        client = base_api_client.BaseAPIClient(base_url)

        assert client.base_url == base_url
        assert client._session == session.return_value

    def test_post_init__trims_trailing_slash_in_url(self, base_url, session):
        base_url_with_trailing_slash = f"{base_url}/"

        client = base_api_client.BaseAPIClient(base_url_with_trailing_slash)

        assert client.base_url == base_url
