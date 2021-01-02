import subprocess

proc = ""


def convert_operator(op):
    mp = {}
    mp["ite"] = "ite"
    mp["+"] = "plus"
    mp["-"] = "minus"
    mp["and"] = "And"
    mp["or"] = "Or"
    mp["not"] = "Not"
    mp["<="] = "le"
    mp["="] = "eq"
    mp[">="] = "ge"
    mp["<"] = "lt"
    mp[">"] = "gt"
    return mp[op]


def add_constraint(con, synth_fun_name):
    global proc
    # print(con)
    if isinstance(con, str):
        proc += con
    elif isinstance(con, tuple):
        proc += str(con[1])
    elif isinstance(con, list):
        first = True
        if con[0] == synth_fun_name:
            proc += "(interpret ("
            for conn in con:
                if first:
                    first = False
                else:
                    proc += " "
                add_constraint(conn, synth_fun_name)
            proc += "))"
        else:
            proc += "("
            for conn in con:
                if first:
                    first = False
                else:
                    proc += " "
                add_constraint(conn, synth_fun_name)
            proc += ")"


def run(bmExpr, depth):
    global proc
    proc = "#lang rosette/safe\n\n"
    proc += "(require rosette/lib/match)\n"
    proc += "(require rosette/lib/angelic)\n"
    proc += "(require rosette/lib/synthax)\n\n"

    # print(proc)

    # print(bmExpr)

    SynFunExpr = []
    VarDecMap = {}
    Constraints = []
    FunDefMap = {}
    for expr in bmExpr:
        if len(expr) == 0:
            continue
        elif expr[0] == 'synth-fun':
            SynFunExpr = expr
        elif expr[0] == 'declare-var':
            VarDecMap[expr[1]] = expr
        elif expr[0] == 'constraint':
            Constraints.append(expr)
        elif expr[0] == 'define-fun':
            FunDefMap[expr[1]] = expr
            # TODO deal with 'define-fun'
    synth_fun_name = SynFunExpr[1]
    synth_fun_args = SynFunExpr[2]
    synth_fun_type = SynFunExpr[3]
    non_terms = SynFunExpr[4]

    # TODO add support for bool
    proc += "(define-symbolic"
    '''
    for var in VarDecMap:
        proc += " " + var
    '''
    for arg in synth_fun_args:
        proc += " " + arg[0]
    proc += " integer?)\n\n"
    # print(proc)
    proc += "(struct plus (left right) #:transparent)\n"
    proc += "(struct minus (left right) #:transparent)\n"
    proc += "(struct mul (left right) #:transparent)\n"
    proc += "(struct div (left right) #:transparent)\n"
    proc += "(struct mod (left right) #:transparent)\n"
    proc += "(struct ite (bool left right) #:transparent)\n"
    proc += "(struct And (left right) #:transparent)\n"
    proc += "(struct Or (left right) #:transparent)\n"
    proc += "(struct Not (term) #:transparent)\n"
    proc += "(struct Abs (term) #:transparent)\n"
    proc += "(struct le (left right) #:transparent)\n"
    proc += "(struct eq (left right) #:transparent)\n"
    proc += "(struct ge (left right) #:transparent)\n"
    proc += "(struct lt (left right) #:transparent)\n"
    proc += "(struct gt (left right) #:transparent)\n\n"
    # print(proc)
    proc += "(define (interpret p)\n"
    proc += "  (match p\n"
    proc += "    [(plus a b) (+ (interpret a) (interpret b))]\n"
    proc += "    [(minus a b) (- (interpret a) (interpret b))]\n"
    proc += "    [(mul a b) (* (interpret a) (interpret b))]\n"
    proc += "    [(div a b) (/ (interpret a) (interpret b))]\n"
    proc += "    [(mod a b) (modulo (interpret a) (interpret b))]\n"
    proc += "    [(ite c a b) (if (interpret c)"
    proc += " (interpret a) (interpret b))]\n"
    proc += "    [(And a b) (and (interpret a) (interpret b))]\n"
    proc += "    [(Or a b) (or (interpret a) (interpret b))]\n"
    proc += "    [(Not a) (not (interpret a))]\n"
    proc += "    [(Abs a) (abs (interpret a))]\n"
    proc += "    [(le a b) (<= (interpret a) (interpret b))]\n"
    proc += "    [(eq a b) (= (interpret a) (interpret b))]\n"
    proc += "    [(ge a b) (>= (interpret a) (interpret b))]\n"
    proc += "    [(lt a b) (< (interpret a) (interpret b))]\n"
    proc += "    [(gt a b) (> (interpret a) (interpret b))]\n"
    proc += "    [_ p]))\n\n"
    # print(proc)
    non_term_names = []
    for non_term in non_terms:
        non_term_names.append(non_term[0])
    for non_term in non_terms:
        non_term_name = non_term[0]
        non_term_type = non_term[1]
        non_term_gens = non_term[2]
        proc += "(define-synthax (" + non_term_name
        for arg in synth_fun_args:
            proc += " " + arg[0]
        proc += " depth)\n"

        term_gens = []
        no_term_gens = []
        for gen in non_term_gens:
            if isinstance(gen, tuple):
                term_gens.append(str(gen[1]))
            elif isinstance(gen, str):
                if gen in non_term_names:
                    no_term_gens.append(gen)
                else:
                    term_gens.append(gen)
            elif isinstance(gen, list):
                contain_non_term = False
                refined_gen = [convert_operator(gen[0])]
                for i in range(1, len(gen)):
                    if isinstance(gen[i], str):
                        refined_gen.append(gen[i])
                        if gen[i] in non_term_names:
                            contain_non_term = True
                    elif isinstance(gen[i], tuple):
                        refined_gen.append(str(gen[i][1]))
                if contain_non_term:
                    no_term_gens.append(refined_gen)
                else:
                    term_gens.append(refined_gen)
        # TODO think about other cases

        proc += "  #:base\n"
        proc += "  (choose\n"
        proc += "   "

        for gen in term_gens:
            if isinstance(gen, str):
                proc += " " + gen
            elif isinstance(gen, list):
                proc += " (" + gen[0]
                for i in range(1, len(gen)):
                    proc += " " + gen[i]
                proc += ")"
        if not term_gens and non_term_type == "Bool":
            proc += " (#t)"
        proc += "\n  )\n"
        proc += "  #:else\n"
        proc += "  (choose\n"
        proc += "   "
        for gen in term_gens:
            if isinstance(gen, str):
                proc += " " + gen
            elif isinstance(gen, list):
                proc += " (" + gen[0]
                for i in range(1, len(gen)):
                    proc += " " + gen[i]
                proc += ")"
        for gen in no_term_gens:
            if isinstance(gen, str):
                proc += " " + gen
            elif isinstance(gen, list):
                proc += " (" + gen[0]
                for i in range(1, len(gen)):
                    if gen[i] in non_term_names:
                        proc += " (" + gen[i]
                        for arg in synth_fun_args:
                            proc += " " + arg[0]
                        proc += " (- depth 1))"
                    else:
                        proc += " " + gen
                proc += ")"
        proc += "\n  )\n"
        proc += ")\n\n"
    proc += "(define-synthax (" + "DummyStart"
    for arg in synth_fun_args:
        proc += " " + arg[0]
    proc += " depth)\n"
    proc += "  #:base\n"
    proc += "  (choose\n"
    for non_term in non_terms:
        non_term_name = non_term[0]
        non_term_type = non_term[1]
        if (non_term_type == synth_fun_type):
            proc += "    (" + non_term_name
            for arg in synth_fun_args:
                proc += " " + arg[0]
            proc += " depth)\n"
    proc += "  )\n"
    proc += "  #:else\n"
    proc += "  (choose\n"
    for non_term in non_terms:
        non_term_name = non_term[0]
        non_term_type = non_term[1]
        if (non_term_type == synth_fun_type):
            proc += "    (" + non_term_name
            for arg in synth_fun_args:
                proc += " " + arg[0]
            proc += " depth)\n"
    proc += "  )\n)\n\n"

    # print(proc)
    proc += "(define (constraint " + synth_fun_name
    for var in VarDecMap:
        proc += " " + var
    proc += ")\n"
    proc += "  (let ([result (interpret (" + synth_fun_name
    for var in VarDecMap:
        proc += " " + var
    proc += "))])\n    (and\n"
    for constraint in Constraints:
        con = constraint[1]
        add_constraint(con, synth_fun_name)
        proc += "\n"
    proc += "    )\n  )\n)\n"
    # print(proc)
    proc += "\n"
    proc += "(define (" + synth_fun_name
    for arg in synth_fun_args:
        proc += " " + arg[0]
    proc += ") (DummyStart"
    for arg in synth_fun_args:
        proc += " " + arg[0]
    proc += " " + str(depth) + "))\n"
    proc += "(define M1 (synthesize\n"
    proc += "  #:forall (list"
    for arg in synth_fun_args:
        proc += " " + arg[0]
    proc += ")\n"
    proc += "  #:guarantee (assert (constraint " + synth_fun_name
    for arg in synth_fun_args:
        proc += " " + arg[0]
    proc += "))))\n"
    proc += "(displayln (evaluate (" + synth_fun_name
    for arg in synth_fun_args:
        proc += " " + arg[0]
    proc += ") M1))"
    # print(proc)


def Run(bmExpr):
    global proc
    depth = 1
    while True:
        run(bmExpr, depth)
        with open("tmp.rkt", "w") as rkt_file:
            print(proc, file=rkt_file)
        process = subprocess.Popen(["racket", "tmp.rkt"],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        out, err = process.communicate()
        out = out.decode("utf-8")
        err = err.decode("utf-8")
        if (out == ""):
            depth = depth + 1
        else:
            print(out)
            break
