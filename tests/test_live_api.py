import json
import os
from urllib.request import Request, urlopen

import pytest


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("QAOPS_BASE_URL"),
    reason="QAOPS_BASE_URL must point to a deployed QA Ops API",
)
def test_deployed_api_health_and_sum():
    base_url = os.environ["QAOPS_BASE_URL"].rstrip("/")

    with urlopen(f"{base_url}/health", timeout=5) as response:
        health = json.loads(response.read())
    assert health["status"] == "ok"

    request = Request(
        f"{base_url}/api/sum",
        data=json.dumps({"a": 7, "b": 5}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=5) as response:
        result = json.loads(response.read())

    assert result == {"result": 12}
