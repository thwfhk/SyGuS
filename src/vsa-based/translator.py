from z3 import *
import random

verbose = False


def DeclareVar(sort,name):
  if sort=="Int":
    return Int(name)
  if sort=='Bool':
    return Bool(name)
  raise Exception("Unknown sort")

def getSort(sort):
  if sort=="Int":
    return IntSort()
  if sort=="Bool":
    return BoolSort()
  raise Exception("Unknown sort")

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
  synFunction=SynFunction(SynFunExpr)

  class Checker:
    def __init__(self, VarTable, synFunction, Constraints):
      self.VarTable=VarTable
      self.synFunction=synFunction
      self.Constraints=Constraints
      self.solver=Solver()
      self.ces = [] # list of counterexamples
      self.es = []
      self.generateExamples()

      self.consSpec = []
      for constraint in Constraints:
        self.consSpec.append('(assert %s)'%(toString(constraint[1:])))

    # maybe useless
    def generateExamples(self):
      vars = list(self.VarTable.values())
      n = len(vars)
      print(vars, n)
      for i in range(max(n, 5)):
        # li = random.sample(range(0, n), n)
        li = list(map(lambda x: IntVal(random.randint(0, n)), range(n)))
        # li[i] = max(li) + (random.randint(1,2) == 1) # magic :)
        print(li)
        self.es.append(list(zip(vars, li)))
      print(self.es)

    def checkExamples(self, spec):
      for subs in self.es:
        cur = substitute(spec, *subs)
        # print("cur:", cur, "\nspec:", spec, "\nsubs:", subs)
        self.solver.push()
        self.solver.add(cur)
        if (self.solver.check() == sat):
          return True
        self.solver.pop()
      return False

    def check(self, funcDefStr):
      spec_smt2 = [funcDefStr] + self.consSpec
      spec_smt2 = '\n'.join(spec_smt2)
      # print("----------------spec_smt2:\n", spec_smt2)
      # print("----------------end spec_smt2")
      spec = parse_smt2_string(spec_smt2, decls = self.VarTable)
      spec = Not(And(spec)) # spec is a list of constraints
      if verbose:
        print("spec:",spec)

      # use examples
      if self.checkExamples(spec) == True:
        return 1
      # use counter-examples first
      for model in self.ces:
        if (model.eval(spec) == True):
          return model

      self.solver.push()
      self.solver.add(spec)
      res = self.solver.check()
      if res == unsat:
        self.solver.pop()
        return None
      else:
        model=self.solver.model()
        self.solver.pop()
        self.ces.append(model)
        return model

  checker = Checker(VarTable, synFunction, Constraints)
  return checker
