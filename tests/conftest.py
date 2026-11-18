import os
import requests
import pytest

# Each learner's app runs on their own VM, normally localhost from inside it.
BASE_URL = os.environ.get("PX_URL", "http://localhost:8000")
API_KEY = os.environ.get("PX_KEY", "")


def _headers():
    h = {"X-API-Key": API_KEY}
    # Only needed if the app was started with REQUIRE_LEARNER_MODEL=1 (not the
    # Day 1 default recommendation - see DAY1_SETUP.md).
    if os.environ.get("AOAI_ENDPOINT"):
        h.update({
            "X-Model-Endpoint": os.environ["AOAI_ENDPOINT"],
            "X-Model-Key": os.environ["AOAI_KEY"],
            "X-Model-Chat-Deployment": os.environ["AOAI_CHAT"],
        })
    return h


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture
def ask():
    """Call the running PX Service Assistant and return the raw HTTP response."""
    def _ask(question: str, **kw):
        payload = {"question": question, **kw}
        return requests.post(f"{BASE_URL}/ask", headers=_headers(), json=payload, timeout=60)
    return _ask
