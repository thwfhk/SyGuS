import sys
import sexp
import pprint
import translator
from getproductions import *
from utils import *

# terms: [Term]
def Extend(terms, Productions):
  ret = []
  # print("len", len(Stmts))
  for i in range(len(terms)):
    term = terms[i]
    if type(term) == list: # term is a function-application
      extend = Extend(term, Productions)
      if extend != []:
        for exTerm in extend:
          ret.append(terms[0:i] + [exTerm] + terms[i+1:])
    elif term in Productions: # term is a symbol (T or NT)
      for exTerm in Productions[term]:
        ret.append(terms[0:i] + [exTerm] + terms[i+1:])
  return ret

def stripComments(bmFile):
  noComments = '('
  for line in bmFile:
    line = line.split(';', 1)[0]
    noComments += line
  return noComments + ')'

def readSygus(filename):
  bm = stripComments(open(filename))
  # Parse string to python list
  bmExpr = sexp.sexp.parseString(bm, parseAll=True).asList()[0] 
  # print("begin-------------------------------------")
  # pprint.pprint(bmExpr)
  # print("end-------------------------------------")

  checker = translator.ReadQuery(bmExpr)

  SynFunExpr = []
  for expr in bmExpr:
    if len(expr) == 0:
      continue
    elif expr[0] == 'synth-fun':
      SynFunExpr = expr
  # print("Function to Synthesize: ")
  # pprint.pprint(SyFunExpr)
  FuncDefine = ['define-fun'] + SynFunExpr[1:4] #copy function signature
  FuncDefineStr = translator.toString(FuncDefine, ForceBracket = True)
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
  print("Productions:")
  for symbol, rule in Productions.items():
    print(symbol, ' -> ', rule)
  print("")
  return checker, StartSym, Productions, FuncDefineStr


def main():
  checker, StartSym, Productions, FuncDefineStr = readSygus(sys.argv[1])
  BfsQueue = [[StartSym]] # Top-down

  debug = 0
  cnt = 0
  ans = -1
  visit = set()
  while (BfsQueue != []):
    cur = BfsQueue.pop(0)
    # print("Extending "+str(cur))
    extend = Extend(cur, Productions)
    debug += 1
    if (debug <= 0):
      print("Extending "+str(cur))
      printlist(extend, "Extended:")
    if (extend == []): # Nothing to extend. We have a solution.
      curStr = FuncDefineStr[:-1] + ' ' + translator.toString(cur) \
            + FuncDefineStr[-1] # insert Program just before the last bracket ')'
      cnt += 1
      if checker.check(curStr): # No counter-example
        ans = curStr
        break
    for term in extend:
      termStr = str(term)
      if not termStr in visit:
        BfsQueue.append(term)
        visit.add(termStr)

  print(ans)

if __name__ == '__main__':
  main()