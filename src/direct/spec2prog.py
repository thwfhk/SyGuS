import pprint
from z3 import *
from utils import *
from checker import *
from sugarlib import *
from specformatter import *

class Branch:
  def __init__(self):
    self.guard = []
    self.result = None
    self.isequal = None
    self.argList = []
    # self.spec = None # the result spec transformed from guard
  def __repr__(self):
    return 'Branch:\n  guard:' + str(self.guard) \
            + '\n  result: ' + str(self.result) \
            + '\n  isequal: ' + str(self.isequal)\
            + '\n  argList: ' + str(self.argList) + '\n'

class SpecTreeNode:
  def __init__(self, spec):
    self.name: str = ""
    self.children: List[SpecTreeNode] = []
    self.parent = None
    self.isleaf: bool = None
    self.value: Any = None
    self.onpath: bool = False # on the path to function
    self.isfcons: bool = False # the root of function constraints
    self.branch: Branch = None # only isfcons=True has a branch
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
      if self.parent:
        parentStr = '(parent: ' + str(self.parent.name) + ') '
      else:
        parentStr = '(root) '
      parentStr = ''
      return '(' + self.name + parentStr + str(self.children) + ')'
    else:
      return str(self.value)

def spec2node(spec):
  cur = SpecTreeNode(spec)
  if not cur.isleaf:
    for subspec in spec[1:]:
      cur.children.append(spec2node(subspec))
      cur.children[-1].parent = cur
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
    # self.argList = []
    self.branchList = []
  
  # find all constraints on function results
  def findFunc(self, cur, parent):
    if cur.isleaf:
      return False
    if cur.name == self.funcName:
      branch = Branch()
      branch.argList = list(map(lambda x: x.value ,cur.children))
      parent.isfcons = True
      parent.branch = branch
      if parent.name == '=':
        branch.isequal = True
        for sibling in parent.children:
          if sibling.name != self.funcName: # result founded
            branch.result = sibling
      else:
        branch.isequal = False
      return True
    for child in cur.children:
      if self.findFunc(child, cur):
        cur.onpath = True
    return cur.onpath

  def getGuard(self, cur, guard):
    if cur.isleaf:
      return
    if cur.isfcons:
      cur.branch.guard = guard.copy()
      self.branchList.append(cur.branch)
      return
    if cur.name == 'and':
      for child in cur.children:
        if not child.onpath:
          guard.append(child)
      for child in cur.children:
        if child.onpath:
          self.getGuard(child, guard.copy())
    elif cur.name == 'or':
      for child in cur.children:
        if not child.onpath:
          tmp = SpecTreeNode(['not'])
          tmp.children.append(child)
          guard.append(tmp)
      for child in cur.children:
        if child.onpath:
          self.getGuard(child, guard.copy())
    else:
      raise Exception('getGuard error: cannot get guards for {}'.format(cur.name))

  def branchExtract(self):
    self.findFunc(self.root, None)
    self.getGuard(self.root, [])
    return self.branchList

  def getSyntaxSet(self):
    syntaxSet = set()
    constList = []
    def dfs(cur):
      if cur.name == self.funcName:
        return
      if cur.isleaf:
        if type(cur.value) == int:
          constList.append(str(cur.value))
        return
      syntaxSet.add(cur.name)
      for child in cur.children:
        dfs(child)
    dfs(self.root)
    return syntaxSet, constList

# directly generate program from constraint specifications
# return the program on sucess
# return False on has unequal constraint
def spec2prog(constraints, synFunc, productions):
  paraList = list(map(lambda x: x[0], synFunc.argList))
  spec = formatNormalize(constraints, synFunc.name, paraList)
  # print('formalized spec:')
  # pprint.pprint(spec)

  specTree = SpecTree(spec, synFunc.name)
  specSyntaxSet, specConstList = specTree.getSyntaxSet()
  branchList = specTree.branchExtract()
  argList = branchList[0].argList
  # print(specTree.root)
  # print(branchList)

  for branch in branchList:
    if not branch.isequal:
      return False, 'unequal constraint on result'
    if branch.argList != argList:
      return False, 'different arguments list'

  # get syntax used by cfg
  cfgSyntaxSet = set()
  constList = []
  for prod in productions.values():
    for syntax in prod:
      if type(syntax) == list:
        cfgSyntaxSet.add(syntax[0])
      elif not syntax in paraList and not syntax in productions:
        constList.append(syntax)
  # print(constList)
  # print(specConstList)

  # Don't handle constants, just fail
  # if not set(specConstList).issubset(set(constList)):
  #   return False, 'constants not in CFG'

  # use 'and' to concatenate guard and transform to list format
  for branch in branchList:
    li = branch.guard
    if len(li) != 0:
      cur = li[0]
      for x in li[1:]:
        tmp = SpecTreeNode(['and'])
        tmp.children = [cur, x]
        cur = tmp
      branch.guard = splitAndOr(pushDownNot(node2spec(cur)))
    else:
      branch.guard = None
    branch.result = splitAndOr(node2spec(branch.result))
  # print(branchList)

  # print('transformed branch guard altnd result:')
  # for branch in branchList:
  #   print(branch.guard, branch.resu)

  progExpr = iteCat(branchList)
  # print('progExpr:')
  # pprint.pprint(progExpr)

  # variable mapping
  progExpr = varsMap(progExpr, paraList, argList)
  # desugar
  desugar = Desugar(progExpr, specSyntaxSet, cfgSyntaxSet, paraList, constList)
  try:
    progExpr = desugar.desugar(progExpr)
    progExpr = desugar.desugarConstant(progExpr)
  except Exception as e:
    return False, 'desugar error: ' + str(e)
  # pprint.pprint(progExpr)
  return True, progExpr

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