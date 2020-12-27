import pprint
from z3 import *
from utils import *
from checker import *
from collections import namedtuple

# split top-level 'or' in constraints
def splitOr(constraints):
  flag = True
  while flag:
    flag = False
    newli = []
    for i, cons in enumerate(constraints):
      if cons[0] == 'or':
        newli.append(cons[1])
        newli.append(cons[2])
        flag = True
      else:
        newli.append(cons)
    constraints = newli
  return constraints

# Branch = namedtuple('Branch', 'guard result isequal')
class Branch:
  def __init__(self):
    self.guard = []
    self.result = None
    self.isequal = None
    # self.spec = None # the result spec transformed from guard
  def __repr__(self):
    return 'Branch:\n  guard:' + str(self.guard) + '\n  result: ' + str(self.result) + '\n'

class SpecTreeNode:
  def __init__(self, spec):
    self.name: str = ""
    self.children: List[SpecTreeNode] = []
    self.isleaf: bool = None
    self.value: Any = None
    self.onpath: bool = False # only used for appendGuard
    self.isend: bool = False # isend=Ture is the subtree of "f args = result"
    if spec == None:
      return
    if type(spec) == list:
      self.name = spec[0]
      self.isleaf = False
    else:
      self.isleaf = True
      if type(spec) == tuple: # handle ('Int', 1)
        self.value = spec[1]
      else:
        self.value = spec

  def __repr__(self):
    if not self.isleaf:
      return '(' + self.name + ' ' + str(self.children) + ')'
    else:
      return str(self.value)

def spec2node(spec):
  cur = SpecTreeNode(spec)
  if not cur.isleaf:
    for subspec in spec[1:]:
      cur.children.append(spec2node(subspec))
  return cur

def node2spec(node):
  spec = []
  if not node.isleaf:
    spec.append(node.name)
    for child in node.children:
      spec.append(node2spec(child))
  else:
    spec = node.value
  return spec

class SpecTree:
  def __init__(self, spec, funcName):
    self.root = spec2node(spec)
    self.funcName = funcName

  def spec2branch(self):
    branch = Branch()
    def findFunc(cur, parent):
      if cur.isleaf:
        return False
      if cur.name == self.funcName:
        parent.isend = True
        if parent.name == '=':
          branch.isequal = True
          for sibling in parent.children:
            if sibling.name != self.funcName: # result founded
              branch.result = sibling
        else:
          branch.isequal = False
        return True
      for child in cur.children:
        if findFunc(child, cur):
          cur.onpath = True
          return True
      cur.onpath = False
      return False
    findFunc(self.root, None)
    def appendGuard(cur):
      if cur.isend:
        return
      for child in cur.children:
        if not child.onpath:
          branch.guard.append(child)
      for child in cur.children:
        if child.onpath:
          appendGuard(child)
    appendGuard(self.root)
    return branch

  def getSyntaxSet(self):
    syntaxSet = set()
    def dfs(cur):
      if cur.isend or cur.isleaf:
        return
      syntaxSet.add(cur.name)
      for child in cur.children:
        dfs(child)
    dfs(self.root)
    return syntaxSet

# directly generate program from constraint specifications
# return the program on sucess
# return False on has unequal constraint
def spec2prog(constraints, synFunc, productions):
  # generate branch from constraint
  constraints = splitOr(constraints)
  branchList = []
  specSyntaxSet = set()
  for spec in constraints:
    specTree = SpecTree(spec, synFunc.name)
    branch = specTree.spec2branch()
    if not branch.isequal: # can only handle equality constraints
      return False
    branchList.append(branch)
    specSyntaxSet |= specTree.getSyntaxSet()

  # get syntax used by cfg
  cfgSyntaxSet = set()
  for prod in productions.values():
    for syntax in prod:
      if type(syntax) == list:
        cfgSyntaxSet.add(syntax[0])

  print(branchList)
  print('specSyntaxSet:', specSyntaxSet)
  print('cfgSyntaxSet:', cfgSyntaxSet)

  # use 'and' to concatenate guard and transform to list format
  for branch in branchList:
    li = branch.guard
    if len(li) != 0:
      cur = li[0]
      for x in li[1:]:
        tmp = SpecTreeNode(['and'])
        tmp.children = [cur, x]
        cur = tmp
      branch.guard = node2spec(cur)
    else:
      branch.guard = None
    branch.result = node2spec(branch.result) # TODO: may not have result

  print('transformed branch guard and result:')
  for branch in branchList:
    print(branch.guard, branch.result)

  progExpr = iteCat(branchList)
  print('progExpr:')
  pprint.pprint(progExpr)

  # TODO: desugar
  # TODO: variable mapping
  progExpr = varsMap(progExpr, synFunc)

  return progExpr

# 要处理guard == None的情况
# 要处理else，其实直接把最后一个ite去掉就行
def iteCat(branchList):
  for branch in branchList:
    if branch.guard is None: # only one unconditional branch
      return branch.result
  li = list(reversed(branchList))
  cur = li[0].result
  for branch in li[1:]:
    cur = ['ite', branch.guard, branch.result, cur]
  return cur

def varsMap(progExpr, synFunc):
  print("----------------------------------------------------------------")
  print(synFunc.argList)
  print("----------------------------------------------------------------")
  return progExpr