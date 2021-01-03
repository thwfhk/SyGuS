from __future__ import print_function
from select import select
from subprocess import Popen, PIPE
import sys

processes = [Popen(['./SyGuS-solver-exe', sys.argv[1]], stdout=PIPE,
                   bufsize=1, close_fds=True,
                   universal_newlines=True),
             Popen(['python3', 'src/final.py', sys.argv[1]], stdout=PIPE,
                   bufsize=1, close_fds=True,
                   universal_newlines=True)]

timeout = 0.1
finish = False
while not finish:
    for p in processes[:]:
        if p.poll() is not None:
            print(p.stdout.read(), end='')
            p.stdout.close()
            finish = True
    if finish:
        for p in processes[:]:
            p.kill()
    else:
        select([p.stdout for p in processes], [],[], timeout)[0]
