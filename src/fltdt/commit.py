import hashlib
import os
import zlib
import time
from pathlib import Path
from .objects import write_object, read_object_into_strm, read_object
from .head import read_oid_from_head

def parse_commit(body: bytes):
    """
    commit オブジェクトの body を解析して
    {tree, parent, author, message} を返す
    """
    text = body.decode()
    lines = text.split("\n")

    info = {
        "tree": None,
        "parent": [],
        "author": None,
        "message": ""
    }

    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("tree "):
            info["tree"] = line[5:]
        elif line.startswith("parent "):
            info["parent"] += [line[7:]]
        elif line.startswith("author "):
            info["author"] = line[7:]
        elif line == "":
            # 空行の次からが commit message
            info["message"] = "\n".join(lines[i+1:])
            break
        i += 1

    return info

def create_commit(
    data_dir,
    tree_oid,
    parent_oids,
    author_name,
    author_email,
    message=""):

    # timestamp
    timestamp = int(time.time())

    lines = []
    lines.append(f"tree {tree_oid}")
    if isinstance(parent_oids, str):
        parent_oids = [ parent_oids ]
    if parent_oids is not None:
        try:
            for parent_oid in iter(parent_oids): 
                lines.append(f"parent {parent_oid}")
        except:
            pass
    lines.append(f"author {author_name} <{author_email}> {timestamp}")
    lines.append(f"committer {author_name} <{author_email}> {timestamp}")
    lines.append("")  # one white space
    lines.append(message)

    body = "\n".join(lines).encode()

    oid = write_object(git_dir, "commit", body)
    return oid

def get_commit_tree_oid(
        data_dir: str | Path,
        commit_id: str | None=None,
        chunk_size: int=1024 ** 2):
    """ get commit tree hash """
    if commit_id is None:
        commit_id = read_oid_from_head(data_dir)
    result = None
    if commit_id:
        oid_type = None
        oid_type = read_object_into_strm(
                data_dir, commit_id, None, chunk_size)
        if oid_type == "commit":
            _, body = read_object(data_dir, commit_id) 
            info = parse_commit(body) 
            result = info['tree'] 
    return result 

def iterate_commit(data_dir : str | Path, chunk_size: int = 1024 ** 2):
    """ iterate commit """
    current_oid = read_oid_from_head(data_dir) 
    while current_oid:
        oid_type = None
        oid_type = read_object_into_strm(
                data_dir, current_oid, None, chunk_size)
        if oid_type == "commit":
            _, body = read_object(data_dir, current_oid) 
            info = parse_commit(body) 
            info["oid"] = current_oid
            yield info
            if len(info["parent"]):
                current_oid = info["parent"][0]
            else:
                current_oid = None
        else:
            break
        

# vi: se ts=4 sw=4 et:
