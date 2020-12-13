import sys
import sexp
import pprint
import translator
from utils import *

# no use :(
def CheckComplete(Stmts, Productions):
  for i in range(len(Stmts)):
    if type(Stmts[i]) == list:
      if not CheckComplete(Stmts[i], Productions):
        return False
    elif Stmts[i] in Productions:
      return False
  return True

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


if __name__ == '__main__':
  benchmarkFile = open(sys.argv[1])
  bm = stripComments(benchmarkFile)
  # Parse string to python list
  bmExpr = sexp.sexp.parseString(bm, parseAll=True).asList()[0] 
  # print("begin-------------------------------------")
  # pprint.pprint(bmExpr)
  # print("end-------------------------------------")
  checker = translator.ReadQuery(bmExpr)
  SynFunExpr = []
  StartSym = 'My-Start-Symbol' #virtual starting symbol
  for expr in bmExpr:
    if len(expr)==0:
      continue
    elif expr[0]=='synth-fun':
      SynFunExpr=expr
  # print("Function to Synthesize: ")
  # pprint.pprint(SynFunExpr)
  # print("")
  FuncDefine = ['define-fun'] + SynFunExpr[1:4] #copy function signature
  FuncDefineStr = translator.toString(FuncDefine, ForceBracket = True)
  # use Force Bracket = True on function definition. MAGIC CODE. DO NOT MODIFY THE ARGUMENT ForceBracket = True.
  BfsQueue = [[StartSym]] # Top-down
  Productions = {StartSym : []}
  Type = {StartSym : SynFunExpr[3]} # set starting symbol's return type

  for NonTerm in SynFunExpr[4]: # SynFunExpr[4] is the production rules
    NTName = NonTerm[0]
    NTType = NonTerm[1]
    if NTType == Type[StartSym]:
      Productions[StartSym].append(NTName) # 'My-Start-Symbol' : 'Start'
    Type[NTName] = NTType
    #Productions[NTName] = NonTerm[2]
    Productions[NTName] = []
    for NT in NonTerm[2]:
      if type(NT) == tuple:
        Productions[NTName].append(str(NT[1]))
        # deal with ('Int',0). 
        # You can also utilize type information, but you will suffer from these tuples.
      else:
        Productions[NTName].append(NT)
  # print("Productions:")
  # for symbol, rule in Productions.items():
  #   print(symbol, ' -> ', rule)
  # print("")

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
      counterexample = checker.check(curStr)
      # print("counterexample: ", counterexample, "\n")
      if (counterexample == None): # No counter-example
        ans = curStr
        break
    for term in extend:
      termStr = str(term)
      if not termStr in visit:
        BfsQueue.append(term)
        visit.add(termStr)

  print(ans)

  # Examples of counter-examples  
  # print (checker.check('(define-fun max2 ((x Int) (y Int)) Int 0)'))
  # print (checker.check('(define-fun max2 ((x Int) (y Int)) Int x)'))
  # print (checker.check('(define-fun max2 ((x Int) (y Int)) Int (+ x y))'))
  # print (checker.check('(define-fun max2 ((x Int) (y Int)) Int (ite (<= x y) y x))'))
