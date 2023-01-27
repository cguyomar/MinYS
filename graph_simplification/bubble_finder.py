#!/usr/bin/env python3

"""
Find (super) bubbles in a gfa graph
"""

import argparse

from genome_graph import genome_graph
from genome_graph import *

input_graph = "../test_data/bubble.gfa"
input_graph= "Vl.APSE_all.81_200_400_71_100.simplified.gfa"
g = genome_graph.GenomeGraph.read_gfa(input_graph)


S = set()
seen = set()
visited = set()

class Bubble:
    def __init__(self,g,s,t):
        self.s = s
        self.t = t

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
        )
        return res


def name(n,g=g):
    return(g.nodes[n].nodeName)

def find_bubble_from_node(g,v):
    S = set()
    seen = set()
    visited = set()

    S.add(v)
    while len(S) != 0:
        n = S.pop()
        visited.add(n)
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
            # print("I have found a bubble :")
            # print(g.nodes[abs(v)].nodeName + " / " + str(v))
            # print(g.nodes[abs(t)].nodeName + " / " + str(t))
            # print("Visited nodes : ")
            print(visited)
            b = Bubble(g,v,t)
            print(b)




for v in g.nodes.keys():
    print(v)
    find_bubble_from_node(g,v)
    find_bubble_from_node(g,-v)
   

