#!/usr/bin/env python3
"""Copy the pre-rendered invitation image to the make.fun output path.

Deterministic and stdlib-only: reads entry.png beside this file, verifies it
is a PNG of at most 1024x1024 and 1 MiB, writes it atomically to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png), then reads the
output back and asserts byte equality.
"""
import os
import struct
from pathlib import Path

MAX_BYTES = 1048576
MAX_DIM = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def check_png(data: bytes) -> None:
    if len(data) > MAX_BYTES:
        raise ValueError(f"entry.png is {len(data)} bytes, over the 1 MiB limit")
    if not data.startswith(PNG_SIGNATURE) or len(data) < 24:
        raise ValueError("entry.png is not a PNG file")
    width, height = struct.unpack(">II", data[16:24])
    if width > MAX_DIM or height > MAX_DIM:
        raise ValueError(f"entry.png is {width}x{height}, over 1024x1024")


def main() -> None:
    here = Path(__file__).resolve().parent
    src = here / "entry.png"
    data = src.read_bytes()
    check_png(data)

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / "entry.png"

    tmp = out_dir / ".entry.png.tmp"
    tmp.write_bytes(data)
    os.replace(tmp, dst)

    written = dst.read_bytes()
    assert written == data, "output bytes differ from source entry.png"
    assert len(written) <= MAX_BYTES


if __name__ == "__main__":
    main()
