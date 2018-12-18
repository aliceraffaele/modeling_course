# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 11:13:29 2018

@author: Alessandro Zeggiotti
"""

# -------------------------------------------------------------------
# USEFUL MODULES

import math
import random
from gurobipy import *

import networkx as nx
import itertools

# -------------------------------------------------------------------
# FUNCTIONS DEFINITION

# Given a graph, this function idefintifies a set of nodes into a single vertex
def Contraction(graph, nodes):
    V = set()
    for i,j in graph:
        V = V.union({i})
        V = V.union({j})
    new_vertex = max(V) + 1
    # Create a minor of the graph
    minor = {}
    for i,j in graph.keys():
        if i in nodes and j in nodes:
            pass
        elif i in nodes and (j,new_vertex) not in minor.keys():
            minor[j,new_vertex] = graph[i,j]
        elif i in nodes:
            minor[j,new_vertex] += graph[i,j]
        elif j in nodes and (i,new_vertex) not in minor.keys():
            minor[i,new_vertex] = graph[i,j]
        elif j in nodes:
            minor[i,new_vertex] += graph[i,j]
        else:
            minor[i,j] = graph[i,j]
    return minor

# Given a graph, this function finds the value of a minimum odd cut
# T is a datum used during the recursion: it must be initially set equal to "vertices"
def minCutValue(graph, T):
    # Base step
    if T == set():
        return float('inf')
    # Create the graph using the module NETWORKX
    G = nx.DiGraph()
    for (i,j) in graph.keys():
        G.add_edge(i, j, capacity = graph[i,j])
        G.add_edge(j, i, capacity = graph[i,j])
    # Let s and t be two random nodes in T
    s = min(T)
    t = max(T)
    # NETWORKX contains a function that allows to find the minimum s-t cut
    # This function is based on Ford-Fulkerson algorithm
    cut_value, partition = nx.minimum_cut(G,s,t)
    S, S_bar = partition
    if len(S.intersection(T)) % 2 == 1: # if S is T-odd: ...
        return min(cut_value,
                   minCutValue(Contraction(graph, {s,t}), T - {s,t}))
    else:
        return min(minCutValue(Contraction(graph, S), T - S),
                   minCutValue(Contraction(graph, S_bar), T - S_bar))

# Given a set, this function finds all its subsets of a fixed cardinality
def findsubsets(S,m):
    # From ITERTOOLS module
    return set(itertools.combinations(S, m))

# Given a graph and the value of a minimum odd cut, this function finds a minimum odd cut
# QUESTION: This technique expoits "brute force", is it possible to do it in a clever way?
def minCutEdges(graph, cut_value):
    for cardinality in range(1,n,2):
        subsets = findsubsets(vertices, cardinality) # "vertices" is global
                                                     # variable defined later
        for S in subsets:
            # Create the cut
            dS = {}
            for i,j in graph.keys():
                if i in S and j not in S:
                    dS[i,j] = graph[i,j]
                if i not in S and j in S:
                    dS[i,j] = graph[i,j]
            dS_value = sum(dS.values())
            if dS_value == cut_value:
                return dS
    print('No odd cut of value %g has been found' % cut_value)
    return None

# -------------------------------------------------------------------
# MODEL DEFINITION
    
# Create vertices and edges for our example
# The user can choose one among the three following graphs
choice = int(input('1 --> TSP problem\n2 --> Petersen graph\nChoose your favourite example: '))

if choice == 1:
    vertices = {0,1,2,3,4,5}
    edges = {
        (0,1): 5,
        (0,2): 5,
        (0,3): 4,
        (1,4): 2,
        (1,5): 3,
        (2,3): 3,
        (2,5): 8,
        (3,4): 4,
        (4,5): 4}
else:
    vertices = {0,1,2,3,4,5,6,7,8,9}
    edges = {
        (0,1): 1,
        (0,4): 1,
        (0,5): 1,
        (1,2): 1,
        (1,6): 1,
        (2,3): 1,
        (2,7): 1,
        (3,4): 1,
        (3,8): 1,
        (4,9): 1,
        (5,7): 1,
        (5,8): 1,
        (6,8): 1,
        (6,9): 1,
        (7,9): 1
        }

n = len(vertices)

# Create the model
m = Model()
# Suppress the standard output, it would be invoked too many times
m.setParam('OutputFlag', 0)

# Create the variables
vars = {}
for (i,j) in edges.keys():
   vars[i,j] = m.addVar(lb=0, vtype=GRB.CONTINUOUS, name='e[%d,%d]'%(i,j))

# To create the model data structure only once, after variables creation
m.update()

# Add the objective function
m.setObjective(sum(vars[i,j]*edges[i,j] for i,j in edges.keys()), GRB.MINIMIZE)

# Add degree-1 constraint
for i in vertices:
    # Look for the edges incident to i
    neighbors = []
    for j in vertices:
        if (i,j) in edges.keys():
            neighbors.append((i,j))
        elif (j,i) in edges.keys():
            neighbors.append((j,i))
    m.addConstr(sum(vars[i,j] for i,j in neighbors) == 1)

# -------------------------------------------------------------------
# MODEL OPTIMIZATION

while True:
    # Solve the problem
    m.optimize()
    print('\n--------------------------------------------------------------\n')
    solution = m.getAttr('x', vars)
    selected = [(i,j) for i,j in solution.keys() if solution[i,j] != 0]
    print('New incumbent solution: ' + str(selected))
    print('Matching value: %g' % m.objVal)
    print('Checking the presence of rationals...')
    # Find the value of a minimum odd cut
    cut_value = minCutValue(solution, vertices)
    if cut_value < 1:
        # Find the edges of a minimum odd cut
        cut_edges = minCutEdges(solution, cut_value)
        # Add a constraint
        m.addConstr(sum(vars[i,j] for (i,j) in cut_edges.keys()) >= 1)
        print('Minimum odd cut: %g' % cut_value)
        print('Related edges: ' + str(list(cut_edges.keys())) + '. New constraint added.')
    else:
        print('This is a feasible solution!')
        break
