import pattern_match as pm
from sugar import *
import expr as expression
import codegen

class BaseEnv:
    def __init__(self):
        self.parent = None
        self.bound_vars = {}

    def get(self, key):
        int_matcher = pm.match(L(('int_constant', pm.Star('x'))))
        m = int_matcher.attempt_match(key)
        if m is not None:
            return ('int_constant', m['x'])
        char_matcher = pm.match(L(('char_constant', pm.Star('x'))))
        m = char_matcher.attempt_match(key)
        if m is not None:
            return ('char_constant', m['x'])
        string_matcher = pm.match(L(('string_constant', pm.Star('x'))))
        m = string_matcher.attempt_match(key)
        if m is not None:
            return ('string_constant', m['x'])
        stack_address_matcher = pm.match(L(('stack_address', pm.Star('x'))))
        m = stack_address_matcher.attempt_match(key)
        if m is not None:
            return ('stack_address', m['x'])
        raise KeyError(key)

class Env:
    def __init__(self, parent = None):
        self.parent = parent
        self.bound_vars = {}
        self.deallocation_list = []

    def declare(self, key):
        assert key not in self.bound_vars
        self.bound_vars[key] = None

    def set(self, key, value):
        assert key in self.bound_vars
        self.bound_vars[key] = value

    def get(self, key):
        if key in self.bound_vars:
            return self.bound_vars[key]
        elif self.parent is not None:
            return self.parent.get(key)
        else:
            raise KeyError(key)

    def outer_get(self, key):
        assert self.parent is not None
        return self.parent.get(key)

    def free_local_on_env_exit(self, local):
        self.deallocation_list.append(local)

def pretty_print_env(env):
    i = 0
    while env is not None:
        print('env[%d]' % i)
        for key in sorted(env.bound_vars):
            print('\t%s --> %s' % (str(key), str(env.bound_vars[key])))
        env = env.parent
        i += 1

class StackMan:
    def __init__(self):
        self._allocated_cells = set()

    def next_free_cell(self):
        i = 0
        while i in self._allocated_cells:
            i += 1
        return i

    def allocate_local(self):
        i = self.next_free_cell()
        self._allocated_cells.add(i)
        return ('stack_address', i)

    def free_local(self, local):
        m = pm.match(('stack_address', pm.Star('i'))).attempt_match(local)
        assert m is not None
        self._allocated_cells.remove(m['i'])

    def allocated_cells(self):
        return list(sorted(list(self._allocated_cells)))


class CompilerState:
    def __init__(self, current_env, stack_man, machine):
        self.current_env = current_env
        self.stack_man = stack_man
        self.machine = machine

def compile_phase_2(built_in_macros, macro):

    n_cells = 30000

    state = CompilerState(
        current_env = BaseEnv(),
        stack_man = StackMan(),
        machine = codegen.Machine(n_cells),
    )

    def lookup_built_in_macro(name):
        return built_in_macros[name]

    # environment actions

    def do_env_begin(state):
        state.current_env = Env(parent = state.current_env)

    def do_env_end(state):
        for x in state.current_env.deallocation_list:
            do_free_local(state, x)
        state.current_env = state.current_env.parent

    def do_env_declare(state, key):
        state.current_env.declare(key)

    def do_env_set(state, key, value):
        state.current_env.set(key, value)
    
    def do_env_get(state, key):
        return state.current_env.get(key)

    def do_outer_env_get(state, key):
        return state.current_env.outer_get(key)

    def do_argument_lookup(state, *args):
        return [state.current_env.get(arg) for arg in args]

    # local allocation actions

    def do_allocate_local(state):
        return state.stack_man.allocate_local()

    def do_free_local(state, x):
        return state.stack_man.free_local(x)

    def do_free_local_on_env_exit(state, x):
        return state.current_env.free_local_on_env_exit(x)

    # built in macro call support
    def do_macro_name_lookup(state, name_literal):
        m = pm.match(L(pm.Star('x'))).attempt_match(name_literal)
        assert m is not None
        return lookup_built_in_macro(m['x'])

    def do_call_macro(state, built_in_macro, args):
        built_in_macro(state.machine, state.stack_man, *args)

    tag_dispatch = {
        'env_begin' : do_env_begin,
        'env_end' : do_env_end,
        'env_declare' : do_env_declare,
        'env_set' : do_env_set,
        'env_get' : do_env_get,
        'outer_env_get' : do_outer_env_get,
        'arguments' : do_argument_lookup,
        'allocate_local' : do_allocate_local,
        'free_local' : do_free_local,
        'free_local_on_env_exit' : do_free_local_on_env_exit,
        'name' : do_macro_name_lookup,
        'call_builtin' : do_call_macro,
    }

    def default_dispatch(tag, args):
        res = tuple([tag] + list(args))
        raise ValueError('unknown expression : %s' % str(res))

    def dispatch(state, tag, args):
        if tag in tag_dispatch:
            return tag_dispatch[tag](state, *args)
        else:
            return default_dispatch(tag, args)

    def eval_expr(state, expr):
        m = pm.match(L(pm.Star('x'))).attempt_match(expr)
        if m is not None:
            return L(m['x'])
        else:
            m = pm.match(pm.Cons(pm.Star('head'), pm.Star('tail'))).attempt_match(expr)
            assert m is not None
            args = [eval_expr(state, x) for x in m['tail']]
            return dispatch(state, m['head'], args)
    
    statements = expression.get_macro_statements(macro)
    for expr in statements:
        eval_expr(state, expr)

    print(formatted_code(state.machine.code))

def formatted_code(code):
    code = ''.join(code)
    line_width = 70
    lines = []
    while len(code) > line_width:
        lines.append(code[:line_width])
        code = code[line_width:]
    if code:
        lines.append(code)
    return ''.join(list(map(lambda s : s + '\n', lines)))


