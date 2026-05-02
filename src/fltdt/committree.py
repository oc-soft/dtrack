import hashlib
import zlib
import time
from pathlib import Path
from .objects import write_object


def create_commit(
    data_dir,
    tree_oid,
    parent_oid,
    author_name,
    author_email,
    message=""):
    # timestamp
    timestamp = int(time.time())

    lines = []
    lines.append(f"tree {tree_oid}")
    if parent_oid:
        lines.append(f"parent {parent_oid}")
    lines.append(f"author {author_name} <{author_email}> {timestamp}")
    lines.append(f"committer {author_name} <{author_email}> {timestamp}")
    lines.append("")  # one white space
    lines.append(message)

    body = "\n".join(lines).encode()

    oid = write_object(git_dir, "commit", body)
    return oid

# vi: se ts=4 sw=4 et:
