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

def a():
    return b() + c()

def b():
    return 2

  
def c():
    return d() + 1

def d():
    return 5

funcs = 'abcd'


class Parser(ast.NodeVisitor):
    def __init__(self):
        self.dependency = []

    def generic_visit(self, node):        
        if type(node).__name__ == 'Call':            
            self.dependency.append(node.func.id)            
        ast.NodeVisitor.generic_visit(self, node)

p = Parser()
p.visit(ast.parse(inspect.getsource(a)))
p.dependency

        
################
        
GraphNode = namedtuple('GraphNode', ['func_name', 'code'])
GraphEdge = namedtuple('GraphEdge', ['node1', 'node2'])

class Graph:
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        
    def add_node(self, node: GraphNode):
        self.nodes[node.func_name] = node
        

    def add_edge(self, edge: GraphEdge):
        self.edges.append(edge)

g = Graph()

for func_name in funcs:
    func = globals()[func_name]
    code = inspect.getsource(func)
    p = Parser()
    p.visit(ast.parse(code))
    g.add_node(GraphNode(func_name, code))
    for dep in p.dependency:        
        g.add_edge(GraphEdge(func_name, dep))
        
g.edges


