"""test api"""

import tempfile
from unittest import mock
import os

import pytest

from abcde.utils import add_data


@pytest.fixture
def env():
    with tempfile.NamedTemporaryFile(delete=True) as tmp:
        print(tmp.name)
        env_vars = {"ABCDE_DB_URL": f"sqlite:///{tmp.name}"}
        with mock.patch.dict(os.environ, env_vars):
            yield env_vars


def test_api(env, client):
    add_data()

    q = "min temperature sensor1"
    resp = client.get("/query", params={"query": q})
    assert resp.status_code == 200
    assert resp.json() == [
        {"sensor": "sensor1", "metric": "temperature", "unit": "C", "value": 7.0}
    ]

    q = "min temperature, humidity sensor1 sensor2"
    resp = client.get("/query", params={"query": q})
    assert resp.status_code == 200
    assert resp.json() == [
        {"sensor": "sensor1", "metric": "humidity", "unit": "%", "value": 1.0},
        {"sensor": "sensor1", "metric": "temperature", "unit": "C", "value": 7.0},
        {"sensor": "sensor2", "metric": "humidity", "unit": "%", "value": 4.0},
        {"sensor": "sensor2", "metric": "temperature", "unit": "C", "value": 10.0},
    ]
