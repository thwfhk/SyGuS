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
    # print('\n*********************** recGenVSA', 'expected-value:', ev)
    # oldvsa.print()

    if ev == None:
      newname = oldvsa.name
      if newname in self.vsa.mem:
        return self.vsa.mem[newname]
      self.vsa.mem.update(oldvsa.vsa.mem)
      # NOTE: 直接全部update进来，省去一些讨论。要注意vsant的vsa指向没改，但应该不要紧。
      return self.vsa.mem[newname]

    newname = Name(oldvsa.name.ntname, (ev,))
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
      # handle each different witness result
      for subevs, num in zip(subevsList, range(len(subevsList))):
        subname = Name(oldvsa.name.ntname + str(num), (ev,))
        subvsa = VSANT(subname, 'F', (funcName, []), self.vsa)
        assert not (subname in self.vsa.mem) # 应该不在里面
        self.vsa.mem[subname] = subvsa
        for nterm, subev in zip(oldvsa.prods[1], subevs):
          newNterm = self.recGenVSA(oldvsa.vsa.mem[nterm], subev)
          if newNterm.kind == 'E':
            subvsa.kind = 'E'
            break
          subvsa.prods[1].append(newNterm.name)
        if subvsa.kind != 'E':
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
    # print(example.term2val.values())
    li = list(example.term2val.values())
    res = []
    for x in li:
      for y in li:
        # if (x <= y) == expectedValue:
        if (x <= y) == expectedValue:
          res.append((x, y))
    # print('res:', res)
    return res
  return None

# None只可能出现在ite中，此时这里是什么值都可以。最后输出程序的话，任意输出一个（比如'x')即可。
# 在intersection的时候，直接把另一个的取过来。也要把另一个用到的递归拿过来。
# NOTE: 可以加一些ad-hoc的优化，比如if去掉一般，比如<=时去掉=