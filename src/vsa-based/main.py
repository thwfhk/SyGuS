import sys
import sexp
import pprint
import translator
from vsa import *
from utils import *
from getproductions import *

# terms: [Term]
def Extend(terms, Productions):
  ret = []
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
  # print("Productions:")
  # for symbol, rule in Productions.items():
  #   print(symbol, ' -> ', rule)
  # print("")
  return checker, StartSym, Productions, FuncDefineStr

def debugTest():
  checker, StartSym, Productions, FuncDefineStr = readSygus(sys.argv[1])
  initialVSA = VSA()
  initialVSA.CFG2VSA(Productions, StartSym)
  # initialVSA.print()
  program = initialVSA.generateProgram()
  print(program)

  print('VSA1')
  example = checker.generateSingleExample([1,1])
  example.print()
  VSA1 = example.generateVSA(initialVSA)
  # VSA1.print()
  program1 = VSA1.generateProgram()
  print(program1)
  # return None

  print('VSA2')
  example = checker.generateSingleExample([2,1])
  example.print()
  VSA2 = example.generateVSA(initialVSA)
  # VSA2.print()
  program2 = VSA2.generateProgram()
  print(program2)

  print('VSA3')
  VSA3 = VSAIntersect(VSA1, VSA2)
  # VSA3.print()
  program3 = VSA3.generateProgram()
  print(program3)

def CEGIS(curVSA, checker, FuncDefineStr, initialVSA):
  while True:
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
  # debugTest()
  main()