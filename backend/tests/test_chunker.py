import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))

from chunker import merge_blocks_to_chunks


def test_merge_blocks_preserves_page_range():
    blocks = [
        {"text": "First page", "page_no": 1},
        {"text": "Second page", "page_no": 2},
    ]

    chunks = merge_blocks_to_chunks(blocks, chunk_size=100, overlap=10)

    assert chunks == [
        {
            "text": "First page Second page",
            "page_start": 1,
            "page_end": 2,
        }
    ]


def test_merge_blocks_ignores_empty_input():
    assert merge_blocks_to_chunks([], chunk_size=100, overlap=10) == []
