"""Natural language query parsing"""

from datetime import datetime
from sqlalchemy import and_, select, func
from dateutil.relativedelta import relativedelta

from abcde.sql_models import Sensor, SensorMetric, SensorValue
from abcde.language_parser import SimilarityTag, ReTag, CompoundTag, DateTag


def last_to_dt(n, type_):
    kwargs = {type_: n}
    return datetime.now() - relativedelta(**kwargs)


EXTRACT_PIPES = {
    "date": (
        (
            (
                SimilarityTag("last", ["last", "previous", "past"]),
                ReTag("n", r"\d+"),
                CompoundTag(
                    None,
                    [
                        SimilarityTag("days", ["day", "days"]),
                        SimilarityTag("weeks", ["week", "weeks"]),
                        SimilarityTag("hours", ["hour", "hours"]),
                        SimilarityTag("minutes", ["minute", "minutes"]),
                        SimilarityTag("seconds", ["second", "seconds"]),
                        SimilarityTag("months", ["month", "months"]),
                    ],
                ),
            ),
            lambda x, y, z: last_to_dt(int(y[1]), z[0]),
        ),
        (
            (
                SimilarityTag("last", ["last", "previous", "past"]),
                CompoundTag(
                    None,
                    [
                        SimilarityTag("days", ["day", "days"]),
                        SimilarityTag("weeks", ["week", "weeks"]),
                        SimilarityTag("hours", ["hour", "hours"]),
                        SimilarityTag("minutes", ["minute", "minutes"]),
                        SimilarityTag("seconds", ["second", "seconds"]),
                        SimilarityTag("months", ["month", "months"]),
                    ],
                ),
            ),
            lambda x, y: last_to_dt(1, y[0]),
        ),
        ((SimilarityTag("since", ["since"]), DateTag("date")), lambda x, y: y[1]),
    ),
    "sensor": (
        (
            (
                SimilarityTag("sensor", ["sensor"]),
                ReTag("n", r"\d+"),
            ),
            lambda x, y: f"sensor{y[1]}",
        ),
        ((ReTag("sensor", r"sensor\d+"),), lambda x: x[1]),
        (
            (
                SimilarityTag("all", ["all"]),
                SimilarityTag("sensor", ["sensor", "sensors"]),
            ),
            lambda x, y: "_all_",
        ),
    ),
    "aggregation": (
        ((SimilarityTag("min", ["min"]),), lambda x: x[0]),
        ((SimilarityTag("max", ["max"]),), lambda x: x[0]),
        ((SimilarityTag("sum", ["sum"]),), lambda x: x[0]),
        ((SimilarityTag("average", ["average"]),), lambda x: x[0]),
    ),
    "metric": (
        ((SimilarityTag("temperature", ["temperature"]),), lambda x: x[0]),
        ((SimilarityTag("humidity", ["humidity"]),), lambda x: x[0]),
        ((SimilarityTag("rain", ["rain"]),), lambda x: x[0]),
        ((SimilarityTag("wind", ["wind"]),), lambda x: x[0]),
    ),
}


class Query:
    def __init__(self, text):
        self.text = text

    def parse(self):
        def check_match(pipe, words, index):
            tags = []
            for i, p in enumerate(pipe):
                idx = index + i
                if idx >= len(words):
                    return False, []
                word = words[idx].strip(".,")
                if m := p.matches(word):
                    tags.append((p.tag_name(), m))
                else:
                    return False, []
            return True, tags

        matches = {key: [] for key in EXTRACT_PIPES}
        words = self.text.split()
        index = 0
        while index < len(words):
            for type_, pipes in EXTRACT_PIPES.items():
                for pipe in pipes:
                    m, tags = check_match(pipe[0], words, index)
                    if m:
                        value = pipe[1](*tags)
                        matches[type_].append(value)
                        break
            index += 1

        missing = [k for k, v in matches.items() if v == [] and k != "date"]

        if missing:
            raise ValueError(
                f"Could not extract all information from the Query. Missing: {','.join(missing)}"
            )

        return matches

    def _latest_stmt(self, parsed):
        rank_col = (
            func.row_number()
            .over(
                partition_by=[SensorValue.sensor_id, SensorValue.metric_id],
                order_by=SensorValue.timestamp.desc(),
            )
            .label("rn")
        )

        # 3. Build the inner query with Joins and Filters
        inner_stmt = (
            select(
                Sensor.name.label("sensor"),
                SensorMetric.name.label("metric"),
                SensorMetric.unit.label("unit"),
                SensorValue.value.label("value"),
                rank_col,
            )
            .join(SensorValue, Sensor.id == SensorValue.sensor_id)
            .join(SensorMetric, SensorMetric.id == SensorValue.metric_id)
        )
        conditions = [SensorMetric.name.in_(parsed["metric"])]
        if "_all_" not in parsed["sensor"]:
            conditions.append(Sensor.name.in_(parsed["sensor"]))
        inner_stmt = inner_stmt.where(and_(*conditions))

        inner_stmt = inner_stmt.subquery()

        # 4. Select only the latest (Rank 1) from the subquery
        return select(inner_stmt).where(inner_stmt.c.rn == 1)

    def _date_stmt(self, parsed):
        stmt = (
            select(
                Sensor.name.label("sensor"),
                SensorMetric.name.label("metric"),
                SensorMetric.unit.label("unit"),
            )
            .join(SensorValue, Sensor.id == SensorValue.sensor_id)
            .join(SensorMetric, SensorMetric.id == SensorValue.metric_id)
            .group_by(Sensor.name, SensorMetric.name)
        )

        conditions = [
            SensorValue.timestamp >= parsed["date"][0],
            SensorMetric.name.in_(parsed["metric"]),
        ]

        if "_all_" not in parsed["sensor"]:
            conditions.append(Sensor.name.in_(parsed["sensor"]))

        stmt = stmt.where(and_(*conditions))

        if parsed["aggregation"][0] == "min":
            stmt = stmt.add_columns(
                func.min(SensorValue.value).label("value"),
            )
        elif parsed["aggregation"][0] == "max":
            stmt = stmt.add_columns(
                func.max(SensorValue.value).label("value"),
            )
        elif parsed["aggregation"][0] == "sum":
            stmt = stmt.add_columns(
                func.sum(SensorValue.value).label("value"),
            )
        elif parsed["aggregation"][0] == "average":
            stmt = stmt.add_columns(
                func.avg(SensorValue.value).label("value"),
            )
        else:
            raise ValueError(
                f"Unknown aggregation operation: {parsed['aggregation'][0]}"
            )

        return stmt

    def get_stmt(self):
        parsed = self.parse()
        if parsed["date"]:
            return self._date_stmt(parsed)
        return self._latest_stmt(parsed)
