import subprocess
import sys

import pdb

class ForkedPdb(pdb.Pdb):
    '''
    A Pdb subclass that may be used
    from a forked multiprocessing child
    https://stackoverflow.com/questions/4716533/how-to-attach-debugger-to-a-python-subproccess
    '''
    def interaction(self, *args, **kwargs):
        _stdin = sys.stdin
        try:
            sys.stdin = open('/dev/stdin')
            pdb.Pdb.interaction(self, *args, **kwargs)
        finally:
            sys.stdin = _stdin

        return

def decode(msg):
    if isinstance(msg, str):
        return msg
    elif isinstance(msg, bytes):
        return msg.decode('utf-8')
    elif msg is None:
        return ''
    else:
        print(f'Warning: message={msg} is not a string or bytes')
        return msg

def run_command(cmd, logprint=None, silent=False):

    if logprint is None:
        # Just remap to print then
        logprint = print

    args = [cmd.split()]
    kwargs = {
        'stdout':subprocess.PIPE,
        'stderr':subprocess.STDOUT,
        'bufsize':1
        }

    with subprocess.Popen(*args, **kwargs) as process:
        try:
            # for line in iter(process.stdout.readline, b''):
            for line in iter(process.stdout.readline, b''):
                if silent is False:
                    logprint(decode(line).replace('\n', ''))

            stdout, stderr = process.communicate()

        except:
            if silent is False:
                logprint('')
                logprint('.....................ERROR....................')
                logprint('')

                logprint('\n'+decode(stderr))

            rc = process.poll()
            raise subprocess.CalledProcessError(
                rc,
                process.args,
                output=stdout,
                stderr=stderr
                )

        rc = process.poll()


        if rc:
            stdout, stderr = process.communicate()
            if silent is False:
                logprint('\n'+decode(stderr))
            raise subprocess.CalledProcessError(
                rc,
                process.args,
                output=stdout,
                stderr=stderr
                )

    return rc

def setup_batches(nobjs, ncores):
    '''
    Create list of batch indices for each core
    '''

    if ncores >= 1:
        batch_len = [nobjs//ncores]*(ncores-1)
    else:
        raise ValueError('ncores must be >= 1')

    s = int(np.sum(batch_len))
    batch_len.append(nobjs-s)

    batch_indices = []

    start = 0
    for i in range(ncores):
        batch_indices.append(range(start, start + batch_len[i]))
        start += batch_len[i]

    return batch_indices
