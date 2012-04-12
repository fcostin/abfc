"""
limited structural pattern matching
"""

# _match(p, e) convention:
# if the match fails, return none
# otherwise, return a list of (name, value) bindings, if any,
# from the successful match

def _match(p, e):
    if isinstance(p, list) or isinstance(p, tuple):
        return _match_list(p, e)
    elif isinstance(p, str):
        return _match_string(p, e)
    else:
        return _match_obj(p, e)

def _match_list(p, e):
    p = list(p)
    try:
        e = list(e)
    except TypeError:
        return None
    if len(p) != len(e):
        return None
    bindings = []
    for (x, y) in zip(p, e):
        z = _match(x, y)
        if z is None:
            return None
        else:
            bindings += z
    return bindings

def _match_string(p, e):
    assert isinstance(p, str)
    if p == e:
        return []
    else:
        return None

def _match_obj(p, e):
    return p.matches(e)

class Star:
    """
    pattern : match any value, set name to value of match
    """
    def __init__(self, name):
        self.name = name

    def matches(self, e):
        return [(self.name, e)]

class One:
    """
    pattern : match any value, discard it
    """
    def __init__(self):
        pass

    def matches(self, e):
        return []

class Zero:
    """
    pattern : match no value
    """
    def __init__(self):
        pass

    def matches(self, e):
        return None

class Cons:
    # list head | tail destructuring
    def __init__(self, head_pattern, tail_pattern):
        self.head_pattern = head_pattern
        self.tail_pattern = tail_pattern

    def matches(self, e):
        try:
            e = list(e)
        except TypeError:
            return None
        if len(e) == 0:
            return None
        x = _match(self.head_pattern, e[0])
        if x is None:
            return None
        y = _match(self.tail_pattern, e[1:])
        if y is None:
            return None
        return x + y

class Matcher:
    def __init__(self, pattern):
        self.pattern = pattern

    def replace(self, action):
        return MatchReplaceRule(self, action)

    def attempt_match(self, expression):
        m = _match(self.pattern, expression)
        if m is not None:
            m = dict(m)
        return m

class MatchReplaceRule:
    def __init__(self, matcher, action):
        self.matcher = matcher
        self.action = action

    def __call__(self, expression):
        m = self.matcher.attempt_match(expression)
        if m is None:
            return expression
        else:
            return self.action(**m)

def match(pattern):
    return Matcher(pattern)

# XXX test code follows

def demonstrate(rule, s):
    print('%s => %s' % (s, rule(s)))

def test_a():

    pattern = [('local', Star('x'))]
    def foo(x):
        return [('greeting', ('hello', 'world', x))]
    
    rule = match(pattern).replace(foo)

    demonstrate(rule, 'foo')
    demonstrate(rule, ['foo'])
    demonstrate(rule, [('local', )])
    demonstrate(rule, [('local', 'hi', 'ho')])
    demonstrate(rule, [('local', 'violin_tuna')])

def test_b():
    # there have been prettier things
    r = (match(Cons('hello', Cons(Star('x'), Cons(Star('y'), Cons(Star('z'), Cons('dog', One()))))))
            .replace((lambda x,y,z : ['ohai', x, y, z, 'cat']))
    )

    demonstrate(r, 'hello')
    demonstrate(r, 'hello this is dog')
    demonstrate(r, ['hello', 'this', 'is', 'dog'])
    demonstrate(r, ['hello', 'yes', 'this', 'is', 'dog'])
    demonstrate(r, ['hello', 'yes', 'this', 'is', 'cat'])
    demonstrate(r, ['hello', 'i', 'am', 'ceiling', 'dog'])

def main():
    test_a()
    test_b()

if __name__ == '__main__':
    main()


