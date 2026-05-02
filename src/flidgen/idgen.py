

class Idgen:
    """ id generator """

    @classmethod
    def get_id(cls, id_path):
        result = None
        with open(id_path, "r+") as f:
            ln = f.readline()
            if not ln:
                result = int(ln)
                result += 1
            else:
                result = 1
            f.seek(0, os.SEEK_SET)

            f.writelines([str(result)]) 
        return result
        

# vi: se ts=4 sw=4 et:
