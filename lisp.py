import traceback
import sys

Symbol = str

class Env(dict):
    #environment distinction(outer and inner)
    def __init__(self, params=(), args=(), outer = None):
        self.update(zip(params, args))
        self.outer = outer
    def find(self, var):
        #finds innermost scope where var appears 
        return self if var in self else self.outer.find(var)

def add_globals(env):
    import operator 
    env.update({
        '+' : operator.add,
        '-' : operator.sub,
        '*' : operator.mul,
        '/' : operator.truediv,
        '>' : operator.gt,
        '<' : operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
        '=' : operator.eq
        })
    env.update({'True':True, 'False': False})
    return env

global_env = add_globals(Env())
isa = isinstance

#eval

def eval(x, env = global_env):
    if isa(x, Symbol):
        return env.find(x)[x]
    elif not isa(x,list):
        return x 
    elif x[0] == 'quote' or x[0] == 'q':
        (_, exp) = x
        return exp
    elif x[0] == 'atom?':
        (_, exp) = x
        return not isa(eval(exp,env), list)
    elif x[0] == 'eq?':
        (_,exp1,exp2) = x
        v1, v2  = eval(exp1, env), eval(exp2 , env)
        return (not isa(v1,list)) and (v1 == v2)
    elif x[0] == 'car':
        (_,exp) = x
        return eval(exp,env)[0]
    elif x[0] == 'cdr':
        (_,exp1) = x
        return eval(exp,env)[1:]
    elif x[0] == 'cons':
        (_,exp1,exp2) = x
        return [eval(exp1,env)]+eval(exp2,env)
    elif x[0] == 'cond':
        for(p,e) in x[1:]:
            if eval(p,env):
                return eval(e,env)
    elif x[0] == "null?":
        (_,exp) = x
        return eval(exp,env) == []
    elif x[0] == 'if':
        (_, test,conseq,alt) = x
        return eval((conseq if eval(test,env) else alt),env)
    elif x[0] == 'set!':
        (_,var,exp) =  x
        env.find(var)[var] = eval(exp,env)
    elif x[0] == 'define':
        (_,var,exp) = x
        env[var] = eval(exp,env)
    elif x[0] == 'lambda':
        (_,vars,exp) = x
        return lambda *args: eval(exp,Env(vars,args,env))
    elif x[0] == 'begin':
        for exp in x[1:]:
            val = eval(exp,env)
        return val
    else:
        exps = [eval(exp,env) for exp in x]
        proc = exps.pop(0)
        return proc(*exps)
#parser

def parse(s):
    return read_from(tokenize(s))
def tokenize(s):
    return s.replace(')', ' ) ').replace('(', ' ( ').split()

def read_from(tokens):
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        L = []
        while tokens[0] != ')':
            L.append(read_from(tokens))
        tokens.pop(0) #this will remove ')'
        return L
    elif ')' == token:
        raise SyntaxError('unexpected )')
    else:
        return atom(token)
def atom(token):
    try : return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Symbol(token)
def to_string(exp):
    if not(isa(exp,list)):
        return str(exp)
    else:
        return '('+' '.join(map(to_string, exp))+')'
    
## loading from a file and executing it 
def load(filename):
    print("Loading and executing")
    f = open(filename , "r")
    program = f.readlines()
    f.close()
    rps = running_paren_sums(program)
    full_line = ""
    for(paren_sum,program_line) in zip(rps, program):
        program_line = program_line.strip()
        full_line += program_line+" "
        if paren_sum == 0 and full_line.strip() != "":
            try:
                val = eval(parse(full_line))
                if val is not None: print (to_string(val))
            except:
                handle_error()
                print ("\nThe line in whhich the error occured: \n")
                break 
            full_line = ""
    repl()

def running_paren_sums(program):
    count_open_parens = lambda line: line.count("(")-line.count(")")
    paren_counts = map(count_open_parens, program)
    rps = []
    total = 0
    for paren_count in paren_counts:
        total += paren_count
        rps.append(total)
    return rps
#REPL
def repl(prompt = 'lisp> '):
    while True:
        try:
            val = eval(parse(input(prompt)))
            if val is not None: print (to_string(val))
        except KeyboardInterrupt:
            print ("\n Exiting lisp\n")
            sys.exit()
        except:
            handle_error()

#error handling(very barebones)
def handle_error():
    #for both the repl and load#
    print ("An error occured. Refer to the Python stack trace: \n")
    traceback.print_exc()

#startup sequence 
if __name__ == "__main__":
    if len(sys.argv) > 1:
        load(sys.argv[1])
    else:
        repl()