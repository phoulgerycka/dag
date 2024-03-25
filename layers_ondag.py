from graph2 import graph, dag
from layers import *
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

def g_then_g2():
    graph.clear()
    print(a()) # 46
    print(g()) # 59
    print(a()) # 46
    print(g2()) # 110
    
def g2_then_g_hm():
    graph.clear()
    print(a()) # 46
    print(g2()) # 110
    print(a()) # 46
    print(g()) # 110

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


def frozen_g_then_g2():
    graph.clear()
    graph.trace_calls = False
    print(a())
    print(fg())
    print(a())
    print(fg2()) # fail
    
def frozen_g2_then_g():
    graph.clear()
    graph.trace_calls = False
    print(a())
    print(fg2()) # fail earlier
    print(a())
    print(fg())
