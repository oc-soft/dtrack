
import os
import pathlib
import argparse

import flidgen

class FlidT:

    def __init__(self):
        pass


    @property
    def idfile_path(self):
        return pathlib.Path(self._idfile_path)

    @property
    def test_count(self):
        return self._test_count

    def set_option(self, option):
        self._idfile_path = option.idfile
        self._test_count = option.test_count
        pass

    def setup_flidgen(self):
        self.idfile_path.parent.mkdir(parents=True, exist_ok=True)

    def run(self):
        self.setup_flidgen()
        res = []
        for _ in range(self.test_count):
            res.append(flidgen.Idgen.get_id(self.idfile_path))
        print(' '.join([str(x) for x in res])) 


if __name__ == "__main__":
    argp = argparse.ArgumentParser()
    argp.add_argument('--idfile', type=str, required=True)
    argp.add_argument('--test-count', type=int, default=10)
    args = argp.parse_args()
    flidt = FlidT()
    flidt.set_option(args)
    flidt.run()

# vi: se ts=4 sw=4 et:
