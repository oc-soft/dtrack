#!/usr/bin/env python3
from .objects import write_path_to_object

def hash_and_write_blob(
    data_dir: str,
    path: str,
    chunk_size: int = 1024 * 1024):
    return write_path_to_object(data_dir, 'blob', path, chunk_size)

# vi: se ts=4 sw=4 et:
