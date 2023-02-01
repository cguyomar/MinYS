#!/usr/bin/env python3

"""
Find (super) bubbles in a gfa graph
"""

import argparse

from genome_graph import genome_graph
from genome_graph import *

input_graph = "../test_data/bubble.gfa"
# input_graph= "Vl.APSE_all.81_200_400_71_100.simplified.gfa"
g = genome_graph.GenomeGraph.read_gfa(input_graph)


S = set()
seen = set()
visited = set()

class Bubble:
    def __init__(self,g,s,t,nodes_inside):
        self.s = s
        self.t = t
        self.nodes_inside = nodes_inside

    def __repr__(self):
        
        if self.s > 0:
            sName = g.nodes[self.s].nodeName
        else:
            sName = g.nodes[-self.s].nodeName + "_rc"
        
        if self.t > 0:
            tName = g.nodes[self.t].nodeName
        else:
            tName = g.nodes[-self.t].nodeName + "_rc"
        res = (
            f'Bubble from node {sName}'
            f' to {tName}'
            f' containing nodes {[g.nodes[-n].nodeName+"_rc" if n<0 else g.nodes[n].nodeName for n in self.nodes_inside]}'
        )
        return res


def name(n,g=g):
    return(g.nodes[n].nodeName)

def find_bubble_from_node(g,v):
    S = set()
    seen = set()
    visited = set()
    nodes_inside = set()

    S.add(v)
    while len(S) != 0:
        n = S.pop()
        visited.add(n)
        nodes_inside.add(n)
        if n in seen:
            seen.remove(n)
      
        if len(g.get_neighbors(n)) == 0:
            # tip
            break
        for u in g.get_neighbors(n):
            if u == v:
                # cycle
                break
            seen.add(u)

            u_parents = {-x for x in g.get_neighbors(-u)}

            if u_parents.issubset(visited):
                S.add(u)

        if len(S)==1 and len(seen)==1:
            t = S.pop()
            nodes_inside.remove(v)
            # print("I have found a bubble :")
            # print(g.nodes[abs(v)].nodeName + " / " + str(v))
            # print(g.nodes[abs(t)].nodeName + " / " + str(t))
            # print("Visited nodes : ")
            print(visited)
            b = Bubble(g,v,t,nodes_inside)
            print(b)




for v in g.nodes.keys():
    # print(v)
    find_bubble_from_node(g,v)
    find_bubble_from_node(g,-v)
   

