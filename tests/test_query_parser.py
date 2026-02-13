"""test api"""

import datetime

import pytest
from sqlmodel import Session

from abcde.query_parser import Query
from abcde.models import SensorMetric


def test_parse(mocker, dt_now):
    dt_mock = mocker.patch("abcde.query_parser.datetime")
    dt_mock.now.return_value = dt_now

    parser = Query(
        "Give me the average temperature and humidity for sensor 1 in the last week."
    )
    result = parser.parse()
    assert result == {
        "date": [datetime.datetime(2025, 11, 24, 0, 0)],
        "sensor": ["sensor1"],
        "aggregation": ["average"],
        "metric": ["temperature", "humidity"],
    }

    parser = Query("min temperature for sensor1 sensor 2 in the past 7 days.")
    result = parser.parse()
    assert result == {
        "date": [datetime.datetime(2025, 11, 24, 0, 0)],
        "sensor": ["sensor1", "sensor2"],
        "aggregation": ["min"],
        "metric": ["temperature"],
    }

    parser = Query("min temperature for sensor1 sensor 2.")
    result = parser.parse()
    assert result == {
        "date": [],
        "sensor": ["sensor1", "sensor2"],
        "aggregation": ["min"],
        "metric": ["temperature"],
    }

    parser = Query("min temperature sensor1")
    result = parser.parse()
    assert result == {
        "date": [],
        "sensor": ["sensor1"],
        "aggregation": ["min"],
        "metric": ["temperature"],
    }

    parser = Query("min temperature sensor1 since 2012.01.01")
    result = parser.parse()
    assert result == {
        "date": [datetime.datetime(2012, 1, 1, 0, 0)],
        "sensor": ["sensor1"],
        "aggregation": ["min"],
        "metric": ["temperature"],
    }


def test_parse_similar(mocker, dt_now):
    dt_mock = mocker.patch("abcde.query_parser.datetime")
    dt_mock.now.return_value = dt_now

    parser = Query("min tempreature for all sensro previosu 7 dyas")
    result = parser.parse()
    assert result == {
        "date": [datetime.datetime(2025, 11, 24, 0, 0)],
        "sensor": ["_all_"],
        "aggregation": ["min"],
        "metric": ["temperature"],
    }


def test_parse_raise():
    parser = Query("min for all sensro previos")

    with pytest.raises(Exception) as excinfo:
        parser.parse()
    assert "Missing: metric" in str(excinfo.value)


def test_query(mocker, engine, test_data, dt_now):
    dt_mock = mocker.patch("abcde.query_parser.datetime")
    dt_mock.now.return_value = dt_now

    with Session(engine) as session:
        stmt = Query("min temperature sensor1 last 7 days").get_stmt()
        assert build_results(session.execute(stmt)) == [
            SensorMetric(sensor="sensor1", metric="temperature", unit="C", value=7.0)
        ]

        stmt = Query("max temperature sensor1 last 7 days").get_stmt()
        assert build_results(session.execute(stmt)) == [
            SensorMetric(sensor="sensor1", metric="temperature", unit="C", value=8.0)
        ]

        stmt = Query("sum temperature sensor1 last 7 days").get_stmt()
        assert build_results(session.execute(stmt)) == [
            SensorMetric(sensor="sensor1", metric="temperature", unit="C", value=7 + 8)
        ]

        stmt = Query("average temperature sensor1 last 7 days").get_stmt()
        assert build_results(session.execute(stmt)) == [
            SensorMetric(
                sensor="sensor1", metric="temperature", unit="C", value=(7 + 8) / 2
            )
        ]

        stmt = Query("min temperature all sensor last 7 days").get_stmt()
        result = [
            tuple(res.model_dump().values())
            for res in build_results(session.execute(stmt))
        ]
        assert set(result) == set(
            [
                tuple(
                    SensorMetric(
                        sensor="sensor1", metric="temperature", unit="C", value=7.0
                    )
                    .model_dump()
                    .values()
                ),
                tuple(
                    SensorMetric(
                        sensor="sensor2", metric="temperature", unit="C", value=10.0
                    )
                    .model_dump()
                    .values()
                ),
            ]
        )


def test_query_latest(mocker, engine, test_data, dt_now):
    dt_mock = mocker.patch("abcde.query_parser.datetime")
    dt_mock.now.return_value = dt_now

    with Session(engine) as session:
        stmt = Query("min temperature sensor1 dsf").get_stmt()
        assert build_results(session.execute(stmt)) == [
            SensorMetric(sensor="sensor1", metric="temperature", unit="C", value=7.0)
        ]


def build_results(result):
    results = []
    for res in result.mappings().all():
        results.append(SensorMetric(**res))
    return results
