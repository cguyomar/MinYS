'''
Implementation of genome graphs.

Data structure : 
g.nodes : dict to store node attributes (seq, name)

g.edges : adjacency list of the nodes. 
       A negative nodeId indicates that the contig is reversed. In that case, 
       the source is the start of the contig, and the target is the end.

'''

import re
import os
import sys
from .utils import reverse_complement,compare_strings, nw_align, locate_nw_binary
#from alignment import PairAlign
from .paths import Path,setExtend

nwCommand = locate_nw_binary()

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

       def add_node(self,nodeName,nodeSeq,check=True):
              newNode = GenomeNode(nodeSeq,nodeName)

              if check:
                     try:
                            assert newNode not in self.nodes.values()
                     except AssertionError:
                            print("Node " + nodeName + "is already in graph")
                     
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
                     self.rem_edge(nodeId,n)

              for n in self.get_neighbors(-nodeId).copy():
                     self.rem_edge(-nodeId,n)

       def get_neighbors(self,nodeId):
              return(self.edges[nodeId])

       def neighborhood(self,nodeId):
              return(self.get_neighbors(nodeId) | self.get_neighbors(-nodeId))

       def get_node_seq(self,nodeId):
              if nodeId < 0:
                     nodeSeq = reverse_complement(self.nodes[-nodeId].nodeSeq.strip())
              else:
                     nodeSeq = self.nodes[nodeId].nodeSeq.strip()
              return(nodeSeq)
   
           
       @classmethod
       def read_gfa(self,file,check=True):
              
              g = GenomeGraph()
              nodeIds = {}  # Used to retrieve a node Id from a name. Is it useful though?
              nlines = 0
              with open(file) as f:
                     for line in f:
                            nlines += 1
                            if re.match(r"S.*", line):
                                   nodeName = line.split("\t")[1]
                                   nodeSeq = line.split("\t")[2].strip()
                                   g.add_node(nodeName,nodeSeq,check)
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

       def stats(self):
              print("Number of nodes : " + str(self.nNodes()))
              print("Number of edges : " + str(self.nEdges()))

              print("Number of connected components : " + str(len(self.connected_components())))

              totLength = 0
              for n in self.nodes:
                     totLength = totLength + len(self.nodes[n].nodeSeq)
              # Overlaps are not counted in the sequence length
              # Here we assume all nodes have the same overlap
              totLength = totLength - self.nEdges()*self.overlap
              
              print("Total length : " + str(totLength))

       def longest_node(self,nodeIds=[]):
              if nodeIds == []:
                     nodeIds = self.nodes
              maxLen = 0
              for n in nodeIds:
                     seq = self.nodes[n].nodeSeq
                     name = self.nodes[n].nodeName
                     if len(seq) > maxLen:
                            longestNode = n
                            maxLen = len(seq)
              return(longestNode)

       ###########  Graph simplification ###########

       def split_branching_nodes(self,maxLinks):
           # Find nodes with more than maxLinks neighbors, and split the graph by removing the neighbors_sequences
           # (In the case of MinYS, removes gapfilled sequences)

            nbCut = 0
            for comp in self.connected_components():
                for n in comp:
                    if n in self.nodes:
                        print(str(n))
                        neighbors = self.get_neighbors(n).copy()
                        if len(neighbors)>=maxLinks:
                            nbCut += 1
                            for n2 in neighbors:
                                print("\t"+str(n2))
                                self.rem_node(abs(n2))

                                # Should we ensure that the node is a gapfilling?
                                # self.rem_edge(n,n2)
                                # n2Name = self.nodes[n2].nodeName
                                # # Is one of the nodes is a gapfilling, we remove it
                                # # This is specific to MinYS
                                # if re.match(r".*;.*;len_.*_qual.*_median_cov.*",n2Name):
                                #     self.rem_node(n2)
                        neighbors = self.get_neighbors(-n).copy()
                        if len(neighbors)>=maxLinks:
                            nbCut += 1
                            for n2 in neighbors:
                                print("\t"+str(n2))
                                self.rem_node(abs(n2))

                                # self.rem_edge(-n,n2)
                                # n2Name = self.nodes[n2].nodeName
                                # # Is one of the nodes is a gapfilling, we remove it
                                # # This is specific to MinYS
                                # if re.match(r".*;.*;len_.*_qual.*_median_cov.*",n2Name):
                                #     self.rem_node(n2)



       def pop_bubble(self,nodeId):
              n1 = self.get_neighbors(nodeId).copy()
              n2 = self.get_neighbors(-nodeId).copy()

              if len(n1)==len(n2)==1 and n1!=n2: # n1!=n2 to avoid cases of self-looping gapfillings
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
                                   #id = PairAlign(refSeq, nodeSeq, 10, -5, -5)
                                   id = nw_align(refSeq,nodeSeq,nwCommand)
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
                            p = Path(self,node)
                            extendable = p.extend_linear_right(self)
                            while extendable:
                                   extendable = p.extend_linear_right(self)
                            extendable = p.extend_linear_left(self)
                            while extendable:
                                   extendable = p.extend_linear_left(self)
                            abs_nodes = [abs(n) for n in p.nodeIds]
                            visited_nodes.update(abs_nodes)
                            if p.nNodes > 1:
                                   print("Found one linear path of "+str(len(abs_nodes))+" nodes")
                                   p.merge(self)
                     node += 1

       def merge_redundant_gapfillings(self,nodeId,l):

              # Starting from a node, look if an identical part of the adjacent nodes can be merged.
              # - get adjacent sequences
              # - use a l bp window to find potential similar sequences
              # - for each l bp primer, 
              #      - find the position of the first divergence
              #      - create a new node and shorten previous nodes
              
              # Should we only start from a contig node? It makes the program specific to mtg output
              
              neighbors = self.get_neighbors(nodeId).copy()

              # Avoid case where two ends of a sequence are neighbors
              for n in neighbors:
                     if -n in neighbors:  
                            return(0)
              #print(neighbors)

              neighbors_sequences = [self.get_node_seq(node) for node in neighbors]

              # First we look at the first 100bp of each seq
              seqStarts = set()
              for seq in neighbors_sequences:
                     if len(seq)>l: # We require at least l common bp to merge
                            if seq[0:l] not in seqStarts:
                                   seqStarts.add(seq[0:l])

              nbSeq = 0 # Number of different merges
              for seqStart in seqStarts:
                     #print("## Merging nb " + str(nbSeq))
                     ref = ""
                     breakPos = {}
                     toMerge = set()

                     for neighbor in neighbors:
                            nseq = self.get_node_seq(neighbor)
                            
                            if nseq[0:l] == seqStart:
                                   toMerge.add(neighbor)
                                   if len(ref)==0:
                                          ref = nseq
                                          refNode = neighbor
                                   else:
                                          breakPos[neighbor] = compare_strings(ref,nseq)
                     #print(len(breakPos))
                     
                     if len(breakPos)==0:
                            continue

                     # We found a set of redundant sequences
                     nbSeq += 1
                     mergePos = min(breakPos.values())
                     
                     consensus = ref[0:mergePos-1]
                     
                     # Add merged node
                     if nodeId < 0:
                            dir = "L"
                     else :
                            dir = "R"
                     
                     newName = self.nodes[abs(nodeId)].nodeName + "_extended(" + str(nbSeq) + ")_" + dir
                     
                     # print(newName)
                     # Get properties
                     self.add_node(newName,consensus)
                     newId = max(self.nodes.keys())
                     self.add_edge(nodeId,newId)
                     
                     # Create edges to new node
                     for n in toMerge:
                            self.add_edge(newId,n)
                            # print(str(nodeId) + " : " + str(n))
                            self.rem_edge(nodeId,n)

                     # Shorten neighbor nodes and cut edges
                     for n in toMerge:
                            if n > 0:
                                   self.nodes[n].nodeSeq = self.nodes[n].nodeSeq[mergePos-self.overlap-1:] 
                            else:
                                   self.nodes[-n].nodeSeq = self.nodes[-n].nodeSeq[0:-(mergePos-self.overlap-1)] 

       def merge_all_gapfillings(self,l):
              visited_nodes = set()
              node = 1
              while node < self.maxId:
                     if node in self.nodes.keys() and node not in visited_nodes:
                            #print("#### Merging from node : " + str(node))
                            self.merge_redundant_gapfillings(node,l)
                            #print("#### Merging from node : " + str(-node))
                            self.merge_redundant_gapfillings(-node,l)

                            visited_nodes.add(node)
                     node += 1   

       def find_all_paths(self,startNode):
       # Enumerates all possible paths going through a node
              p = Path(self,startNode)
              paths = {p}
              extendedPaths, extended = setExtend(paths,self)
              #print(extended)
              nbExtension = 1
              terminatedPaths = set()
              while len(extendedPaths)>0:

                     paths = set()
                     # Removing terminated non circular paths
                     for p in extendedPaths:
                         if p.extendable != True:
                             terminatedPaths.add(p)
                         else:
                             paths.add(p)
                     extendedPaths, extended = setExtend(paths,self)

              return(terminatedPaths)


       def find_all_cyclic_paths(self,startNode):
       # Enumerates all possible paths going through a node
              p = Path(self,startNode)
              paths = {p}
              extendedPaths, extended = setExtend(paths,self)
              nbExtension = 1
              while extended and len(extendedPaths)<200:
                     print(str(len(extendedPaths))+"\n")
                     nbExtension += 1

                     # There are smarter things to do : we don't need to try to extend the whole set
                     paths = extendedPaths.copy()
                     extendedPaths, extended = setExtend(paths,self)
                     for p in extendedPaths:
                            print(p.nodeIds)
              return(extendedPaths)



       def BFS(self, n):
              res = set()
              visited = [False] * (self.maxId+1) # Nodes are 1-indexed
       
              q = [] 
       
              q.append(abs(n)) 
              visited[abs(n)] = True
       
              while q: 
                     #print(q)
                     s = q.pop(0)
                     res.add(abs(s))
       
                     for i in self.neighborhood(s): 
                            if visited[abs(i)] == False: 
                                   q.append(abs(i)) 
                                   visited[abs(i)] = True
              return(res)
       
       def connected_components(self):
              visited = [False] * (self.maxId+1) # Nodes are 1-indexed
              res = []
              for n in self.nodes:
                     if visited[n] == False:
                            comp = self.BFS(n)
                            for i in comp:
                                   visited[i] = True
                            res.append(comp)
              return(res)
              

