def andCat(specs):
  res = specs[0]
  for spec in specs[1:]:
    res = ['and', res, spec]
  return res

def removeImplication(cur):
  if type(cur) != list:
    return cur
  res = []
  if cur[0] == '=>':
    left = removeImplication(cur[1])
    right = removeImplication(cur[2])
    res = ['or', ['not', left], right]
  else:
    res.append(cur[0])
    for sub in cur[1:]:
      res.append(removeImplication(sub))
  return res

def pushDownNot(cur):
  if type(cur) != list:
    return cur
  res = []
  if cur[0] == 'not':
    sub = cur[1]
    if sub[0] == 'not': # not-not
      res = pushDownNot(sub[1])
    elif sub[0] == 'and':
      res = pushDownNot(['or', ['not', sub[1]], ['not', sub[2]]])
    elif sub[0] == 'or':
      res = pushDownNot(['and', ['not', sub[1]], ['not', sub[2]]])
    elif sub[0] == '=':
      res = pushDownNot(['!=', sub[1], sub[2]])
    else:
      res = cur # cannot push down anymore
  else:
    res.append(cur[0])
    for sub in cur[1:]:
      res.append(pushDownNot(sub))
  return res

def mergeAndOr(cur):
  if type(cur) != list:
    return cur
  flag = True
  while flag:
    flag = False
    res = [cur[0]]
    if cur[0] == 'and':
      for sub in cur[1:]:
        if sub[0] == 'and':
          res.append(sub[1])
          res.append(sub[2])
          flag = True
        else:
          res.append(sub)
    elif cur[0] == 'or':
      for sub in cur[1:]:
        if sub[0] == 'or':
          res.append(sub[1])
          res.append(sub[2])
          flag = True
        else:
          res.append(sub)
    else:
      for sub in cur[1:]:
        res.append(sub)
    cur = res
  res = [cur[0]]
  for sub in cur[1:]:
    res.append(mergeAndOr(sub))
  return res

def foldMulti(name, li):
  if len(li) == 2:
    return [name, li[0], li[1]]
  return [name, li[0], foldMulti(name, li[1:])]

# NOTE: haven't tested, and maybe won't be used
def splitAndOr(cur):
  if type(cur) != list:
    return cur
  res = [cur[0]]
  if cur[0] == 'and' or cur[0] == 'or':
    cur = foldMulti(cur[0], cur[1:])
    for sub in cur[1:]:
      res.append(splitAndOr(sub))
    return res
  else:
    for sub in cur[1:]:
      res.append(splitAndOr(sub))
    return res


def formatNormalize(constraints):
  # use 'and' to connect constraints
  spec = andCat(constraints)
  # print('spec:')
  # pprint.pprint(spec)

  spec = removeImplication(spec)
  # print('spec:')
  # pprint.pprint(spec)

  spec = pushDownNot(spec)
  # print('spec:')
  # pprint.pprint(spec)

  spec = mergeAndOr(spec)
  # print('spec:')
  # pprint.pprint(spec)
  return spec

# NOTE: can only handle (=/>/< (f ...) ...)
def transConstArgs(cur, funcName, paraList):
  if type(cur) != list:
    return cur
  if cur[0] in ['=', '<', '>']:
    condList = []
    for i in [1, 2]:
      sub = cur[i]
      oth = cur[3-i]
      if sub[0] != funcName:
        continue
      # we have (=/>/< (f ...) ...), transform it!
      for i, a in enumerate(sub[1:]):
        b = paraList[i]
        if type(a) == tuple:
          condList.append(['=', b, a[1]])
          sub[i+1] = b
      if len(condList) != 0:
        res = ['=>']
        res.append(andCat(condList))
        res.append(cur)
        return res
      return cur
  res = [cur[0]]
  for sub in cur[1:]:
    res.append(transConstArgs(sub, funcName, paraList))
  return res

