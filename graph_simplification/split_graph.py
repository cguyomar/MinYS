#!/usr/bin/env python3

"""
Split connected components when there are more than k edges starting on a node
"""

import argparse

from genome_graph import genome_graph


op = argparse.ArgumentParser()
op.add_argument("infile")
op.add_argument("outfile")
op.add_argument("maxlinks")
opts = op.parse_args()

print("Loading graph")
g = genome_graph.GenomeGraph.read_gfa(opts.infile)

maxLinks = int(opts.maxlinks)

nbCut = 0
for comp in g.connected_components():
    for n in comp:
        neighbors = g.get_neighbors(n).copy()
        if len(neighbors)>=maxLinks:
            nbCut += 1
            for n2 in neighbors:
                g.rem_edge(n,n2)
        neighbors = g.get_neighbors(-n).copy()
        if len(neighbors)>=maxLinks:
            nbCut += 1
            for n2 in neighbors:
                g.rem_edge(-n,n2)

print("Cut edges for "+str(nbCut)+" branching nodes")

g.write_gfa(opts.outfile)
