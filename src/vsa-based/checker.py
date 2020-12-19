from z3 import *
from example import *
import random

class SynFunction:
  def __init__(self, SynFunExpr):
    self.name=SynFunExpr[1]
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

  # generate 
  def generateSingleExample(self, vals):
    vars = list(self.VarTable.keys())
    example = Example()
    for var, val in zip(vars, vals):
      example.term2val[var] = val
    example.subs = list(zip(self.VarTable.values(), map(IntVal, vals)))
    example.output = self.getResult(example.subs)
    return example

  def generateExamples4Max(self, n):
    for i in range(n):
      li = [0] * n
      print(li)
      li[i] = 1
      example = self.generateSingleExample(li)
      self.examples.append(example)

  examplesNum = 1
  # generate examples for max
  # NOTE: only consider generate Int value
  def generateRandomExamples(self):
    # print("-----generateExamples begin-----")
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
    # self.generateExamples4Max(n)
    # return None
    for i in range(Checker.examplesNum):
      li = list(map(lambda x: random.randint(0, n), range(n)))
      example = self.generateSingleExample(li)
      self.examples.append(example)
      # example.print()
    # print("-----generateExamples end-----")

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

    # use examples NOTE: not needed in vsa-based
    # if self.checkExamples(spec) == True: # satisfied
    #   return False, None

    self.solver.push()
    self.solver.add(spec)
    res = self.solver.check()
    if res == unsat:
      self.solver.pop()
      return True, None
    else:
      model = self.solver.model()
      self.solver.pop()
      example = model2Example(model, self)
      self.examples.append(example)
      print("\nnew counter-example:")
      example.print()
      return False, example
