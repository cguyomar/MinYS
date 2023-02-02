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

def name(n,g=g):
    return(g.nodes[n].nodeName)

bubbles = g.find_bubbles()

print(f'Found {len(bubbles)} bubbles')

# Remove sub-bubbles
to_remove = set()
for b1 in bubbles:
    for b2 in bubbles:
        if b1.is_included(b2):
            to_remove.add(b1)
            break

for b in to_remove:
    bubbles.remove(b)

print(f'Found {len(bubbles)} bubbles')


   
