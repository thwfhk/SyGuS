from __future__ import print_function
from select import select
from subprocess import Popen, PIPE, TimeoutExpired
import sys
import time

processes = [
  Popen(['./SyGuS-solver-mac', sys.argv[1]], stdout=PIPE,
    bufsize=1, close_fds=True,
    universal_newlines=True),
  Popen(['python3', 'src/direct/directwrapper.py', sys.argv[1]], stdout=PIPE,
    bufsize=1, close_fds=True,
    universal_newlines=True)
]

finish = False
out = None
while not finish:
  for p in processes:
    try:
      out, err = p.communicate(timeout = 1)
    except TimeoutExpired:
      continue
    if not out == "":
      finish = True
      break
    else:
      processes.remove(p)
print(out, end="")
for p in processes:
  p.kill()