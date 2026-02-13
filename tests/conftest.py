"""conftest"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
import datetime

from abcde.main import app
from abcde.sql_models import Sensor, SensorMetric, SensorValue, Base


@pytest.fixture(scope="function")
def client():
    return TestClient(app)


@pytest.fixture(scope="function")
def engine():
    db = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=db)
    yield db
    db.dispose()


@pytest.fixture()
def dt_now():
    return datetime.datetime(2025, 12, 1)


@pytest.fixture()
def test_data(engine, dt_now):
    dt1week = datetime.datetime(2025, 11, 24, 0, 0)
    dt2week = datetime.datetime(2025, 11, 17, 0, 0)

    with Session(engine) as session:
        sensor1 = Sensor(name="sensor1")
        sensor2 = Sensor(name="sensor2")

        metric1 = SensorMetric(name="humidity", unit="%")
        metric2 = SensorMetric(name="temperature", unit="C")

        values = [
            # sensor1 - metric1
            SensorValue(value=1, timestamp=dt_now, sensor=sensor1, metric=metric1),
            SensorValue(value=2, timestamp=dt1week, sensor=sensor1, metric=metric1),
            SensorValue(value=3, timestamp=dt2week, sensor=sensor1, metric=metric1),
            # sensor2 - metric1
            SensorValue(value=4, timestamp=dt_now, sensor=sensor2, metric=metric1),
            SensorValue(value=5, timestamp=dt1week, sensor=sensor2, metric=metric1),
            SensorValue(value=6, timestamp=dt2week, sensor=sensor2, metric=metric1),
            # sensor1 - metric2
            SensorValue(value=7, timestamp=dt_now, sensor=sensor1, metric=metric2),
            SensorValue(value=8, timestamp=dt1week, sensor=sensor1, metric=metric2),
            SensorValue(value=9, timestamp=dt2week, sensor=sensor1, metric=metric2),
            # sensor2 - metric2
            SensorValue(value=10, timestamp=dt_now, sensor=sensor2, metric=metric2),
            SensorValue(value=11, timestamp=dt1week, sensor=sensor2, metric=metric2),
            SensorValue(value=12, timestamp=dt2week, sensor=sensor2, metric=metric2),
        ]

        session.add_all(values)
        session.commit()
