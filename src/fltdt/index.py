#!/usr/bin/env python3
import os
import struct
import hashlib
from pathlib import Path


INDEX_HEADER = b"DIRC"
INDEX_VERSION = 2

def read_index(path: str | Path):
    if not path.exists():
        return []

    data = path.read_bytes()

    if len(data) < 12:
        return []

    signature, version, count = struct.unpack(">4sLL", data[:12])
    if signature != INDEX_HEADER:
        raise ValueError("Invalid index signature")

    entries = []
    offset = 12
    for idx in range(count):
        # stat fields
        fields = struct.unpack(">LLLLLLLLLL20sH", data[offset:offset+62])
        ctime_s, ctime_n, mtime_s, mtime_n, dev, ino, mode, uid, gid, size, oid, flags = fields
        data_len = 62
        name_len = flags & 0x0FFF
        name_offset = offset + data_len 
        name = data[name_offset:name_offset+name_len].decode()
        data_len += name_len
        pad = 8 - (data_len % 8)
        data_len += pad
        offset += data_len
        entries.append({
            "ctime_s": ctime_s,
            "ctime_n": ctime_n,
            "mtime_s": mtime_s,
            "mtime_n": mtime_n,
            "dev": dev,
            "ino": ino,
            "mode": mode,
            "uid": uid,
            "gid": gid,
            "size": size,
            "oid": oid,
            "flags": flags,
            "name": name,
        })

    return entries


def write_index(path : str | Path, entries):
    entries = sorted(entries, key=lambda e: e["name"])
    body = b""
    for e in entries:
        name_bytes = e["name"].encode()
        flags = len(name_bytes) & 0x0FFF
        entry = struct.pack(
            ">LLLLLLLLLL20sH",
            e["ctime_s"], e["ctime_n"],
            e["mtime_s"], e["mtime_n"],
            e["dev"], e["ino"], e["mode"],
            e["uid"], e["gid"], e["size"],
            e["oid"], flags
        )
        entry += name_bytes

        pad = 8 - (len(entry) % 8)
        entry += b"\0" * pad
        body += entry

    header = struct.pack(">4sLL", INDEX_HEADER, INDEX_VERSION, len(entries))
    checksum = hashlib.sha1(header + body).digest()

    return path.write_bytes(header + body + checksum)


def update_index_add(
    data_dir: str | Path, 
    file_path: str | Path,
    entry_name: str, oid_hex):
    index_path = get_index_path(data_dir)
    entries = read_index(index_path)

    st = os.stat(file_path)
    oid = bytes.fromhex(oid_hex)
    new_entry = {
        "ctime_s": int(st.st_ctime),
        "ctime_n": 0,
        "mtime_s": int(st.st_mtime),
        "mtime_n": 0,
        "dev": st.st_dev,
        "ino": st.st_ino,
        "mode": st.st_mode,
        "uid": st.st_uid,
        "gid": st.st_gid,
        "size": st.st_size,
        "oid": oid,
        "flags": 0,
        "name": entry_name,
    }

    # 既存エントリを置き換え
    entries = [e for e in entries if e["name"] != entry_name]
    entries.append(new_entry)
    write_index(index_path, entries)

def get_index_path(data_dir: str | Path):
    """ get index path """
    return Path(data_dir) / "index"
    

