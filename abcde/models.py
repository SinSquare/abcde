"""Request and response models."""

from pydantic import BaseModel, RootModel


class QueryInput(BaseModel):
    query: str


class SensorMetric(BaseModel):
    """SensorMetric"""

    sensor: str
    metric: str
    unit: str
    value: float


class SensorMetricResult(RootModel):
    """Sort Output model"""

    root: list[SensorMetric]

    def __iter__(self):  # pragma: no cover
        return iter(self.root)

    def __getitem__(self, item):  # pragma: no cover
        return self.root[item]
