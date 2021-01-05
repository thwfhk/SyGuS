from __future__ import print_function
from select import select
from subprocess import Popen, PIPE
import sys
import time

processes = [Popen(['./SyGuS-solver-mac', sys.argv[1]], stdout=PIPE,
           bufsize=1, close_fds=True,
           universal_newlines=True),
       Popen(['python3', 'src/final.py', sys.argv[1]], stdout=PIPE,
           bufsize=1, close_fds=True,
           universal_newlines=True)]

timeout = 0.1
finish = False
while not finish:
  for p in processes:
    if p.poll() is not None:
      res = p.stdout.read()
      p.kill()
      processes.remove(p)
      if res == 'No answer.\n':
        continue
      print(res, end='')
      finish = True
  if finish:
    for p in processes[:]:
      p.kill()
  else:
    select([p.stdout for p in processes], [],[], timeout)[0]
    # time.sleep(0.5)
