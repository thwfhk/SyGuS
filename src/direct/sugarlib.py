import pprint

# map all variables in progExpr from argList to paraList
def varsMap(progExpr, paraList, argList):
  # print("----------------------------------------------------------------")
  # print(paraList)
  # print(argList)
  arg2para = dict(zip(argList, paraList))
  def dfs(cur):
    res = []
    if type(cur) != list:
      if cur in arg2para:
        return arg2para[cur]
      return cur
    res.append(cur[0])
    for sub in cur[1:]:
      res.append(dfs(sub))
    return res
  # print("----------------------------------------------------------------")
  return dfs(progExpr)


class Desugar:
  def __init__(self, progExpr, specSyntaxSet, cfgSyntaxSet, paraList, constList):
    self.progExpr = progExpr
    self.specSyntaxSet = specSyntaxSet
    self.cfgSyntaxSet = cfgSyntaxSet
    self.paraList = paraList
    self.constList = constList
    self.diff = specSyntaxSet - cfgSyntaxSet
    # print('Desugar------------------------------------------')
    # print('progExpr', progExpr)
    # print('specSyntaxSet:', specSyntaxSet)
    # print('cfgSyntaxSet:', cfgSyntaxSet)
    # print('diff:', self.diff)
    # print('Desugar------------------------------------------')

  def isCompVarConst(self, cur):
    if not cur[0] in ['=', '!=', '<', '>', '<=', '>=']:
      return False
    if not cur[1] in self.paraList:
      return False
    if not type(cur[2]) == int:
      return False
    return True

  def findMultiple(self, num):
    for s in self.constList:
      if s[-1].isdigit():
        x = int(s)
        if x != 0 and x % num == 0:
          return x
    return None

  def constructMultiply(self, var, cnt):
    if not '+' in self.cfgSyntaxSet:
      raise Exception('we have no add :(')
      # return False
    res = var
    for i in range(cnt-1):
      res = ['+', res, var]
    return res

  # constList is of type [str]
  # we only handle int constant
  def desugarConstant(self, cur):
    if type(cur) != list:
      return cur
    if self.isCompVarConst(cur):
      var = cur[1]
      num = cur[2]
      if not str(num) in self.constList:
        multiple = self.findMultiple(num)
        if multiple is None:
          raise Exception('cannot handle {}'.format(str(cur)))
        cnt = multiple // num
        res = [cur[0], self.constructMultiply(var, cnt), multiple]
        return res
      return cur
    else:
      res = [cur[0]]
      for sub in cur[1:]:
        res.append(self.desugarConstant(sub))
      return res

  def desugar(self, cur):
    res = []
    if type(cur) != list:
      return cur
    if cur[0] in self.diff:
      if cur[0] == 'and' and 'ite' in self.cfgSyntaxSet:
        res = self.and2ite(cur)
      elif cur[0] == 'max' and 'ite' in self.cfgSyntaxSet:
        res = self.max2ite(cur)
      elif cur[0] == '>' and '<=' in self.cfgSyntaxSet \
            and 'not' in self.cfgSyntaxSet:
        res = self.g2notle(cur)
      elif cur[0] == '<' and '>=' in self.cfgSyntaxSet \
            and 'not' in self.cfgSyntaxSet:
        res = self.l2notge(cur)
      elif cur[0] == '!=' and 'not' in self.cfgSyntaxSet \
            and '=' in self.cfgSyntaxSet:
        res = self.neq2noteq(cur)
      else:
        res = self.sugarSearch(cur)
        if not res:
          raise Exception('desugar error: cannot handle {}'.format(cur[0]))
    else:
      res.append(cur[0])
      for sub in cur[1:]:
        res.append(self.desugar(sub))
    return res

  # ----------------------------------------------------------------
  # utilities for desugaring
  def and2ite(self, cur):
    left = self.desugar(cur[1])
    right = self.desugar(cur[2])
    false = self.getFalse()
    return ['ite', left, right, false]

  def or2ite(self, cur):
    left = self.desugar(cur[1])
    right = self.desugar(cur[2])
    true = self.getTrue()
    return ['ite', left, true, right]

  def not2ite(self, cur):
    tmp = self.desugar(cur[1])
    true = self.getTrue()
    false = self.getFalse()
    return ['ite', tmp, false, true]

  def max2ite(self, cur):
    left = self.desugar(cur[1])
    right = self.desugar(cur[2])
    return ['ite', ['<', left, right], right, left]

  def g2notle(self, cur):
    left = self.desugar(cur[1])
    right = self.desugar(cur[2])
    return ['not', ['<=', left, right]]

  def l2notge(self, cur):
    left = self.desugar(cur[1])
    right = self.desugar(cur[2])
    return ['not', ['>=', left, right]]

  def neq2noteq(self, cur):
    left = self.desugar(cur[1])
    right = self.desugar(cur[2])
    return ['not', ['=', left, right]]

  # ----------------------------------------------------------------
  # utilities for getting constants
  def getFalse(self):
    if 'False' in self.constList:
      return 'False'
    if len(self.paraList) != 0:
      c = self.paraList[0]
    elif len(self.constList) != 0:
      c = self.constList[0]
    else:
      raise Exception('desugar error: no False')
    if '<' in self.cfgSyntaxSet:
      return ['<', c, c]
    if '>' in self.cfgSyntaxSet:
      return ['>', c, c]
    raise Exception('desugar error: no False')

  def getTrue(self):
    if 'True' in self.constList:
      return 'True'
    if len(self.paraList) != 0:
      c = self.paraList[0]
    elif len(self.constList) != 0:
      c = self.constList[0]
    else:
      raise Exception('desugar error: no True')
    if '=' in self.cfgSyntaxSet:
      return ['=', c, c]
    raise Exception('desugar error: no True')

  def sugarSearch(self, cur):
    return False
