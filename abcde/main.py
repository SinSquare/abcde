"""abcde main app"""

from typing import Annotated
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, HTTPException
from sqlalchemy import select

from abcde import models
from abcde.utils import SessionDep, create_db_and_tables
from abcde.query_parser import Query as QueryParser
from abcde.sql_models import Sensor, SensorMetric, SensorValue


@asynccontextmanager
async def lifespan(_):
    await create_db_and_tables()
    yield


app = FastAPI(title="abcde", lifespan=lifespan)  # pylint: disable=unused-argument


@app.get(
    "/query",
    response_model=models.SensorMetricResult,
    response_model_exclude_unset=True,
    status_code=200,
)
async def get_query(
    data: Annotated[models.QueryInput, Query()],
    session: SessionDep,
):
    """GET query"""
    try:
        parser = QueryParser(data.query)
        stmt = parser.get_stmt()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    result = await session.execute(stmt)
    results = []
    for res in result.mappings().all():
        results.append(models.SensorMetric(**res))

    meta = models.QueryMeta(
        sensor=parser.parsed["sensor"],
        metric=parser.parsed["metric"],
        aggregation=parser.parsed["aggregation"][0],
        date=parser.parsed["date"][0] if len(parser.parsed["date"]) > 0 else None,
    )
    return models.SensorMetricResult(data=results, meta=meta)


@app.post(
    "/sensor",
    status_code=200,
)
async def post_sensor_data(
    data: models.SensorInput,
    session: SessionDep,
):
    """POST sensor"""
    result = await session.execute(select(Sensor).where(Sensor.name == data.sensor))
    sensor = result.scalars().first()

    result = await session.execute(
        select(SensorMetric).where(SensorMetric.name == data.metric)
    )
    metric = result.scalars().first()

    if not sensor:
        sensor = Sensor(name=data.sensor)
    if not metric:
        metric = SensorMetric(name=data.metric, unit=data.unit)

    session.add(SensorValue(value=data.value, sensor=sensor, metric=metric))
    await session.commit()
