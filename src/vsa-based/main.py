import sys
import sexp
import pprint
from checker import *
from vsa import *
from utils import *
from getproductions import *

def stripComments(bmFile):
  noComments = '('
  for line in bmFile:
    line = line.split(';', 1)[0]
    noComments += line
  return noComments + ')'

def readQuery(bmExpr):
  SynFunExpr=[]
  VarDecMap={}
  Constraints=[]
  FunDefMap={}
  for expr in bmExpr:
    if len(expr)==0:
      continue
    elif expr[0]=='synth-fun':
      SynFunExpr=expr
    elif expr[0]=='declare-var':
      VarDecMap[expr[1]]=expr
    elif expr[0]=='constraint':
      Constraints.append(expr)
    elif expr[0]=='define-fun':
      FunDefMap[expr[1]]=expr
  
  VarTable={}
  # Declare Var
  for var in VarDecMap:
    VarTable[var] = DeclareVar(VarDecMap[var][2], var)

  # Declare Target Function
  synFunction=SynFunction(SynFunExpr)

  checker = Checker(VarTable, synFunction, Constraints)
  return checker

def readSygus(filename):
  bm = stripComments(open(filename))
  # Parse string to python list
  bmExpr = sexp.sexp.parseString(bm, parseAll=True).asList()[0] 
  # print("begin-------------------------------------")
  # pprint.pprint(bmExpr)
  # print("end-------------------------------------")

  checker = readQuery(bmExpr)

  SynFunExpr = []
  for expr in bmExpr:
    if len(expr) == 0:
      continue
    elif expr[0] == 'synth-fun':
      SynFunExpr = expr
  # print("Function to Synthesize: ")
  # pprint.pprint(SyFunExpr)
  FuncDefine = ['define-fun'] + SynFunExpr[1:4] #copy function signature
  FuncDefineStr = toString(FuncDefine, ForceBracket = True)
  # use Force Bracket = True on function definition. MAGIC CODE.
  StartSym = 'My-Start-Symbol' #virtual starting symbol
  Productions = {StartSym : []}
  Type = {StartSym : SynFunExpr[3]} # set starting symbol's return type

  # generate productions
  for NonTerm in SynFunExpr[4]: # SynFunExpr[4] is the production rules
    NTName = NonTerm[0]
    NTType = NonTerm[1]
    if NTType == Type[StartSym]:
      Productions[StartSym].append(NTName) # 'My-Start-Symbol' : 'Start'
    Type[NTName] = NTType
    Productions[NTName] = []
    if "max" in SynFunExpr[1]:
      getProductionsMax(Productions[NTName], NonTerm[2])
    else:
      for NT in NonTerm[2]:
        if type(NT) == tuple:
          Productions[NTName].append(str(NT[1]))
          # deal with ('Int',0). 
        else:
          Productions[NTName].append(NT)
  # print("Productions:")
  # for symbol, rule in Productions.items():
  #   print(symbol, ' -> ', rule)
  # print("")
  return checker, StartSym, Productions, FuncDefineStr

def countNtermNum(vsa):
  cnt = 0
  single = 0
  for x in vsa.mem.values():
    if x.kind != 'E':
      cnt += 1
    if x.kind == 'U' and len(x.prods) == 1:
      single += 1
  return cnt, single

def debugTest(verbose = False):
  checker, StartSym, Productions, FuncDefineStr = readSygus(sys.argv[1])
  initialVSA = VSA()
  initialVSA.CFG2VSA(Productions, StartSym)
  print('VSA size:', countNtermNum(initialVSA))
  initialVSA.print()
  program0 = initialVSA.generateProgram()
  print(program0)
  # return None

  print('VSA1')
  example = checker.generateSingleExample([0,1,2])
  example.print()
  VSA1 = example.generateVSA(initialVSA)
  print('VSA size:', countNtermNum(VSA1))
  if verbose:
    VSA1.print()
  program1 = VSA1.generateProgram()
  print(program1)

  print('VSA2')
  example = checker.generateSingleExample([2,0,1])
  example.print()
  VSA2 = example.generateVSA(initialVSA)
  print('VSA size:', countNtermNum(VSA2))
  if verbose:
    VSA2.print()
  program2 = VSA2.generateProgram()
  print(program2)

  print('VSA3')
  example = checker.generateSingleExample([1,2,0])
  example.print()
  VSA3 = example.generateVSA(initialVSA)
  # VSA3.print()
  program3 = VSA3.generateProgram()
  print(program3)

  print('VSA FINAL')
  VSAfinal = VSAIntersect(VSA1, VSA2)
  print('VSA size:', countNtermNum(VSAfinal))
  if verbose:
    VSAfinal.print()
  program12 = VSAfinal.generateProgram()
  # tmp = VSAfinal.generateProgramBFS()
  print(program12)
  # print(tmp)

  VSAfinal = VSAIntersect(VSAfinal, VSA3)
  # VSAfinal.print()
  program = VSAfinal.generateProgram()
  print(program)

def CEGIS(curVSA, checker, FuncDefineStr, initialVSA):
  while True:
    print('curVSA size:', countNtermNum(curVSA))
    program = curVSA.generateProgram()
    funcStr = FuncDefineStr[:-1] + ' ' + program + FuncDefineStr[-1]
    print(funcStr)
    res, example = checker.check(funcStr)
    if res:
      return funcStr
    elif example:
      tmpVSA = example.generateVSA(initialVSA)
      curVSA = VSAIntersect(curVSA, tmpVSA)
  return None

def main():
  # print (sys.getrecursionlimit())
  sys.setrecursionlimit(1000)
  checker, StartSym, Productions, FuncDefineStr = readSygus(sys.argv[1])
  initialVSA = VSA()
  initialVSA.CFG2VSA(Productions, StartSym)
  # initialVSA.print()
  curVSA = None
  for example in checker.examples:
    example.print()
    tmpVSA = example.generateVSA(initialVSA)
    if curVSA == None:
      curVSA = tmpVSA
    else:
      curVSA = VSAIntersect(curVSA, tmpVSA)
  CEGIS(curVSA, checker, FuncDefineStr, initialVSA)

if __name__ == '__main__':
  debugTest()
  # main()