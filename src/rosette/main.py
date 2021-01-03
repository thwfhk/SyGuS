import sys
import sexp
import pprint
import translator
import rosette_driver

# no use :(
def CheckComplete(Stmts, Productions):
    for i in range(len(Stmts)):
        if type(Stmts[i]) == list:
            if not CheckComplete(Stmts[i], Productions):
                return False
        elif Stmts[i] in Productions:
            return False
    return True

def Extend(Stmts,Productions):
    ret = []
    # print("len", len(Stmts))
    for i in range(len(Stmts)):
        if type(Stmts[i]) == list:
            TryExtend = Extend(Stmts[i], Productions)
            if len(TryExtend) > 0 :
                for extended in TryExtend:
                    ret.append(Stmts[0:i]+[extended]+Stmts[i+1:])
        elif Stmts[i] in Productions:
            for extended in Productions[Stmts[i]]:
                ret.append(Stmts[0:i]+[extended]+Stmts[i+1:])
    return ret

def stripComments(bmFile):
    noComments = '('
    for line in bmFile:
        line = line.split(';', 1)[0]
        noComments += line
    return noComments + ')'


if __name__ == '__main__':
    benchmarkFile = open(sys.argv[1])
    bm = stripComments(benchmarkFile)
    # Parse string to python list
    bmExpr = sexp.sexp.parseString(bm, parseAll=True).asList()[0]
    ans = rosette_driver.Run(bmExpr)
    print(ans)
    # pprint.pprint(bmExpr)
