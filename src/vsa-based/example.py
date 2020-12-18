from z3 import *
from vsa import *

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
    self.vsa = None      # type: VSA
    self.term2val = {} # type: Dict[str, value]
    self.output = None # type: value
    self.subs = []     # type: List[(z3symbol, z3val)]

  def print(self):
    print("----------[Example]----------")
    if self.vsa:
      self.vsa.print()
    print("term2val:", self.term2val)
    print("output:", self.output)
    print("subs:", self.subs)
    # print(type(self.subs[0][0]), type(self.subs[0][1]))
    print("----------[End]----------")

  # generate VSA from example and initialVSA
  def generateVSA(self, oldVSA: VSA) -> VSA:
    self.vsa = VSA()
    self.vsa.startSym =\
      self.recGenVSA(oldVSA.mem[oldVSA.startSym], self.output).name
    return self.vsa

  def recGenVSA(self, oldvsa: VSANT, ev) -> VSANT:
    print('\n*********************** recGenVSA', 'expected-value:', ev)
    oldvsa.print()

    if ev == None:
      newname = oldvsa.name
      if newname in self.vsa.mem:
        return self.vsa.mem[newname]
      newvsa = VSANT(newname, oldvsa.kind, deepcopy(oldvsa.prods), self.vsa)
      self.vsa.mem[newname] = newvsa
      return newvsa

    newname = Name(oldvsa.name.ntname, (ev))
    if newname in self.vsa.mem:
      return self.vsa.mem[newname]
    newvsa = VSANT(newname, oldvsa.kind, None, self.vsa)
    self.vsa.mem[newname] = newvsa

    if oldvsa.kind == 'P':
      newvsa.prods = set()
      for terminal in oldvsa.prods:
        if self.term2val[terminal] == ev:
          newvsa.prods.add(terminal)
      if len(newvsa.prods) == 0:
        newvsa.kind = 'E'
    elif oldvsa.kind == 'U':
      newvsa.prods = []
      for nterm in oldvsa.prods:
        newNterm = self.recGenVSA(oldvsa.vsa.mem[nterm], ev)
        if newNterm.kind != 'E':
          newvsa.prods.append(newNterm.name)
      if len(newvsa.prods) == 0:
        newvsa.kind = 'E'
    else: # oldvsa.kind == 'F'
      newvsa.kind = 'U'
      newvsa.prods = []
      funcName = oldvsa.prods[0]
      subevsList = witness(funcName, ev, self)
      for subevs, num in zip(subevsList, range(len(subevsList))):
        subname = Name(oldvsa.name.ntname + str(num), (ev))
        subvsa = VSANT(subname, 'F', (funcName, []), self.vsa)
        if subname in self.vsa.mem:
          subvsa = self.vsa.mem[subname]
        else:
          self.vsa.mem[subname] = subvsa
          for nterm, subev in zip(oldvsa.prods[1], subevs):
            newNterm = self.recGenVSA(oldvsa.vsa.mem[nterm], subev)
            subvsa.prods[1].append(newNterm.name)
        newvsa.prods.append(subvsa.name)
    # newvsa.print()
    return newvsa

def model2Example(model, checker):
  example = Example()
  for var in model.decls():
    example.term2val[str(var)] = model[var].as_long()
    example.subs.append((Int(str(var)), model[var]))
  example.output = checker.getResult(example.subs)
  return example


# 返回多组可能的赋值
def witness(funcName, expectedValue, example):
  if funcName == 'ite':
    return [(True, expectedValue, None), (False, None, expectedValue)]
  if funcName == '<=':
    # 分配可能性太多了。优化：只使用terminal的取值
    print(example.term2val.values())
    li = list(example.term2val.values())
    x, y = li
    if x <= y:
      if expectedValue:
        return [(x,y)]
      else:
        return [(y,x)]
    else:
      if expectedValue:
        return [(y,x)]
      else:
        return [(x,y)]
  return None