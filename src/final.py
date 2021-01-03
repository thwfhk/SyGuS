import os
import sys
import time
import pprint
from copy import deepcopy
sys.path.append(os.path.join(os.getcwd(), os.path.join("src", "direct")))
from direct import sexp
from direct.checker import *
from direct.utils import *
from direct.spec2prog import *
from direct.specformatter import *
from rosette.rosette_driver import Run

CandyQwQ = False

def stripComments(bmFile):
  noComments = '('
  for line in bmFile:
    line = line.split(';', 1)[0]
    noComments += line
  return noComments + ')'

def readQuery(bmExpr):
  synFunExpr = None
  var2Decl = {}
  constraints = []
  for expr in bmExpr:
    if len(expr) == 0:
      continue
    elif expr[0] == 'synth-fun':
      synFunExpr = expr
    elif expr[0] == 'declare-var':
      var2Decl[expr[1]] = expr
    elif expr[0] == 'constraint':
      constraints.append(expr[1])
  
  varTable={}
  for var in var2Decl:
    varTable[var] = DeclareVar(var2Decl[var][2], var)

  # Declare Target Function
  synFunc = SynFunction(synFunExpr)

  checker = Checker(varTable, synFunc, constraints)
  return checker

def readSygus(filename):
  bm = stripComments(open(filename))
  # Parse string to python list
  bmExpr = sexp.sexp.parseString(bm, parseAll=True).asList()[0] 
  # print("begin-------------------------------------")
  # pprint.pprint(bmExpr)
  # print("end-------------------------------------")

  checker = readQuery(bmExpr)

  synFunExpr = checker.synFunc.synFunExpr
  funcDefine = ['define-fun'] + synFunExpr[1:4] #copy function signature
  funcDefineStr = toString(funcDefine, ForceBracket = True)

  # use Force Bracket = True on function definition. MAGIC CODE.
  StartSym = 'My-Start-Symbol' #virtual starting symbol
  productions = {StartSym : []}
  Type = {StartSym : synFunExpr[3]} # set starting symbol's return type

  # generate productions
  for nterm in synFunExpr[4]: # SynFunExpr[4] is the production rules
    ntName = nterm[0]
    ntType = nterm[1]
    if ntType == Type[StartSym]:
      productions[StartSym].append(ntName) # 'My-Start-Symbol' : 'Start'
    Type[ntName] = ntType
    productions[ntName] = []
    for subnt in nterm[2]:
      if type(subnt) == tuple:
        productions[ntName].append(str(subnt[1]))
        # deal with ('Int',0). 
      else:
        productions[ntName].append(subnt)
  return bmExpr, checker, StartSym, productions, funcDefineStr

def main():
  bmExpr, checker, StartSym, productions, funcDefineStr = readSygus(sys.argv[1])

  flag, progExpr = spec2prog(deepcopy(checker.constraints), checker.synFunc, productions)
  if not flag:
    # direct failed, try to use rosette
    if CandyQwQ:
      print('direct synthesis failed:', progExpr, '\nusing rosette:')
    # time.sleep(60)
    paraList = list(map(lambda x: x[0], checker.synFunc.argList))
    funcName = checker.synFunc.name
    newBmExpr = []
    for line in bmExpr:
      if line[0] != 'constraint':
        newBmExpr.append(line)
      else:
        newBmExpr.append(transConstArgs(line, funcName, paraList))
    # pprint.pprint(newBmExpr)
    progStr = Run(newBmExpr) + ')'
    print(progStr)
    if CandyQwQ:
      res, model = checker.check(progStr)
      print('checker result:', res)
  else:
    progStr = funcDefineStr[:-1] + ' ' + toString(progExpr) + funcDefineStr[-1]
    # print("----------------------------------------------------------------\nresult:");
    # pprint.pprint(progExpr)
    if CandyQwQ:
      print('direct synthesis sucess:')
    print(progStr)
    if CandyQwQ:
      res, model = checker.check(progStr)
      print('checker result:', res)

if __name__ == '__main__':
  main()