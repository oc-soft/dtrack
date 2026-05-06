
import os
import fltdt 


if __name__ == "__main__":
    fltdt_dir = os.getenv('FLTDT_DATA_DIR')  
    for commit in fltdt.iterate_commit(fltdt_dir):
        print(repr(commit))


# vi: se ts=4 sw=4 et:
