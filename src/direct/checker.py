from z3 import *
from utils import *
import random

class SynFunction:
  def __init__(self, SynFunExpr):
    self.synFunExpr = SynFunExpr
    self.name = SynFunExpr[1]
    self.argList = SynFunExpr[2]
    self.retSort= SynFunExpr[3]

class Checker:
  def __init__(self, varTable, synFunc, constraints):
    self.varTable = varTable
    self.synFunc = synFunc
    self.constraints = constraints
    self.solver = Solver()
    self.funcSpec = None # spec of function result
    self.consSpec = []
    for constraint in constraints:
      # print(constraint)
      self.consSpec.append('(assert %s)'%(toString(constraint)))
    # print("consSpec: ", self.consSpec)

  def check(self, funcDefStr):
    # print(funcDefStr)
    spec_smt2 = [funcDefStr] + self.consSpec
    spec_smt2 = '\n'.join(spec_smt2)
    # print("----------------spec_smt2:\n", spec_smt2)
    # print("----------------end spec_smt2")
    spec = parse_smt2_string(spec_smt2, decls = self.varTable)
    spec = Not(And(spec)) # spec is a list of constraints

    self.solver.push()
    self.solver.add(spec)
    res = self.solver.check()
    self.solver.pop()
    if res == unsat:
      return True, None
    else:
      return False, self.solver.model()