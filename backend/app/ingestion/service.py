from io import BytesIO

import pandas as pd

from app.ingestion.schemas import DATASET_SCHEMAS, DatasetType


class DatasetValidationError(ValueError):
    def __init__(self, issues: list[dict[str, object]]):
        self.issues = issues
        super().__init__("Dataset validation failed")


def read_and_validate_dataset(content: bytes, filename: str, dataset_type: DatasetType) -> pd.DataFrame:
    suffix = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    try:
        if suffix == "csv":
            frame = pd.read_csv(BytesIO(content))
        elif suffix == "xlsx":
            frame = pd.read_excel(BytesIO(content))
        else:
            raise DatasetValidationError([{"code": "unsupported_format", "message": "Upload a CSV or Excel file."}])
    except DatasetValidationError:
        raise
    except Exception as exc:
        raise DatasetValidationError([{"code": "unreadable_file", "message": "The file could not be read as a tabular dataset."}]) from exc

    frame.columns = [str(column).strip().lower() for column in frame.columns]
    issues: list[dict[str, object]] = []
    column_names = frame.columns.tolist()
    duplicated = sorted({name for name in column_names if column_names.count(name) > 1})
    if duplicated:
        issues.append({"code": "duplicate_columns", "columns": duplicated})
    if frame.empty:
        issues.append({"code": "empty_dataset", "message": "The file has no data rows."})

    rules = DATASET_SCHEMAS[dataset_type]
    missing = [rule.name for rule in rules if rule.name not in frame.columns]
    if missing:
        issues.append({"code": "missing_columns", "columns": missing})
    else:
        for rule in rules:
            values = frame[rule.name]
            blank = values.isna() | values.astype(str).str.strip().eq("")
            if blank.any():
                issues.append({"code": "missing_values", "column": rule.name, "rows": (blank[blank].index + 2).tolist()[:20]})
                continue
            if rule.kind == "number":
                invalid = pd.to_numeric(values, errors="coerce").isna()
            elif rule.kind == "date":
                invalid = pd.to_datetime(values, errors="coerce").isna()
            else:
                continue
            if invalid.any():
                issues.append({"code": f"invalid_{rule.kind}", "column": rule.name, "rows": (invalid[invalid].index + 2).tolist()[:20]})

    if issues:
        raise DatasetValidationError(issues)
    return frame
