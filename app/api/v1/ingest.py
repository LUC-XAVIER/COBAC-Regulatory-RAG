import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.config import settings
from app.dependencies import get_embedding_model, get_vector_index, get_chunk_store
from app.services.loader import extract_pages
from app.services.chunking import chunk_pages
from app.schemas.ingest import IngestResponse, Status

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    ingested: list[str] = []
    failed: list[str] = []
    all_chunks = []

    for upload in files:
        if not upload.filename or not upload.filename.lower().endswith(".pdf"):
            failed.append(upload.filename or "unknown")
            continue

        pdf_path = settings.RAW_DIR / upload.filename
        settings.RAW_DIR.mkdir(parents=True, exist_ok=True)

        try:
            with open(pdf_path, "wb") as f:
                shutil.copyfileobj(upload.file, f)

            pages = extract_pages(pdf_path)
            chunks = chunk_pages(pages)
            all_chunks.extend(chunks)
            ingested.append(upload.filename)
        except Exception:
            failed.append(upload.filename or "unknown")
        finally:
            await upload.close()

    if not all_chunks:
        status = Status.FAILURE if not ingested else Status.SUCCESS
        return IngestResponse(
            ingested=ingested, failed=failed, total_chunks=0, status=status,
        )

    embedding_model = get_embedding_model()
    index = get_vector_index()
    chunk_store = get_chunk_store()

    texts = [c.text for c in all_chunks]
    vectors = embedding_model.embed(texts)

    start_id = len(chunk_store._store)
    ids = list(range(start_id, start_id + len(all_chunks)))

    for chunk_id, chunk in zip(ids, all_chunks):
        chunk_store.add(chunk_id, chunk)

    index.add(vectors, ids)

    settings.INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    index.save(settings.INDEX_PATH)
    chunk_store.save(settings.CHUNKS_PATH)

    status = Status.SUCCESS if not failed else Status.PARTIAL
    return IngestResponse(
        ingested=ingested, failed=failed, total_chunks=len(all_chunks), status=status,
    )
