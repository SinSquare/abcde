from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


# pylint: disable=too-few-public-methods
class Base(DeclarativeBase):
    pass


# pylint: disable=too-few-public-methods
class Sensor(Base):
    __tablename__ = "sensors"

    # pylint: disable=unsubscriptable-object
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)


# pylint: disable=too-few-public-methods
class SensorMetric(Base):
    __tablename__ = "sensor_metrics"

    # pylint: disable=unsubscriptable-object
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    unit: Mapped[str] = mapped_column(String(30))


# pylint: disable=too-few-public-methods
class SensorValue(Base):
    __tablename__ = "sensor_values"

    # pylint: disable=unsubscriptable-object
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.now)
    value: Mapped[float] = mapped_column(Float)

    sensor_id: Mapped[int] = mapped_column(ForeignKey("sensors.id"))
    metric_id: Mapped[int] = mapped_column(ForeignKey("sensor_metrics.id"))

    sensor: Mapped["Sensor"] = relationship()
    metric: Mapped["SensorMetric"] = relationship()
