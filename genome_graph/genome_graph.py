'''
Implementation of genome graphs.

Data structure : 
g.nodes : dict to store node attributes (seq, name)

g.edges : adjacency list of the nodes. 
       A negative nodeId indicates that the contig is reversed. In that case, 
       the source is the start of the contig, and the target is the end.

'''

import re
from pipeline.genome_graph.utils import reverse_complement,compare_strings
from pipeline.genome_graph.SequenceAlignment import NeedlemanWunsch
from pipeline.genome_graph.paths import LinearPath

class GenomeNode:

       def __init__(self,nodeSeq,nodeName):
              # self.nodeId = nodeId
              self.nodeSeq = nodeSeq
              self.nodeName = nodeName
              # self.active = True  # Alternative way to remove nodes ?
       
       def __eq__(self, other):
              if isinstance(other, GenomeNode):
                     return self.nodeSeq == other.nodeSeq and self.nodeName == other.nodeName 
              return False

       def __ne__(self, other):
              return not self.__eq__(other)

       def __hash__(self):
              return hash((self.nodeSeq, self.nodeName))

class GenomeGraph:

       def __init__(self):
              self.nodes = {}
              self.edges = {}
              self.overlap = 0
              self.maxId = 0

       def nNodes(self):
              return(len(self.nodes))
       
       def nEdges(self):
              return(len([j for i in self.edges.values() for j in i])/2)

       def add_node(self,nodeName,nodeSeq):
              newNode = GenomeNode(nodeSeq,nodeName)
              try:
                     assert newNode not in self.nodes.values()
              except AssertionError:
                     print("Node already in graph")
                     
              if len(self.nodes)>0:
                     self.maxId = self.maxId+1
                     nodeId = self.maxId
              else: 
                     nodeId = 1
                     self.maxId = 1
              self.nodes[nodeId] = newNode
              self.edges[nodeId] = set()
              self.edges[-nodeId] = set()

       def add_edge(self,n1,n2):
              self.edges[n1].add(n2)
              self.edges[-n2].add(-n1)

       def rem_edge(self,n1,n2):
              try:
                     self.edges[n1].remove(n2)
                     self.edges[-n2].remove(-n1)
              except KeyError:
                     print("Edge not in graph")
              
       def rem_node(self,nodeId):
              try:
                     self.nodes.pop(nodeId)
              except KeyError:
                     print("Node not in graph")

              for n in self.get_neighbors(nodeId).copy():
                     self.rem_edge(-n,-nodeId)

              for n in self.get_neighbors(-nodeId).copy():
                     self.rem_edge(-n,nodeId)

              self.edges.pop(nodeId)
              self.edges.pop(-nodeId)

       def get_neighbors(self,nodeId):
              return(self.edges[nodeId])

       def get_node_seq(self,nodeId):
              if nodeId < 0:
                     nodeSeq = reverse_complement(self.nodes[-nodeId].nodeSeq.strip())
              else:
                     nodeSeq = self.nodes[nodeId].nodeSeq.strip()
              return(nodeSeq)
   
           
       @classmethod
       def read_gfa(self,file):
              
              g = GenomeGraph()
              nodeIds = {}  # Used to retrieve a node Id from a name. Is it useful though?
              nlines = 0
              with open(file) as f:
                     for line in f:
                            nlines += 1
                            if re.match(r"S.*", line):
                                   nodeName = line.split("\t")[1]
                                   nodeSeq = line.split("\t")[2].strip()
                                   g.add_node(nodeName,nodeSeq)
                                   nodeIds[nodeName] = g.nNodes()
                            elif re.match(r"L.*",line):
                                   startName,startDir,endName,endDir,overlap = line.split("\t")[1:]
                                   
                                   if g.overlap == 0:
                                          overlap = int(overlap.replace('M\n',''))
                                          g.overlap = overlap
                                   
                                   startNode = nodeIds[startName]
                                   endNode = nodeIds[endName]

                                   if startDir == "-":
                                          startNode = - startNode
                                   if endDir == "-":
                                          endNode = - endNode

                                   g.add_edge(startNode,endNode)                                  
              return(g)     

       def write_gfa(self,filename):
              overlap = str(self.overlap) + "M"
              with open(filename,"w") as f:
                     for node in self.nodes.values():
                            f.write("S\t"+node.nodeName+"\t"+node.nodeSeq+"\n")
                     written_edges = set()
                     for src_id in self.nodes.keys():
                            src_name = self.nodes[abs(src_id)].nodeName
                            for dst_id in self.edges[src_id]:
                                   if (src_id,dst_id) not in written_edges:
                                          dst_name = self.nodes[abs(dst_id)].nodeName
                                          if dst_id > 0:
                                                 f.write("L\t"+src_name+"\t+\t"+dst_name+"\t+\t"+overlap+"\n")
                                          else:
                                                 f.write("L\t"+src_name+"\t+\t"+dst_name+"\t-\t"+overlap+"\n")
                                          written_edges.add((src_id,dst_id))
                                          written_edges.add((-dst_id,-src_id))
                            for dst_id in self.edges[-src_id]:
                                   if (-src_id,dst_id) not in written_edges:
                                          dst_name = self.nodes[abs(dst_id)].nodeName
                                          if dst_id > 0:
                                                 f.write("L\t"+src_name+"\t-\t"+dst_name+"\t+\t"+overlap+"\n")
                                          else:
                                                 f.write("L\t"+src_name+"\t-\t"+dst_name+"\t-\t"+overlap+"\n")
                                          written_edges.add((-src_id,dst_id))
                                          written_edges.add((-dst_id,src_id))


       ###########  Graph simplification ###########

       def pop_bubble(self,nodeId):
              n1 = self.get_neighbors(nodeId).copy()
              n2 = self.get_neighbors(-nodeId).copy()

              if len(n1)==len(n2)==1:
                     r = self.get_neighbors(-n1.pop())
                     l = self.get_neighbors(-n2.pop())
                     assert -nodeId in r and nodeId in l

                     r_rev = {-i for i in r}

                     inter = l & r_rev
                     assert nodeId in inter

                     if len(inter)>0:
                            toRemove = self.compare_nodes(inter)
                            for node in toRemove:
                                   self.rem_node(abs(node))

       def pop_all_bubbles(self):
              for node in list(self.nodes):
                     if node in self.nodes.keys():
                            self.pop_bubble(node)
              


       def compare_nodes(self,nodeSet):
              uniq = set()
              remove = set()
              for node in nodeSet:
                     nodeSeq = self.get_node_seq(node) # Gets rc if node<0
                            
                     if node in uniq:
                            continue
                     foundmatch = False
                     for refNode in uniq:
                            refSeq =  self.get_node_seq(refNode)
                            if refSeq == nodeSeq:
                                   remove.add(node)
                                   foundmatch = True
                            else:
                                   nw = NeedlemanWunsch(refSeq, nodeSeq, 10, -5, -5)
                                   id = nw.getIdentity()
                                   if id > 0.95:
                                          remove.add(node)
                                          foundmatch = True
                     if not foundmatch:
                            uniq.add(node)
              return(remove)
       
       def merge_all_linear_paths(self):
              visited_nodes = set()
              node = 1
              while node < self.maxId:
                     if node in self.nodes.keys() and node not in visited_nodes:
                            p = LinearPath(self,node)
                            extendable = p.extend_right(self)
                            while extendable:
                                   extendable = p.extend_right(self)
                            extendable = p.extend_left(self)
                            while extendable:
                                   extendable = p.extend_left(self)
                            abs_nodes = [abs(n) for n in p.nodeIds]
                            visited_nodes.update(abs_nodes)
                            if p.nNodes > 1:
                                   print("Found one linear path of "+str(len(abs_nodes))+" nodes")
                                   p.merge(self)
                     node += 1

       def merge_redundant_gapfillings(self,nodeId):

              # Starting from a node, look if an identical part of the adjacent nodes can be merged.
              # - get adjacent sequences
              # - use a 100bp window to find potential similar sequences
              # - for each 100bp primer, 
              #      - find the position of the first divergence
              #      - create a new node and shorten previous nodes
              
              # Should we only start from a contig node? It makes the program specific to mtg output
              
              neighbors = self.get_neighbors(nodeId)
              neighbors_sequences = [self.get_node_seq(node) for node in neighbors]

              seqStarts = set()
              for seq in neighbors_sequences:
                     if seq[0:100] not in seqStarts:  # What if length <100?
                            seqStarts.add(seq[0:100])

              nbSeq = 0 # Number of different merges
              for seqStart in seqStarts:
                     ref = ""
                     refNode = 0
                     breakPos = {}

                     for neighbor in neighbors:
                            nseq = self.get_node_seq(neighbor)
                            if nseq[0:100] == seqStart:
                                   if len(ref)==0:
                                          ref = nseq
                                          refNode = neighbor
                                   else:
                                          breakPos[neighbor] = compare_strings(ref,nseq)
                     print(len(breakPos))
                     if len(breakPos)==0:
                            continue
                     mergePos = min(breakPos.values())
                     
                     consensus = ref[0:mergePos]
                     
                     # Add merged node
                     if nodeId < 0:
                            dir = "L"
                     else :
                            dir = "R"
                     
                     newName = self.nodes[nodeId].nodeName + "_extended_" + dir
                     #self.add_node()


                     return(mergePos)

g = GenomeGraph.read_gfa("pipeline/genome_graph/data/simple4.gfa")
g.pop_all_bubbles()
g.merge_all_linear_paths()

g.merge_redundant_gapfillings(1)                                          