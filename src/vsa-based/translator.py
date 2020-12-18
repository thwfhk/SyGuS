from z3 import *
from example import *
import random

verbose = False

def toString(Expr,Bracket=True,ForceBracket=False):
  if type(Expr)==str:
    return Expr
  if type(Expr)==tuple:
    return (str(Expr[1])) # todo: immediate
  subexpr=[]
  for expr in Expr:
    if type(expr)==list:
      subexpr.append(toString(expr, ForceBracket=ForceBracket))
    elif type(expr)==tuple:
      subexpr.append(str(expr[1]))
    else:
      subexpr.append(expr)
  if not Bracket:
    #print subexpr
    return "%s"%(' '.join(subexpr))
  # Avoid Redundant Brackets
  if ForceBracket:
    return "(%s)"%(' '.join(subexpr))
  if len(subexpr)==1:
    return "%s"%(' '.join(subexpr))
  else:
    return "(%s)"%(' '.join(subexpr))

class SynFunction:
  def __init__(self, SynFunExpr):
    self.name=SynFunExpr[1]
    # TODO: arg and ret sort
    self.argList=SynFunExpr[2]
    self.retSort=SynFunExpr[3]
    self.Sorts=[]
    for expr in self.argList:
      self.Sorts.append(getSort(expr[1]))
    self.Sorts.append(getSort(self.retSort))
    self.targetFunction=Function('__TARGET_FUNCTION__', *(self.Sorts))

class Checker:
  def __init__(self, VarTable, synFunction, Constraints):
    self.VarTable=VarTable
    self.synFunction=synFunction
    self.Constraints=Constraints
    self.solver=Solver()
    # self.ces = [] # list of counterexamples
    self.examples = []
    self.funcSpec = None # spec of function result
    self.consSpec = []
    for constraint in Constraints:
      self.consSpec.append('(assert %s)'%(toString(constraint[1:])))
    self.generateRandomExamples()

  @staticmethod
  def constructFuncStr(name, argList):
    res = name
    for arg in argList:
      res = res + ' ' + arg[0]
    res = '(' + res + ')'
    return res

  # get the output of the given input as a python long value
  def getResult(self, subs):
    cur = substitute(self.funcSpec, *subs)
    self.solver.push()
    self.solver.add(cur)
    if self.solver.check() == unsat:
      Exception("Unsat Input.")
    m = self.solver.model()
    res = m[DeclareVar(self.synFunction.retSort, 'result')]
    self.solver.pop()
    return res.as_long()

  def generateSingleExample(self, vals):
    vars = list(self.VarTable.keys())
    example = Example()
    for var, val in zip(vars, vals):
      example.term2val[var] = val
    example.subs = list(zip(self.VarTable.values(), map(IntVal, vals)))
    example.output = self.getResult(example.subs)
    return example

  examplesMinNum = 3
  # generate examples for max
  # NOTE: only consider generate Int value
  def generateRandomExamples(self):
    print("-----generateExamples begin-----")
    funcStr = Checker.constructFuncStr(self.synFunction.name,\
                self.synFunction.argList)
    specStr = '\n'.join(self.consSpec).replace(funcStr, 'result')
    varTable = self.VarTable.copy()
    resultSymbol = DeclareVar(self.synFunction.retSort, 'result')
    varTable['result'] = resultSymbol
    spec = parse_smt2_string(specStr, decls = varTable)
    spec = And(spec)
    self.funcSpec = spec
    # print(spec)

    vars = list(self.VarTable.keys())
    n = len(vars)
    for i in range(max(n, Checker.examplesMinNum)):
      # li = random.sample(range(0, n), n)
      li = list(map(lambda x: random.randint(0, n), range(n)))
      # li[i] = max(li) + (random.randint(1,2) == 1) # magic :)
      example = self.generateSingleExample(li)
      self.examples.append(example)
      # example.print()
    print("-----generateExamples end-----")

  # NOTE: 这里是把变量代入后检查约束，而不是检查函数结果是否=output
  # 效率应该差不多吧
  def checkExamples(self, spec):
    for example in self.examples:
      cur = substitute(spec, *example.subs)
      self.solver.push()
      self.solver.add(cur)
      if self.solver.check() == sat:
        return True
      self.solver.pop()
    return False

  def check(self, funcDefStr):
    # print(funcDefStr)
    spec_smt2 = [funcDefStr] + self.consSpec
    spec_smt2 = '\n'.join(spec_smt2)
    # print("----------------spec_smt2:\n", spec_smt2)
    # print("----------------end spec_smt2")
    spec = parse_smt2_string(spec_smt2, decls = self.VarTable)
    spec = Not(And(spec)) # spec is a list of constraints
    if verbose:
      print("spec:",spec)

    # use examples
    if self.checkExamples(spec) == True: # satisfied
      return False

    self.solver.push()
    self.solver.add(spec)
    res = self.solver.check()
    if res == unsat:
      self.solver.pop()
      return True
    else:
      model = self.solver.model()
      self.solver.pop()
      example = model2Example(model, self)
      self.examples.append(example)
      print("\nnew counter-example:")
      example.print()
      return False

def ReadQuery(bmExpr):
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
  
  if verbose:
    print(SynFunExpr)
    print(VarDecMap)
    print(FunDefMap)
    print(Constraints)
  
  VarTable={}
  # Declare Var
  for var in VarDecMap:
    VarTable[var] = DeclareVar(VarDecMap[var][2], var)

  # Declare Target Function
  synFunction=SynFunction(SynFunExpr)

  checker = Checker(VarTable, synFunction, Constraints)
  return checker
