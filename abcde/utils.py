from typing import Annotated
from datetime import datetime, timedelta
import functools

from fastapi import Depends
from sqlmodel import Session, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from abcde.config import Config
from abcde.sql_models import Sensor, SensorMetric, SensorValue, Base


@functools.lru_cache()
def get_engine():
    """Return the config loaded from envvars."""
    config = Config()

    connect_args = {"check_same_thread": False}
    engine = create_engine(config.db_url, connect_args=connect_args)

    return engine


@functools.lru_cache()
def get_async_engine():
    config = Config()
    connect_args = {"check_same_thread": False}
    url = config.db_url
    url = url.replace("sqlite:", "sqlite+aiosqlite:")
    engine = create_async_engine(url, connect_args=connect_args)
    return engine


async def create_db_and_tables():
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session():
    engine = get_async_engine()
    async with AsyncSession(engine) as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


def add_data():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    with Session(engine) as session:
        dt_now = datetime.now()
        dt1week = dt_now - timedelta(weeks=1)
        dt2week = dt1week - timedelta(weeks=1)

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


if __name__ == "__main__":
    add_data()
