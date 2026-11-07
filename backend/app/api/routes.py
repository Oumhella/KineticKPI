import json
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import get_db
from app.db.models import ImportBatch
from app.ingestion.schemas import DatasetType
from app.ingestion.service import DatasetValidationError, read_and_validate_dataset

router = APIRouter()


@router.post("/imports", status_code=status.HTTP_201_CREATED, tags=["ingestion"])
async def import_dataset(
    dataset_type: DatasetType = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    filename = Path(file.filename or "upload").name
    limit = settings.max_upload_size_mb * 1024 * 1024
    content = await file.read(limit + 1)
    if len(content) > limit:
        raise HTTPException(status_code=413, detail=f"File exceeds the {settings.max_upload_size_mb} MB upload limit.")

    try:
        frame = read_and_validate_dataset(content, filename, dataset_type)
    except DatasetValidationError as exc:
        raise HTTPException(status_code=422, detail={"message": str(exc), "issues": exc.issues}) from exc

    settings.upload_directory.mkdir(parents=True, exist_ok=True)
    extension = Path(filename).suffix.lower()
    stored_filename = f"{uuid4().hex}{extension}"
    destination = settings.upload_directory / stored_filename
    destination.write_bytes(content)
    batch = ImportBatch(
        dataset_type=dataset_type.value,
        original_filename=filename,
        stored_filename=stored_filename,
        row_count=len(frame),
        column_names=json.dumps(frame.columns.tolist()),
    )
    try:
        db.add(batch)
        db.commit()
        db.refresh(batch)
    except Exception:
        db.rollback()
        destination.unlink(missing_ok=True)
        raise
    return {
        "id": batch.id,
        "dataset_type": batch.dataset_type,
        "filename": batch.original_filename,
        "row_count": batch.row_count,
        "columns": frame.columns.tolist(),
        "created_at": batch.created_at,
    }


@router.get("/imports", tags=["ingestion"])
def list_imports(db: Session = Depends(get_db)) -> list[dict[str, object]]:
    batches = db.scalars(select(ImportBatch).order_by(ImportBatch.created_at.desc())).all()
    return [
        {
            "id": batch.id,
            "dataset_type": batch.dataset_type,
            "filename": batch.original_filename,
            "row_count": batch.row_count,
            "columns": json.loads(batch.column_names),
            "created_at": batch.created_at,
        }
        for batch in batches
    ]
