import graph2
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

graph = Graph()

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

#############
# a()
# a()
# graph.tweak('c', 10, 1)
# a()

def simulate():
    print(a())
    
    with Layer() as l:
        graph.tweak('d', -1)
        print(a())
    
    print(a())
    
    with l:
        print(a())
        graph.tweak('c', 8, 1)
        print(a())
    
    with Layer():
        graph.tweak('d', 4)
        print(a())
    print(a())
    

@dag
def layer():
    # x = f()
    with Layer() as l:
        graph.tweak('d', 3)
        return l
    
@dag
def g():
    with layer():
        return a()

@dag
def g2():
    with layer():
        graph.tweak('f', 10)
        return a()

def gsim12():
    graph.clear()
    print(a())
    print(g())
    print(a())
    print(g2())
    
def gsim21():
    graph.clear()
    print(a())
    print(g2())
    print(a())
    print(g())

class FLayer:
    def __init__(self):
        self.graphBefore = dictDeepCopy(graph.nodes)
        self.graph = graph.nodes
        self.frozen = False
        
    def __enter__(self):
        graph.nodes = self.graph
        return self

    def __exit__(self, exc_ty, exc_v, exc_tb):
        if not self.frozen:
            self.frozen = True
            self.tweaks = graph.tweaks.copy()
        else:
            if self.tweaks != graph.tweaks:
                raise Exception('Frozen layer!')
        graph.nodes = self.graphBefore


@dag
def flayer():
    # x = f()
    with FLayer() as l:
        graph.tweak('d', 3)
        return l
    
@dag
def fg():
    with flayer():
        return a()

@dag
def fg2():
    with flayer():
        graph.tweak('f', 10)
        return a()


def fgsim12():
    graph.clear()
    graph.trace_calls = False
    print(a())
    print(fg())
    print(a())
    print(fg2())
    
def fgsim21():
    graph.clear()
    graph.trace_calls = False
    print(a())
    print(fg2())
    print(a())
    print(fg())
