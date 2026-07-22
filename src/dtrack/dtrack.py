from pathlib import Path

import io
import os
import re

import flidgen
import flock
import fltdt
import tgstore
import tempfile


class Dtrack:
    """ data tracking management """
    @classmethod
    def get_content(
            cls,
            content_id: int, path_template: str, dst_strm,
            chunk_size: int = 1024 ** 2):
        """ 
get content specified id from release directory.

Parameters
__________

content_id: int content id

path_template : str

dst_strm: io.BufferedIOBase

chunk_size : temporary buffer size as bytes for copying. default size are 1024 ** 2



Returns
_______

header: dict

"""
        path_str = path_template.format(id=content_id)  
        result = None
        with open(path_str, "r+") as fp:
            flock.acquire_lock(fp)
            result = tgstore.TgStore.read(
                    path_str, dst_strm, chunk_size)
        return result

    @classmethod
    def get_header(
            cls,
            content_id: int, path_template: str | Path):
        """
get content header specified id release directory.

Parameters
__________

content_id: int content id

path_template : str

Returns
_______

dict

```
    {
        tags: ['svg', 'img'],
        'content-type': 'image/svg+xml',
        'note': 'My icon',
        'title': 'My page favicon'
    }
```
"""
        path_str = path_template.format(id=content_id) 
        result = None
        with open(path_str, "r+") as fp:
            flock.acquire_lock(fp)
            result = tgstore.TgStore.read_header(path_str)
        return result
    @classmethod
    def update_content(
            cls, content_id: int, path_template: str,
            new_contents, chunk_size : int=1024 ** 2):
        """
update content in working directry.

Parameters
__________

new_contents: io.BufferedIOBase

path_template : str

content_id : int

chunk_size : temporary buffer size as bytes for copying. default size are 1024 ** 2


"""
        path_str = path_template.format(id = content_id) 
        with open(path_str, "r+") as fp:
            flock.acquire_lock(fp)
            header = tgstore.TgStore.read_header(path_str)
            tgstore.TgStore.save_stream(
                header, new_contents, path_str, chunk_size)

    @classmethod
    def update_header(
            cls, content_id: int,
            path_template: str, new_header, chunk_size: int=1024 ** 2): 
        """
update header in working directory.

Parameters
__________

path_template : str

content_id : int

new_header: dict

"""
        path_str = path_template.format(id=content_id) 
        with open(path_str, "r+") as fp:
            flock.acquire_lock(fp)
            tgstore.TgStore.save_header(
                new_header, path_str, chunk_size)

    @classmethod
    def exists(
        cls,
        content_id: int, path_template: str):
        """
check whether id's path exists as file

Parameters
----------
content_id: int

Returns
-------
True if id's path exists

"""
        path_str = path_template.format(id = content_id) 
        return Path(path_str).is_file()
    @classmethod
    def list_id(
            cls,
            dir: str | Path,
            match_str: str,
            group_index: int):
        """
list content files.

Parameters
__________

dir: str

match_str: str

group_index: int

Returns
_______

list
    file name list
"""
        regex = re.compile(match_str)
        for entry in os.scandir(dir):
            if entry.is_file(follow_symlinks=False):
                fn = os.fsdecode(entry.name)
                match = regex.match(fn) 
                if match is not None:
                    try:
                        str_id = match.group(group_index)
                        yield int(str_id)
                    except IndexError:
                        pass

    @classmethod
    def create_content_for_editing(
            cls,
            id_management_path: str | Path,
            path_template: str):
        """
create new empty content in working directory.

Parameters
__________

id_management_path: str

path_template : str

content_id : int

Returns
_______

int
    content id
"""
        content_id = flidgen.Idgen.get_id(id_management_path)
        if content_id is not None:
            path_str = path_template.format(id=content_id)
            try:
                with io.BytesIO() as src_strm:
                    tgstore.TgStore.save_stream({}, src_strm, path_str)
            except Exception:
                content_id = None
        return content_id

    @classmethod
    def commit_content_editting(
            cls, 
            content_id: int,
            track_data_dir : str | Path,
            src_path_template : str, 
            dst_path_template : str,
            delete_src,
            author_name: str,
            author_email: str,
            chunk_size: int=1024 ** 2):
        """
commit content in working directory into release directory.


Parameters
__________

track_data_dir : str

src_path_template : str

dst_path_template : str

content_id : int

delete_src : boolean

author_name : str

author_email : str

chunk_size : temporary buffer size as bytes for copying. default size are 1024 ** 2

"""
        dst_path = Path(dst_path_template.format(id=content_id))
        src_path = Path(src_path_template.format(id=content_id))
       
        with open(src_path, "r+") as src_fp:
            flock.acquire_lock(src_fp)
            with open(dst_path, "a") as dst_fp:
                flock.acquire_lock(dst_fp)
                cls.copy_content(
                    content_id,
                    src_path_template,
                    dst_path_template,
                    chunk_size)
                flock.release_lock(src_fp)
                oid = fltdt.write_path_to_object(
                    track_data_dir, 'blob', dst_path, chunk_size) 
                with open(
                        fltdt.get_index_path(track_data_dir),
                        "a") as idx_fp:
                    flock.acquire_lock(idx_fp)
                    with open(
                            fltdt.get_head_path(track_data_dir),
                            "a") as head_fp:
                        flock.acquire_lock(head_fp)
                        fltdt.update_index_add(
                                track_data_dir,
                                dst_path, dst_path.name, oid)
                        flock.release_lock(dst_fp)
                        tree_oid = fltdt.write_tree(track_data_dir)
                        current_tree_oid = \
                                fltdt.get_commit_tree_oid(
                                    track_data_dir, None,
                                    chunk_size)
                        if tree_oid != current_tree_oid:
                            new_commit_oid = fltdt.create_commit(
                                    track_data_dir, tree_oid, 
                                    fltdt.read_oid_from_head(
                                        track_data_dir),
                                    author_name, author_email)
                            fltdt.update_head(
                                    track_data_dir, new_commit_oid)

        if delete_src:
           os.remove(src_path)

    @classmethod
    def iterate_tree_items(
            cls,
            data_dir: str | Path,
            tree_id: str,
            chunk_size: int=1024 ** 2):
        """ list tree items"""
        tree = fltdt.read_tree(data_dir, tree_id)     
        if tree is not None:
            return fltdt.iterate_tree_body(tree) 
        else:
            return None

    @classmethod
    def iterate_commit(
            cls, data_dir: str | Path, chunk_size: int=1024 ** 2):
        """ iterate commit history """
        return fltdt.iterate_commit(data_dir, chunk_size)

    @classmethod
    def get_content_from_oid(
            cls, data_dir: str | Path, oid: str, 
            strm,
            chunk_size: int=1024 ** 2):

        result = None
        with tempfile.NamedTemporaryFile() as tmp_strm:
            obj_type = fltdt.read_object_into_strm(
                data_dir, oid, tmp_strm, chunk_size) 
            tmp_strm.flush()
            if obj_type == "blob":
                result = tgstore.TgStore.read(tmp_strm.name, strm, chunk_size)
        return result
    @classmethod
    def get_header_from_oid(
            cls, data_dir: str | Path, oid: str, 
            chunk_size: int=1024 ** 2):

        result = None
        with tempfile.NamedTemporaryFile() as tmp_strm:
            obj_type = fltdt.read_object_into_strm(
                data_dir, oid, tmp_strm, chunk_size) 
            tmp_strm.flush()
            if obj_type == "blob":
                result = tgstore.TgStore.read_header(tmp_strm.name)
        return result


    @classmethod
    def cancel_content_editing(
            cls, content_id: int, path_template: str):
        """
remove content from working directory without commit.

Parameters
__________

path_template : str

content_id: int content id
"""
        path_str = path_template.format(id=content_id)
        os.remove(path_str)
    @classmethod
    def copy_content(
            cls,
            content_id: int,
            src_path_template: str,
            dst_path_template: str,
            chunk_size: int=1024 ** 2):
        """
copy content

Parameters
__________

src_path_template : str

dst_path_template : str

contentid : int

chunk_size : temporary buffer size as bytes for copying. default size are 1024 ** 2

"""
        copied_size = 0
        if src_path_template != dst_path_template:
            src_path_str = src_path_template.format(id=content_id)
            dst_path_str = dst_path_template.format(id=content_id)
            with open(src_path_str, "rb+") as src_strm:
                flock.acquire_lock(src_strm)
                with open(dst_path_str, "wb") as dst_strm:
                    flock.acquire_lock(dst_strm)
                    copied_size = cls.copy_stream(
                        src_strm, dst_strm, chunk_size)
                    flock.release_lock(dst_strm)
                flock.release_lock(src_strm)
        return copied_size

    @classmethod
    def is_content_exists(
            cls,
            content_id: int,
            path_template: str):
        """
check whether specified id content exists

Parameters
__________

content_id: content id

path_template: path template

Returns

True if specified id content exists.

"""
        path_str = path_template.format(id=content_id)
        return Path.is_file(path_str) 

    @classmethod
    def copy_stream(cls, src_strm, dst_strm, chunk_size: int=1024 ** 2):
        """
copy stream

Parameters
__________

src_strm : source stream 

dst_strm : destination stream

chunk_size : temporary buffer size as bytes for copying. default size are 1024 ** 2
"""
        chunk = bytearray(chunk_size)
        total_size = 0
        while True:
            read_size = src_strm.readinto(chunk)
            if read_size == 0:
                break
            if read_size < len(chunk):
                chunk = chunk[:read_size]
            dst_strm.write(chunk)
            total_size += read_size
        return total_size

                   
    @classmethod
    def init_file_system(
        cls,
        edit_path_template: str | Path,
        release_path_template: str | Path):
        """
initialize dtrack store.
it create commit and edit path template directories.

Parameters
__________

edit_path_template: str

release_path_template: str
"""
        if isinstance(edit_path_template, Path):
            edit_path = edit_path_template
        else:
            edit_path = Path(edit_path_template)
        if isinstance(release_path_template, Path):
            release_path = release_path_template
        else:
            release_path = Path(release_path_template)
        edit_path.parent.mkdir(parents=True, exist_ok=True)
        release_path.parent.mkdir(parents=True, exist_ok=True)
 
# vi: se ts=4 sw=4 et:
