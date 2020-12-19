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


# functional programming
def Id(x):
  return x

def fork(f, g):
  return lambda x : (f(x), g(x))

def unzip(li):
  return zip(*li)