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

g.split_branching_nodes(int(opts.maxlinks))




g.write_gfa(opts.outfile)
