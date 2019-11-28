#!/usr/bin/env python3

"""
Remove redundant gapfillings in a MindTheGap assembly graph
"""

import argparse

from genome_graph import utils
from genome_graph import genome_graph


op = argparse.ArgumentParser()
op.add_argument("infile")
op.add_argument("outfile")
opts = op.parse_args()

print("Loading graph")
g = genome_graph.GenomeGraph.read_gfa(opts.infile)

print("\n")
print("Statistics of input graph : ")
g.stats()
print("\n")

print("Popping bubbles")
g.pop_all_bubbles()

print("Merging linear paths")
g.merge_all_linear_paths()

print("Merging redundancies")
g.merge_all_gapfillings()

# rerun linear path
print("Merging linear paths")
g.merge_all_linear_paths()

print("\n")
print("Statistics of output graph : ")
g.stats()
print("\n")

g.write_gfa(opts.outfile)
