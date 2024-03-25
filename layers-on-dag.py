import graph2
import layers
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
