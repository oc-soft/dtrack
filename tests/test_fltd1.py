import unittest
import fltdt
import os
import io

class TestFltd(unittest.TestCase):

    @classmethod
    def get_dtrace_dir(cls):
        test_dir = os.getenv('TEST_DATA_DIR')
        return os.path.join(test_dir, 'dtrace')

    def test_hash_object(self):
        test_dir = os.getenv('TEST_DATA_DIR')

        data_path = os.path.join(test_dir, 'hello.txt')
        hash_val = fltdt.write_path_to_object(
            self.get_dtrace_dir(), 'blob', data_path)
        self.assertIsInstance(hash_val, str)

        mem_strm = io.BytesIO()
        obj_type = fltdt.read_object_into_strm(
                self.get_dtrace_dir(), hash_val, mem_strm)
        
        self.assertEqual(mem_strm.getvalue().decode(), 'Hello world\n') 

# vi: se ts=4 sw=4 et:
