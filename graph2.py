import ast
import inspect
import time
import itertools
from frozendict import frozendict
from IPython.display import display
import graphviz
import inspect
from collections import namedtuple
from typing import Dict, List
from matplotlib import pyplot as plt



GNode = namedtuple('GNode', ['value', 'children'])
GNodeKey = namedtuple('GNodeKey', ['func', 'args', 'kwargs'])

class Graph:
    def __init__(self):
        self.nodes: Dict[GNodeKey, GNode] = {}
        self.tweaks : Dict[GNodeKey, bool] = {}
        self.func_defs: Dict[str, str] = {}
        self.trace_calls = True
            
    def set_node(self, k: GNodeKey, n: GNode):
        self.nodes[k] = n
        
    def is_node(self, func_name: str):
        return func_name in self.func_defs
    
    def get_node(self, k: GNodeKey):
        return self.nodes.get(k)
    
    def clear(self):
        self.nodes = {}
        self.tweaks = {}
    
    def add_func_def(self, func_name: str, source: str):
        self.func_defs[func_name] = source
        
    def tweak(self, func_name, val, *args, **kwargs):
        # for simplicity ignore the fact that you could
        # set value with args and kwargs

        # Override
        key = GNodeKey(func_name, args, frozendict(kwargs))
        node = GNode(val, [])
        self.set_node(key, node)
        self.tweaks[key] = True
        
        # Invalidate ancesters
        ancesters = self._get_ancesters(key)
        for a in ancesters:            
            self.invalidate(a)
            
    def invalidate(self, k: GNodeKey):
        del self.nodes[k]
        
    def get_edges(self):
        return list(itertools.chain.from_iterable(
            self._get_edges_for_node(*x) for x in self.nodes.items()))
    def _get_edges_for_node(self, k: GNodeKey, n: GNode):
        return [(k, x) for x in n.children]
    
    def _get_ancesters(self, k: GNodeKey):
        parents = [p_k for p_k, p_n in self.nodes.items() if k in p_n.children]

        return parents + list(itertools.chain.from_iterable(self._get_ancesters(x) for x in parents))
    
graph = Graph()

################

class Parser(ast.NodeVisitor):
    def __init__(self):
        self.dependency = []

    def generic_visit(self, node):        
        if type(node).__name__ == 'Call':
            print(node)
            print(node.args)
            args = tuple(x.value for x in node.args)
            kwargs = frozendict((kw.arg, kw.value.value) for kw in node.keywords)
            if hasattr(node.func, 'id'):
                self.dependency.append(GNodeKey(node.func.id, args, kwargs))
      
        ast.NodeVisitor.generic_visit(self, node)
       
################

def dag(func):    
    p = Parser()
    source = inspect.getsource(func)
    tree = ast.parse(source)
    p.visit(tree)
    func_name = tree.body[0].name

    def f(*args, **kwargs):
        key = GNodeKey(func_name, args, frozendict(kwargs))
        cached_node = graph.get_node(key)
        if cached_node:
            return cached_node.value
        if graph.trace_calls:
            print('Calling: {}, args={}, kwargs={}'.format(func_name, args, kwargs))
            
        graph.add_func_def(func_name, source)
        value = func(*args, **kwargs)
        children = [x for x in p.dependency if graph.is_node(x.func)]
        node = GNode(value, children)
        graph.set_node(key, node)
        return value

    return f

################

def off_graph_func():
    print('Going off graph')
    return 1

def expensive_function(x):
    print('Expensive {}'.format(x))
    time.sleep(1)
    return x

@dag
def a():
    return b(x=3) + c(1) ** 2 + off_graph_func()

@dag
def b(x=2):
    return x * x

@dag
def c(x):
    if d() > 0:
        return x * e()
    else:
        return x * f()

@dag
def d():
    return 5

@dag
def e():
    return expensive_function(6)

@dag
def f():
    return expensive_function(7)

#############

def sim():
    print(a())
    print(a())
    
    graph.tweak('c', 10, 1)
    print(c(1))
    print(a())
