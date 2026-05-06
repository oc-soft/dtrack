from pathlib import Path

import hashlib
import io
import os
import shutil
import tempfile
import zlib

import flock


def read_object_into_strm(
        data_dir : str | Path,
        oid,
        strm,
        chunk_size: int = 1024 ** 2):
    """
    Git オブジェクトをストリーミングで読み込み、
    (type, body_bytes) を返す。
    out が BytesIO の場合は、header + body を chunk 単位で out に書き込む。

    ※ body_bytes は最終的に全体を返すためメモリに乗るが、
      out を使う場合は body を返さず None にすることも可能。
    """
    path_data_dir = data_dir if isinstance(data_dir, Path) else Path(data_dir)
    obj_path = path_data_dir / "objects" / oid[:2] / oid[2:]

    # zlib ストリーム解凍器
    d = zlib.decompressobj()

    # header を読み終えたかどうか
    header = None
    header_parsed = False
    expected_size = None
    consumed = 0

    with open(obj_path, "rb+") as f:
        flock.acquire_lock(f)
        while True:
            comp_chunk = f.read(chunk_size)
            if not comp_chunk:
                break

            # 解凍（複数回に分かれる可能性あり）
            raw = d.decompress(comp_chunk)

            # raw を処理（header → body）
            offset = 0
            while True:
                if not header_parsed:
                    # header を探す
                    null_pos = raw.find(b"\0", offset)
                    if null_pos == -1:
                        # header がまだ終わらない → 次の chunk へ
                        # header が巨大になることは通常ないが、念のため out に書かない
                        break

                    header = raw[offset:null_pos].decode()
                    obj_type, size_str = header.split(" ")
                    expected_size = int(size_str)
                    header_parsed = True

                    offset = null_pos + 1
                else:
                    # body 部分
                    remaining = raw[offset:]
                    if not remaining:
                        break
                    elif strm is None:
                        break

                    consumed += len(remaining)
                    strm.write(remaining) 

                    break  # 次の raw chunk へ
            if header_parsed and strm is None:
                break
    # 解凍完了後 flush
    tail = d.flush()
    if tail:
        if not header_parsed:
            # header が tail に含まれる rare case
            null_pos = tail.index(b"\0")
            header = tail[:null_pos].decode()
            obj_type, size_str = header.split(" ")
            expected_size = int(size_str)
            header_parsed = True

            body_part = tail[null_pos+1:]
            consumed += len(body_part)
            if strm is not None:
                strm.write(body_part)
        else:
            consumed += len(tail)
            if strm is not None:
                strm.write(tail)

    # サイズチェック
    if strm is not None:
        if expected_size is not None and consumed != expected_size:
            raise ValueError(f"Object size mismatch: expected {expected_size}, got {consumed}")
    return obj_type

def read_object(data_dir : str | Path, oid):
    """reade object and return (type, body)"""
    obj_path = Path(data_dir) / "objects" / oid[:2] / oid[2:]

    data = b''
    with open(obj_path, "r+") as f: 
        flock.acquire_lock(f)
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
    data_dir: str | Path,
    obj_type: str,
    path: str | Path,
    chunk_size: int = 1024 * 1024):
    file_path = Path(path)
    size = file_path.stat().st_size

    # Git blob header
    header = f"{obj_type} {size}\0".encode()

    h = hashlib.sha1()
    h.update(header)

    compressor = zlib.compressobj()

    oid = None
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        try:
            tmp_file.write(compressor.compress(header))
            with open(path, "rb") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    h.update(chunk)
                    tmp_file.write(compressor.compress(chunk))
            tmp_file.write(compressor.flush())
            tmp_file.close()
            oid = h.hexdigest()
            obj_dir = Path(data_dir) / "objects" / oid[:2]
            obj_dir.mkdir(parents=True, exist_ok=True)

            obj_path = obj_dir / oid[2:]

            shutil.move(tmp_file.name, obj_path)
            tmp_file = None

        finally:
            if tmp_file is not None:
                os.remove(tmp_file.name)
    return oid


def write_object(data_dir, obj_type, body):
    header = f"{obj_type} {len(body)}\0".encode('utf-8')
    store = header + body

    oid = hashlib.sha1(store).hexdigest()
    compressed = zlib.compress(store)

    obj_dir = Path(data_dir) / "objects" / oid[:2]
    obj_dir.mkdir(parents=True, exist_ok=True)
    obj_path = obj_dir / oid[2:]

    with open(obj_path, "wb") as f:
        flock.acquire_lock(f)
        obj_path.write_bytes(compressed)

    return oid
# vi: se ts=4 sw=4 et:
