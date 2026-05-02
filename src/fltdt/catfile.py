import zlib
from pathlib import Path
from .objects import read_object

def cat_file_p(git_dir, oid):
    obj_type, body = read_object(git_dir, oid)

    if obj_type == "blob":
        return body.decode(errors="replace")

    elif obj_type == "tree":
        result = []
        i = 0
        while i < len(body):
            # mode SP name \0 oid(20 bytes)
            space = body.index(b" ", i)
            mode = body[i:space].decode()

            null = body.index(b"\0", space)
            name = body[space+1:null].decode()

            oid_bytes = body[null+1:null+21]
            oid_hex = oid_bytes.hex()

            result.append(f"{mode} {oid_hex} {name}")
            i = null + 21

        return "\n".join(result)

    elif obj_type == "commit":
        return body.decode()

    else:
        return None

# vi: se ts=4 sw=4 et:
