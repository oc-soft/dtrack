from pathlib import Path

from .objects import write_object, read_object
from .index import read_index

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

def read_tree(data_dir: str | Path, oid: str):
    obj_type, body = read_object(data_dir, oid) 
    result = None
    if obj_type == "tree":
        result = body
    return result

def iterate_tree_body(tree_body):
    i = 0
    while i < len(tree_body):
        # mode SP name \0 oid(20 bytes)
        space = tree_body.index(b" ", i)
        mode = tree_body[i:space].decode()

        null = tree_body.index(b"\0", space)
        name = tree_body[space+1:null].decode()

        oid_bytes = tree_body[null+1:null+21]
        oid_hex = oid_bytes.hex()

        yield {
            "name": name,
            "oid": oid_hex,
            "mode": mode
        }
        i = null + 21

 

def write_tree(data_dir):
    index_path = Path(data_dir) / "index"
    entries = read_index(index_path)

    tree_body = build_tree(entries)

    oid = write_object(data_dir, "tree", tree_body)
    return oid

