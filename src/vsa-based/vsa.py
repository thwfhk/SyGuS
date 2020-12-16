from collections import namedtuple
# Term = 'x' | '0' | 'nt-name' | ['func-name', 'nt-name1', 'nt-name2', ...]

# VSA non-terminal
# name = ('nt-name', [expected-value])
# kind = 'T' | 'U' | 'F' | 'E'
# prods = {P1, ..., Pk} | [name] | ('func-name', [name]) | ()
# mem = {name : VSANT}
VSANT = namedtuple('VSANT', 'name kind prods mem')

# mem is the cache of the result VSANT
def VSAIntersect(nt1: VSANT, nt2: VSANT, mem: dict) -> VSANT:
  assert nt1.name[0] == nt2.name[0]
  resname = (nt1.name[0], nt1.name[1] + nt2.name[1])

  if nt2.kind == 'U':
    nt1, nt2 = nt2, nt1
  if nt1.kind == 'U':
    res = VSANT(resname, 'U', [], mem)
    for name in nt1.prods:
      nt = nt1.mem[name]
      res.prods.append(VSAIntersect(nt, nt2, mem).name)
    mem[res.name] = res
    return res

  if nt1.kind == 'F' and nt2.kind == 'F':
    if nt1.prods[0] != nt2.prods[0]:
      res = VSANT(resname, 'E', (), mem)
      return res
    res = VSANT(resname, 'F', (nt1.prods[0], []), mem)
    for nt1name, nt2name in zip(nt1.prods, nt2.prods):
      tmp1 = nt1.mem[nt1name]
      tmp2 = nt2.mem[nt2name]
      res.prods[1].append(VSAIntersect(tmp1, tmp2, mem).name)
    return res

  if nt2.kind == 'P':
    nt1, nt2 = nt2, nt1
  if nt1.kind == 'P' and nt2.kind == 'F':
    res = VSANT(resname, 'P', set(), mem)
    for terminal in nt1.prods:
      if checkGenerate(terminal, nt2):
        res.prods.add(terminal)
    return res
  else: # both are 'P'
    res = VSANT(resname, 'P', set(), mem)
    res.prods = nt1.prods & nt2.prods
    return res

def checkGenerate(terminal, nt):
  pass