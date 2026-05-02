import os
import hashlib
import zlib
from pathlib import Path
from .objects import write_object
import struct

def read_index(path):
    if not path.exists():
        return []

    data = path.read_bytes()
    signature, version, count = struct.unpack(">4sLL", data[:12])
    if signature != b"DIRC":
        raise ValueError("Invalid index")

    entries = []
    offset = 12
    for _ in range(count):
        fields = struct.unpack(">LLLLLLLLLL20sH", data[offset:offset+62])
        ctime_s, ctime_n, mtime_s, mtime_n, dev, ino, mode, uid, gid, size, oid, flags = fields
        offset += 62

        name_len = flags & 0x0FFF
        name = data[offset:offset+name_len].decode()
        offset += name_len

        pad = (8 - (offset % 8)) % 8
        offset += pad

        entries.append({
            "mode": mode,
            "name": name,
            "oid": oid,
        })

    return entries


def build_tree(entries):
    """
    entries: list of {"mode": int, "name": str, "oid": bytes}
    """
    body = b""
    for e in sorted(entries, key=lambda x: x["name"]):
        mode_str = f"{e['mode']:o}"
        name = e["name"]
        body += f"{mode_str} {name}".encode() + b"\0" + e["oid"]
    return body


def write_tree(git_dir):
    index_path = Path(git_dir) / "index"
    entries = read_index(index_path)

    tree_body = build_tree(entries)

    oid = write_object(git_dir, "tree", tree_body)
    return oid

