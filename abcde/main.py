"""abcde main app"""

from typing import Annotated
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query

from abcde import models
from abcde.utils import SessionDep, create_db_and_tables
from abcde.query_parser import Query as QueryParser


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
    """query"""
    parser = QueryParser(data.query)
    stmt = parser.get_stmt()
    result = await session.execute(stmt)
    results = []
    for res in result.mappings().all():
        results.append(models.SensorMetric(**res))

    return results
