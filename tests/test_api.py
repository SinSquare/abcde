"""test api"""

import tempfile
from unittest import mock
import os

import pytest

from abcde.utils import add_data, get_engine, get_async_engine


@pytest.fixture
def env():
    with tempfile.NamedTemporaryFile(delete=True) as tmp:
        env_vars = {"ABCDE_DB_URL": f"sqlite:///{tmp.name}"}
        with mock.patch.dict(os.environ, env_vars):
            yield env_vars


def test_api(env, client):
    get_engine.cache_clear()
    get_async_engine.cache_clear()
    add_data()

    q = "min temperature sensor1"
    resp = client.get("/query", params={"query": q})
    assert resp.status_code == 200
    assert resp.json()["data"] == [
        {"sensor": "sensor1", "metric": "temperature", "unit": "C", "value": 7.0}
    ]

    q = "min temperature, humidity sensor1 sensor2"
    resp = client.get("/query", params={"query": q})
    assert resp.status_code == 200
    assert resp.json()["data"] == [
        {"sensor": "sensor1", "metric": "humidity", "unit": "%", "value": 1.0},
        {"sensor": "sensor1", "metric": "temperature", "unit": "C", "value": 7.0},
        {"sensor": "sensor2", "metric": "humidity", "unit": "%", "value": 4.0},
        {"sensor": "sensor2", "metric": "temperature", "unit": "C", "value": 10.0},
    ]


def test_post(env, client):
    get_engine.cache_clear()
    get_async_engine.cache_clear()
    add_data()

    q = "min temperature sensor3"
    resp = client.get("/query", params={"query": q})
    assert resp.json()["data"] == []

    payload = {
        "sensor": "sensor3",
        "metric": "temperature",
        "unit": "C",
        "value": 10,
    }

    resp = client.post("/sensor", json=payload)
    assert resp.status_code == 200

    resp = client.get("/query", params={"query": q})
    assert resp.json()["data"] == [
        {"sensor": "sensor3", "metric": "temperature", "unit": "C", "value": 10}
    ]

    payload["value"] = 5
    payload["sensor"] = "  sensor   3  "
    payload["metric"] = "  tempe rat ure  "
    resp = client.post("/sensor", json=payload)
    assert resp.status_code == 200

    resp = client.get("/query", params={"query": q})
    assert resp.json()["data"] == [
        {"sensor": "sensor3", "metric": "temperature", "unit": "C", "value": 5}
    ]

    resp = client.get(
        "/query", params={"query": "average temperature sensor3 last week"}
    )
    assert resp.json()["data"] == [
        {"sensor": "sensor3", "metric": "temperature", "unit": "C", "value": 7.5}
    ]

    payload["metric"] = "rain"
    payload["unit"] = "mm"

    resp = client.post("/sensor", json=payload)
    assert resp.status_code == 200

    resp = client.get("/query", params={"query": "average rain sensor3 last week"})
    assert resp.json()["data"] == [
        {"sensor": "sensor3", "metric": "rain", "unit": "mm", "value": 5}
    ]
