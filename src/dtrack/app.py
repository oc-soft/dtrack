from pathlib import Path
import tomllib
import os

from .dtrack import Dtrack

class App:
    """ dtrack application """

    def __init__(self): 
        """ constructor """
        pass

    def load_from_env(self):
        """ load from enviroment """
        config = os.getenv('DTRACK_CONFIG') 
        if config is not None:
            self.load_config(config)     
        pass
    
    def load_config(self, config_path: str | Path):
        """ load configuration from file path """
        config = None
        with open(config_path, "rb") as fp:
            config = tomllib.load(fp)
            self._data_tracking_dir = config['tracking-dir']
            self._release_template_path = config['release-template-path']
            self._edit_template_path = config['edit-template-path']
            self._id_management_path = config['id-management-path']
            self._stream_chunk_size = config['stream-chunk-size']

    @property
    def data_tracking_dir(self):
        """ data tracking directory """
        return self._data_tracking_dir

    @property
    def release_template_path(self):
        """ release template path """
        return self._release_template_path

    @property
    def edit_template_path(self):
        """ edit template path """
        return self._edit_template_path

    @property
    def id_management_path(self):
        """ id management path """
        return self._id_management_path

    @property
    def stream_chunk_size(self):
        """ stream chunk size """
        return self._stream_chunk_size

    def get_content(self, id: int, dst_strm):
        """ get content """
        Dtrack.get_content(
                id, self.release_template_path, dst_strm,
                self.stream_chunk_size) 

    def get_header(self, id: int):
        """ get header """
        return Dtrack.get_header(id, self.release_template_path) 
 

    def get_content_editing(self, id: int, dst_strm):
        """ get editing content """
        Dtrack.get_content(
                id, self.edit_template_path, dst_strm,
                self.stream_chunk_size) 
    def get_header_editing(self, id: int):
        """ get editing header """
        return Dtrack.get_header(id, self.edit_template_path) 
 
    def update_content(self, id: int, new_content_strm):
        """ update content during editing. """
        return Dtrack.update_content(
                id, self.edit_template_path,
                new_content_strm, self.stream_chunk_size)

    def update_header(self, id: int, new_header):
        """ update content during editing. """
        return Dtrack.update_header(
                id, self.edit_template_path,
                new_header, self.stream_chunk_size)

    def create_content_for_editing(self):
        """ create new empty content in editing directory """
        content_id = Dtrack.create_content_for_editing(
            self.id_management_path, self.edit_template_path)
        return content_id

    def create_edit_content_from_id(self, content_id: int):
        """ copy release content to edit content """
        Dtrack.copy_content(content_id,
            self.release_template_path,
            self.edit_template_path,
            self.stream_chunk_size)

    def iterate_tree_items(self, tree_id: str):
        """ iterate tree items"""
        return Dtrack.iterate_tree_items(self.data_tracking_dir, tree_id)

    def iterate_commit_tree(self):
        """ iterate content id """
        for commit in Dtrack.iterate_commit(self.data_tracking_dir):
            yield commit['tree']

    def iterate_commit(self):
        """ iterate commit history """
        return Dtrack.iterate_commit(
                self.data_tracking_dir,
                self.stream_chunk_size)
    def get_content_from_oid(self, oid, strm):
        """ get content from oid """
        return Dtrack.get_content_from_oid(
                self.data_tracking_dir,
                oid, strm,
                self.stream_chunk_size)

    def get_header_from_oid(self, oid):
        """ get content header from oid """
        return Dtrack.get_header_from_oid(
                self.data_tracking_dir,
                oid, self.stream_chunk_size)

    def iterate_history_of_id(self, content_id: int):
        """ iterate edit history of content id """
        content_path = self.release_template_path.format(id=content_id)
        content_name = Path(content_path).name
        last_oid = None
        for tree_id in self.iterate_commit_tree():
            for tree_item in self.iterate_tree_items(tree_id):
                if tree_item["name"] == content_name:
                    if last_oid != tree_item["oid"]:
                        yield tree_item["oid"]
                        last_oid = tree_item["oid"]

    def commit(
            self, content_id: int,
            delete_editing_src: True | False,
            author_name: str, author_email: str):
        """ commit editing content and release """
        Dtrack.commit_content_editting(
            content_id,
            self.data_tracking_dir,
            self.edit_template_path,
            self.release_template_path,
            delete_editing_src,
            author_name,
            author_email,
            self.stream_chunk_size)

    def init_system(self):
        """ initialize dtrack system """
        id_mng_path = Path(self.id_management_path)
        id_mng_path.parent.mkdir(parents=True, exist_ok=True) 
        Dtrack.init_file_system(
                self.edit_template_path,
                self.release_template_path)

# vi: se ts=4 sw=4 et:
