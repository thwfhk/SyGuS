def printlist(li, str=""):
  if str != "":
    print(str)
  for x in li:
    print(x)
  print("")

# functional programming
def Id(x):
  return x

def fork(f, g):
  return lambda x : (f(x), g(x))

def unzip(li):
  return zip(*li)