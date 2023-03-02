#!/usr/bin/env python3

"""
Find (super) bubbles in a gfa graph
"""

import argparse
import sys

from genome_graph import genome_graph
from genome_graph import *


if __name__ == '__main__':
    op = argparse.ArgumentParser()
    op.add_argument("graph")
    op.add_argument("out")
    opts = op.parse_args()

    g = genome_graph.GenomeGraph.read_gfa(opts.graph)

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

    print(f'Kept {len(bubbles)} super-bubbles')

    # Create a subgraph for each bubble
    # And find all paths in those

    print("Enumerating paths in bubble :")
    for b_id,b in enumerate(bubbles):
        print(b)
        bubble_nodes = set(b.nodes_inside_ids)
        bubble_nodes.add(b.sId)
        bubble_nodes.add(b.tId)
      
        subg = g.subgraph(bubble_nodes)

        paths = subg.find_all_paths(b.sId,dir=1)
        print(f'Found {len(paths)} paths in bubble')
        to_compare = set()
        for p_id,p in enumerate(paths):
            # print(g.get_neighbors(p.nodeIds[len(p.nod eIds)-1]))d alongside the results directory:
            p.trim_left(g)
            # print(g.get_neighbors(p.nodeIds[len(p.nod eIds)-1]))
            # print([g.nodes[abs(nId)].nodeName for nId in p.nodeIds]) 
            # Add a new node for each path
            newNodeId = "bubble_" + str(b_id) + "_path_" + str(p_id)
            g.add_node(
                newNodeId,
                p.getSeq(subg),
                True
            )
            to_compare.add(g.maxId) # The last added node always has maxId as Id
            # Link the new node to the rest of the graph
            g.add_edge(b.sId,-g.maxId)
            g.add_edge(-b.tId,g.maxId)
        # Remove the bubble nodes now that we have the path nodes
        for n in set(b.nodes_inside_ids):
            g.rem_node(abs(n))

        # Compare paths : 
        to_remove = g.compare_nodes(to_compare)
        print(f"Removing {len(to_remove)} redundant paths")
        for n in to_remove:
            g.rem_node(n)
    
    g.merge_all_linear_paths()

    g.write_gfa(opts.out)

