#!/usr/bin/env python3

"""
Remove all connected components of a gfa graph smaller than a threshold
"""

import argparse

from genome_graph import genome_graph


op = argparse.ArgumentParser()
op.add_argument("infile")
op.add_argument("outfile")
op.add_argument("minlength")
opts = op.parse_args()

print("Loading graph")
g = genome_graph.GenomeGraph.read_gfa(opts.infile)

for comp in g.connected_components():
    #print(comp)
    compLength = 0
    for n in comp:
        compLength = compLength + len(g.nodes[n].nodeSeq)  # We should not count the overlaps twice in the length  computation
    if compLength < int(opts.minlength):
        for n in comp:
            g.rem_node(n)

g.write_gfa(opts.outfile)
