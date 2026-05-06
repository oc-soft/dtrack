import fcntl


def acquire_lock(fd): 
    """ simple fctl lock wrapper. """
    fcntl.lockf(fd, fcntl.LOCK_EX)

def release_lock(fd):
    fcntl.lockf(fd, fcntl.LOCK_UN)
    

# vi: se ts=4 sw=4 et:
