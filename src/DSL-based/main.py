import sys
import sexp
import pprint
from checker import *
from utils import *
from getproductions import *
from spec2prog import *

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
    # if "max" in SynFunExpr[1]:
      # getproductionsMax(productions[NTName], NonTerm[2])
    # else:
    for subnt in nterm[2]:
      if type(subnt) == tuple:
        productions[ntName].append(str(subnt[1]))
        # deal with ('Int',0). 
      else:
        productions[ntName].append(subnt)
  # print("productions:")
  # for symbol, rule in productions.items():
  #   print(symbol, ' -> ', rule)
  # print("")
  return checker, StartSym, productions, funcDefineStr

def main():
  checker, StartSym, productions, funcDefineStr = readSygus(sys.argv[1])

  # print("Productions:")
  # for k in productions:
  #   print(" ", k, productions[k])
  # print("Constraints:")
  # for c in checker.constraints:
  #   print(" ", c)

  progExpr = spec2prog(checker.constraints, checker.synFunc, productions)
  progStr = funcDefineStr[:-1] + ' ' + toString(progExpr) + funcDefineStr[-1]
  pprint.pprint(progExpr)
  print(progStr)
  res, model = checker.check(progStr)
  print(res)

if __name__ == '__main__':
  main()