from dataclasses import dataclass
from enum import StrEnum


class DatasetType(StrEnum):
    ORDERS = "orders"
    EMPLOYEES = "employees"
    DELIVERIES = "deliveries"
    PRODUCTIVITY = "productivity"


@dataclass(frozen=True)
class ColumnRule:
    name: str
    kind: str


DATASET_SCHEMAS: dict[DatasetType, tuple[ColumnRule, ...]] = {
    DatasetType.ORDERS: (
        ColumnRule("order_id", "text"), ColumnRule("order_date", "date"),
        ColumnRule("region", "text"), ColumnRule("amount", "number"),
        ColumnRule("status", "text"),
    ),
    DatasetType.EMPLOYEES: (
        ColumnRule("employee_id", "text"), ColumnRule("department", "text"),
        ColumnRule("region", "text"),
    ),
    DatasetType.DELIVERIES: (
        ColumnRule("delivery_id", "text"), ColumnRule("order_id", "text"),
        ColumnRule("promised_date", "date"), ColumnRule("delivered_date", "date"),
        ColumnRule("region", "text"),
    ),
    DatasetType.PRODUCTIVITY: (
        ColumnRule("employee_id", "text"), ColumnRule("date", "date"),
        ColumnRule("tasks_completed", "number"), ColumnRule("hours_worked", "number"),
    ),
}
