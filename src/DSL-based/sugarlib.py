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
    print(progExpr)
    print('specSyntaxSet:', specSyntaxSet)
    print('cfgSyntaxSet:', cfgSyntaxSet)
    self.progExpr = progExpr
    self.specSyntaxSet = specSyntaxSet
    self.cfgSyntaxSet = cfgSyntaxSet
    self.paraList = paraList
    self.constList = constList
    self.diff = specSyntaxSet - cfgSyntaxSet
    print('diff:', self.diff)

  def desugar(self, cur):
    res = []
    if type(cur) != list:
      return cur
    if cur[0] in self.diff:
      if cur[0] == 'and' and 'ite' in self.cfgSyntaxSet:
        res = self.and2ite(res, cur)
      elif cur[0] == 'max' and 'ite' in self.cfgSyntaxSet:
        res = self.max2ite(res, cur)
      else:
        Exception('desugar error: cannot handle {}'.format(cur[0]))
    else:
      res.append(cur[0])
      for sub in cur[1:]:
        res.append(self.desugar(sub))
    return res

  def and2ite(self, res, cur):
    left = self.desugar(cur[1])
    right = self.desugar(cur[2])
    false = self.getFalse()
    return ['ite', left, right, false]

  def max2ite(self, res, cur):
    return cur

  def getFalse(self):
    if 'False' in self.constList:
      return 'False'
    if len(self.paraList) != 0:
      c = self.paraList[0]
    elif len(self.constList) != 0:
      c = self.constList[0]
    else:
      Exception('desugar error: no False')
    if '<' in self.cfgSyntaxSet:
      return ['<', c, c]
    if '>' in self.cfgSyntaxSet:
      return ['>', c, c]
    Exception('desugar error: no False')

  def getTrue(self):
    if 'True' in self.constList:
      return 'True'
    if len(self.paraList) != 0:
      c = self.paraList[0]
    elif len(self.constList) != 0:
      c = self.constList[0]
    else:
      Exception('desugar error: no True')
    if '=' in self.cfgSyntaxSet:
      return ['=', c, c]
    Exception('desugar error: no True')
