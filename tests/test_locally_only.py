import pytest

from kenny import BaseAPIClient


@pytest.mark.skip
def test_real_api_request():
    """Useful for local debugging."""
    url = "https://api.publicapis.org"
    client = BaseAPIClient(url)

    response = client.get("entries")

    assert response.status_code == 200
