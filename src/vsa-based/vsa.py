from collections import namedtuple
from copy import deepcopy
from random import randint

# Term = 'x' | '0' | 'nt-name' | ['func-name', 'nt-name1', 'nt-name2', ...]

Name = namedtuple('Name', 'ntname ev')
class VSA:
  def __init__(self):
    self.mem = {}
    self.startSym = None

  def print(self):
    print("********************************VSA********************************")
    print("StartSym:", self.startSym)
    for name, vsant in self.mem.items():
      print('')
      vsant.print()
    print("********************************end********************************")

  def CFG2VSA(self, Productions, StartSym):
    # print(StartSym, '\n', Productions)
    self.startSym = self.recurseCFG2VSA(Productions, StartSym)

  # return the name of VSANT
  def recurseCFG2VSA(self, Productions, curSym):
    # print("[recurseCFG2VSA]", curSym)
    curvsa = VSANT(Name(curSym, ()), 'U', [], self)
    if curvsa.name in self.mem:
      return curvsa.name
    self.mem[curvsa.name] = curvsa

    prods = Productions[curSym]
    # print("-----------------------prods:", prods)
    terminals = set()
    # first handle terminals
    for prod in prods:
      if type(prod) == str and not (prod in Productions): # prod is a terminal
        terminals.add(prod)
    if len(terminals) != 0: # we have terminals
      newvsa = VSANT(Name(curSym + 'P', ()), 'P', terminals, self)
      if newvsa.name in self.mem:
        newvsa = self.mem[newvsa.name]
      else:
        self.mem[newvsa.name] = newvsa
      curvsa.prods.append(newvsa.name)

    for prod in prods:
      # print("-----------------------prod:", prod)
      if type(prod) == str and prod in Productions: # prod is a non-terminal
        newname = self.recurseCFG2VSA(Productions, prod)
        curvsa.prods.append(newname)
      elif type(prod) == str: # prod is a terminal
        continue
      else: # prod is a function-application
        funcName = prod[0]
        newvsa = VSANT(Name(curSym + funcName, ()), 'F',
                        (funcName, []), self)
        if newvsa.name in self.mem:
          newvsa = self.mem[newvsa.name]
        else:
          self.mem[newvsa.name] = newvsa
          for subprod in prod[1:]:
            subnewname = self.recurseCFG2VSA(Productions, subprod)
            newvsa.prods[1].append(subnewname)
        curvsa.prods.append(newvsa.name)

    return curvsa.name
  
  # remove epsilon productions
  # 也许在生成的时候已经都去掉了？
  def removeEmpty(self):
    pass

  # generate any program from vsant
  # select terminals first
  def generateProgram(self):
    queue = [self.mem[self.startSym]]
    while queue != []:
      vsant = queue.pop(0)

  # NOTE: dfs may never terminate?

  def dfsProgram(self, vsant):
    print("dfsProgram")
    vsant.print()
    if vsant.kind == 'E':
      Exception('empty kind vsant')
    if vsant.kind == 'P':
      return list(vsant.prods)[0]
    if vsant.kind == 'F':
      res = '(' + vsant.prods[0]
      for subnt in vsant.prods[1]:
        res += ' ' + self.dfsProgram(self.mem[subnt])
      res += ')'
      return res
    if vsant.kind == 'U':
      # NOTE: just choose the first
      n = randint(0, len(vsant.prods)-1)
      return self.dfsProgram(self.mem[vsant.prods[n]])
      # return self.dfsProgram(self.mem[vsant.prods[0]])
    Exception('invalid kind', vsant.kind)


# VSA non-terminal
# name : (str, [val]) ; nt-name and expected-values
# kind : 'P' | 'U' | 'F' | 'E'
# prods : {str} | [name] | None
# exam : information of the example
# VSANT = namedtuple('VSANT', 'name kind prods exam')
class VSANT:
  def __init__(self, name, kind, prods, vsa):
    self.name = name
    self.kind = kind
    self.prods = prods
    self.vsa = vsa

  def print(self):
    print("---------------------------------------------")
    print("VSANT:", self.name)
    print(self.kind, self.prods)
    # print(self.vsa)
    print("---------------------------------------------")

# Name = namedtuple('Name', 'ntname spec')
# memory : {name : VSANT} ; Map VSANT-names to VSANTs.
# term2val : {str : val} ; Map terminal-names to values.

# def VSAIntersect(nt1: VSANT, nt2: VSANT, vsa: VSA) -> VSANT:
#   # if nt1.name[0] != nt2.name[0]:
#     # return VSANT('', 'E', None, exam)
#   resname = ('(' + nt1.name[0] + ')*(' + nt2.name[0] + ')',\
#               nt1.name[1] + nt2.name[1])

#   if resname in exam.mem:
#     return exam.mem[resname]

#   if nt2.kind == 'U':
#     nt1, nt2 = nt2, nt1
#   if nt1.kind == 'U':
#     res = VSANT(resname, 'U', [], exam)
#     for name in nt1.prods:
#       nt = nt1.exam.mem[name]
#       res.prods.append(VSAIntersect(nt, nt2, exam).name)
#     exam.mem[res.name] = res
#     return res

#   if nt1.kind == 'F' and nt2.kind == 'F':
#     if nt1.prods[0] != nt2.prods[0]:
#       res = VSANT(resname, 'E', (), exam)
#       return res
#     res = VSANT(resname, 'F', (nt1.prods[0], []), exam)
#     for nt1name, nt2name in zip(nt1.prods[1], nt2.prods[1]):
#       tmp1 = nt1.exam.mem[nt1name]
#       tmp2 = nt2.exam.mem[nt2name]
#       res.prods[1].append(VSAIntersect(tmp1, tmp2, exam).name)
#     return res

#   if nt2.kind == 'P':
#     nt1, nt2 = nt2, nt1
#   if nt1.kind == 'P' and nt2.kind == 'F':
#     res = VSANT(resname, 'P', set(), exam)
#     for terminal in nt1.prods:
#       value = nt1.exam.term2val[terminal]
#       if value in nt2.name[1]: # nt2已经是带着expected-value的，只要检查value是否在那里面
#         res.prods.add(terminal)
#     return res
#   else: # both are 'P'
#     res = VSANT(resname, 'P', set(), exam)
#     res.prods = nt1.prods & nt2.prods
#     return res
