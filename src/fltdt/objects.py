import hashlib
import zlib
from pathlib import Path

def read_object(data_dir, oid):
    """reade object and return (type, body)"""
    obj_path = Path(data_dir) / "objects" / oid[:2] / oid[2:]
    data = obj_path.read_bytes()

    raw = zlib.decompress(data)

    # "type size\0body" を分解
    null_index = raw.index(b"\0")
    header = raw[:null_index].decode()
    obj_type, size_str = header.split(" ")
    size = int(size_str)

    body = raw[null_index + 1:]

    if len(body) != size:
        raise ValueError("Object size mismatch")

    return obj_type, body


def write_path_to_object(
    data_dir: str,
    obj_type: str,
    path: str,
    chunk_size: int = 1024 * 1024):
    file_path = Path(path)
    size = file_path.stat().st_size

    # Git blob header
    header = f"{obj_type} {size}\0".encode("utf-8")

    h = hashlib.sha1()
    h.update(header)

    compressor = zlib.compressobj()

    compressed = compressor.compress(header)

    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
            compressed += compressor.compress(chunk)

    compressed += compressor.flush()

    oid = h.hexdigest()

    obj_dir = Path(data_dir) / "objects" / oid[:2]
    obj_dir.mkdir(parents=True, exist_ok=True)

    obj_path = obj_dir / oid[2:]

    if not obj_path.exists():
        with open(obj_path, "wb") as f:
            f.write(compressed)

    return oid


def write_object(data_dir, obj_type, body):
    header = f"{obj_type} {len(body)}\0".encode('utf-8')
    store = header + body

    oid = hashlib.sha1(store).hexdigest()
    compressed = zlib.compress(store)

    obj_dir = Path(data_dir) / "objects" / oid[:2]
    obj_dir.mkdir(parents=True, exist_ok=True)
    obj_path = obj_dir / oid[2:]

    if not obj_path.exists():
        obj_path.write_bytes(compressed)

    return oid
# vi: se ts=4 sw=4 et:
