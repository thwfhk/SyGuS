from z3 import *
from typing import List, Set, Dict, Tuple, Optional, Union, Any

def toString(Expr,Bracket=True,ForceBracket=False):
  if type(Expr) == str:
    return Expr
  if type(Expr) == tuple:
    return (str(Expr[1])) # handle ('Int', 1)
  if type(Expr) != list: # handler 1
    return str(Expr)
  subexpr=[]
  for expr in Expr:
    if type(expr)==list:
      subexpr.append(toString(expr, ForceBracket=ForceBracket))
    elif type(expr)==tuple:
      subexpr.append(str(expr[1]))
    else:
      subexpr.append(str(expr))
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

def DeclareVar(sort, name):
  if sort == 'Int':
    return Int(name)
  if sort == 'Bool':
    return Bool(name)
  raise Exception("Unknown sort")

def getSort(sort):
  if sort == "Int":
    return IntSort()
  if sort == "Bool":
    return BoolSort()
  raise Exception("Unknown sort")

# functional programming
def Id(x):
  return x

def fork(f, g):
  return lambda x : (f(x), g(x))

def unzip(li):
  return zip(*li)