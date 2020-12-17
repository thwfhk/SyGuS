from z3 import *

def DeclareVar(sort, name):
  if sort=='Int':
    return Int(name)
  if sort=='Bool':
    return Bool(name)
  raise Exception("Unknown sort")

def getSort(sort):
  if sort=="Int":
    return IntSort()
  if sort=="Bool":
    return BoolSort()
  raise Exception("Unknown sort")

class Example:
  def __init__(self):
    self.mem = {}      # type: Dict[str, VSANT]
    self.term2val = {} # type: Dict[str, value]
    self.output = None # type: value
    self.subs = []     # type: List[(z3symbol, z3val)]
  def print(self):
    print("----------[Example]----------")
    print("mem:", self.mem)
    print("term2val:", self.term2val)
    print("output:", self.output)
    print("subs:", self.subs)
    # print(type(self.subs[0][0]), type(self.subs[0][1]))
    print("----------[End]----------")

def model2Example(model, checker):
  example = Example()
  for var in model.decls():
    example.term2val[str(var)] = model[var].as_long()
    example.subs.append((Int(str(var)), model[var]))
  example.output = checker.getResult(example.subs)
  return example