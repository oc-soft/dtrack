from pathlib import Path
import os

import flock

class Idgen:
    """ id generator """

    @classmethod
    def get_id(cls, id_path: str | Path):
        result = None
        try:
            with open(id_path, "r+b", buffering=0) as f:
                flock.acquire_lock(f)
                try:
                    f.seek(0, os.SEEK_SET)
                    byte_data = f.read()
                    if len(byte_data):
                        result = int(byte_data.decode())
                        result += 1
                    else:
                        result = 1
                    f.seek(0, os.SEEK_SET)
                    f.write(f"{result}\n".encode()) 
                finally:
                    flock.release_lock(f)
        except FileNotFoundError:
            pass
        if result is None:
            try:
                f = open(id_path, "x")
                f.close()
            except FileExistsError: 
                pass
            result = cls.get_id(id_path) 
        return result
        

# vi: se ts=4 sw=4 et:
