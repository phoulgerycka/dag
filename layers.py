from graph2 import graph, dag, GNode
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

def dictDeepCopy(d):
    return {k : GNode(v.value, v.children) for k, v in d.items()}

class Layer:
    def __init__(self):
        self.graphBefore = dictDeepCopy(graph.nodes)
        self.graph = graph.nodes
        
    def __enter__(self):
        graph.nodes = self.graph
        return self

    def __exit__(self, exc_ty, exc_v, exc_tb):
        graph.nodes = self.graphBefore
        
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
    if d() > 4:
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
    return (-expensive_function(7))

def simulate():
    graph.clear()
    print(a()) # 46
    
    with Layer() as l:
        graph.tweak('d', -1)
        print(a()) # 59 inside layer
    
    print(a()) # 46 outside layer
    
    with l:
        print(a()) # 59 back inside layer
        graph.tweak('c', 8, 1)
        print(a()) # 74 inside layer
    
    with Layer():
        graph.tweak('d', 4)
        print(a()) # 59 inside different layer
    print(a()) # 46 outside the second layer too
