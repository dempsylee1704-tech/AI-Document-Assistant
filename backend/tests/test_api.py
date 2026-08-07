import sys
from io import BytesIO
from pathlib import Path

import pytest
from fastapi import HTTPException, UploadFile
from starlette.datastructures import Headers

APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))

from api import health_check, validate_pdf
from io_utils import get_pdf_path_by_doc_id


def make_upload(filename: str, content_type: str, size: int = 0) -> UploadFile:
    return UploadFile(
        file=BytesIO(b""),
        filename=filename,
        size=size,
        headers=Headers({"content-type": content_type}),
    )


def test_health_check_reports_configuration_state():
    result = health_check()

    assert result["status"] == "ok"
    assert set(result["services"]) == {"openai_configured", "qdrant_configured"}


def test_validate_pdf_accepts_a_pdf():
    upload = make_upload("report.pdf", "application/pdf")

    assert validate_pdf(upload) == "report.pdf"


def test_validate_pdf_rejects_an_unsupported_file():
    upload = make_upload("notes.txt", "text/plain")

    with pytest.raises(HTTPException) as error:
        validate_pdf(upload)

    assert error.value.status_code == 400


def test_pdf_lookup_rejects_path_traversal():
    assert get_pdf_path_by_doc_id("../../private") is None
