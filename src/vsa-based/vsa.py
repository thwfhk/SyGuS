from collections import namedtuple
from copy import deepcopy
from random import randint
from queue import PriorityQueue, Queue

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
  def generateProgramBFS(self):
    queue = PriorityQueue()
    # queue = Queue()
    start = Program([self.mem[self.startSym]], 1)
    queue.put(start)
    visit = set()
    visit.add(start)
    while not queue.empty():
      cur: Program = queue.get()
      # print(''.join(map(str, cur.prog)))
      finish = True
      for x in cur.prog:
        if type(x) != str:
          finish = False
      if finish: # and len(cur) > 1:
        # print(len(cur))
        return ''.join(cur.prog)

      hasPF = True
      while hasPF:
        hasPF = False
        for i, x in enumerate(cur.prog):
          if type(x) == str:
            continue
          elif x.kind == 'E':
            Exception('empty kind of vsant is not valid when generating programs')
          elif x.kind == 'P':
            cur.prog[i] = next(iter(x.prods))
            cur.vsantNum -= 1
          elif x.kind == 'F':
            new = Program([], 0)
            new.prog = ['(', x.prods[0]]
            for subntname in x.prods[1]:
              subnt = self.mem[subntname]
              new.prog += [' ', subnt]
              new.vsantNum += 1
              if subnt.kind in ('P', 'F'):
                hasPF = True
            new.prog += [')']
            cur.prog[i:i+1] = new.prog
            cur.vsantNum += new.vsantNum - 1
      hasU = False
      for i, x in enumerate(cur.prog):
        if type(x) != str and x.kind == 'U':
          hasU = True
          for nt in x.prods:
            new = cur.copy()
            new.prog[i] = self.mem[nt]
            if not new in visit:
              queue.put(new)
              visit.add(new)
      if not hasU:
        if not cur in visit:
          queue.put(cur)
          visit.add(cur)
    return "NO PROGRAM FOUNDED :("

  def generateProgram(self):
    programTable = {}
    # base:
    for nt in self.mem.values():
      if nt.kind == 'P':
        programTable[nt.name] = [next(iter(nt.prods))]
    # induction:
    updating = True
    while not self.startSym in programTable and updating:
      updating = False
      for nt in self.mem.values():
        if nt.kind == 'E':
          continue
        if not nt.name in programTable:
          if nt.kind == 'U':
            for subntName in nt.prods:
              if subntName in programTable:
                programTable[nt.name] = programTable[subntName]
                updating = True
                break
          elif nt.kind == 'F':
            prog = ['(', nt.prods[0]]
            flag = True
            for subntName in nt.prods[1]:
              if not subntName in programTable:
                flag = False
                break
              prog += [' '] + programTable[subntName]
            if flag:
              programTable[nt.name] = prog + [')']
              updating = True
    if self.startSym in programTable:
      return ''.join(programTable[self.startSym])
    else:
      return "NO PROGRAM FOUNDED :("


class Program:
  def __init__(self, prog, num):
    self.prog = prog
    self.vsantNum = num
  def __hash__(self):
    return hash(tuple(self.prog))
  def __gt__(self, other):
    return self.vsantNum > other.vsantNum
  def copy(self):
    return Program(self.prog.copy(), self.vsantNum)


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
  def __repr__(self):
    return 'VSANT(' + self.name.ntname + str(self.name.ev) + ')'
  def __hash__(self):
    return hash(self.name)
  def __gt__(self, oth):
    if type(oth) == str:
      return self.name.ntname > oth
    else:
      return self.name > oth.name
  def __lt__(self, oth):
    if type(oth) == str:
      return self.name.ntname < oth
    else:
      return self.name < oth.name
  def print(self):
    print("---------------------------------------------")
    print("VSANT:", self.name)
    print(self.kind, self.prods)
    # print(self.vsa)
    print("---------------------------------------------")

# Name = namedtuple('Name', 'ntname spec')
# memory : {name : VSANT} ; Map VSANT-names to VSANTs.
# term2val : {str : val} ; Map terminal-names to values.

def VSAIntersect(VSA1: VSA, VSA2: VSA) -> VSA:
  resVSA = VSA()
  resVSA.startSym =\
    vsantIntersect(VSA1.mem[VSA1.startSym], VSA2.mem[VSA2.startSym], resVSA).name
  return resVSA

def vsantIntersect(nt1: VSANT, nt2: VSANT, newVSA: VSA) -> VSANT:
  # if nt1.name[0] != nt2.name[0]:
    # return VSANT('', 'E', None, exam)
  resname = Name('(' + nt1.name[0] + ')*(' + nt2.name[0] + ')',\
              nt1.name[1] + nt2.name[1])

  if resname in newVSA.mem:
    return newVSA.mem[resname]
  res = VSANT(resname, '', None, newVSA)
  newVSA.mem[resname] = res

  if nt2.kind == 'U':
    nt1, nt2 = nt2, nt1
  if nt1.kind == 'U':
    res.kind = 'U'
    res.prods = []
    for name in nt1.prods:
      nt = nt1.vsa.mem[name]
      newnt = vsantIntersect(nt, nt2, newVSA)
      if newnt.kind != 'E':
        res.prods.append(newnt.name)
    if len(res.prods) == 0:
      res.kind = 'E'
    return res

  if nt1.kind == 'F' and nt2.kind == 'F':
    if nt1.prods[0] != nt2.prods[0]:
      res.kind = 'E'
      return res
    res.kind = 'F'
    res.prods = (nt1.prods[0], [])
    for nt1name, nt2name in zip(nt1.prods[1], nt2.prods[1]):
      tmp1 = nt1.vsa.mem[nt1name]
      tmp2 = nt2.vsa.mem[nt2name]
      newnt = vsantIntersect(tmp1, tmp2, newVSA)
      if newnt == 'E':
        res.kind = 'E'
        break
      res.prods[1].append(newnt.name)
    return res

  if nt2.kind == 'P':
    nt1, nt2 = nt2, nt1
  if nt1.kind == 'P' and nt2.kind == 'F':
    res.kind = 'E'
    return res
  else: # both are 'P'
    res.kind = 'P'
    if type(nt1.prods) != type(nt2.prods):
      print(nt1.kind, nt2.kind)
      print(nt1.prods, nt2.prods)
    res.prods = nt1.prods & nt2.prods
    if len(res.prods) == 0:
      res.kind = 'E'
    return res
