from .utils import reverse_complement
from copy import deepcopy
#from pipeline.genome_graph.genome_graph import *

class Path:
    def __init__(self,g,nodeId):
        self.nodes = [g.nodes[abs(nodeId)]]
        self.nodeIds = [nodeId]
        self.nNodes = 1
        self.extendable = True
        # self.circular = False
    
    def is_circular(self,g):
        neighbors = g.edges[self.nodeIds[-1]]
        if self.nodeIds[0] in neighbors:
            return(True)
        else:
            return(False)

    def trim_left(self,g):
        # Removes the first node
        self.nodeIds = self.nodeIds[1:]
        self.nodes = [g.nodes[abs(id)] for id in self.nodeIds]
        self.extendable = True

    def extend_right(self,g):
        lastNode = self.nodeIds[-1]
        neighbors = g.edges[lastNode].copy()
        extendedPaths = set()

        if len(neighbors)>0:
            for neighbor in neighbors:
                if abs(neighbor) not in [abs(n) for n in self.nodeIds]: # Node has not been visited by path
                    rev_neighbors = g.edges[-neighbor]
                    assert -lastNode in rev_neighbors
                    newP = deepcopy(self)
                    newP.nodes.append(g.nodes[abs(neighbor)]) 
                    newP.nodeIds.append(neighbor)
                    newP.nNodes += 1
                    extendedPaths.add(newP)
        if len(extendedPaths) > 0:
            return(extendedPaths)
        else:
            return(False)
            

    def extend_linear_right(self,g):
        lastNode = self.nodeIds[-1]
        neighbors = g.edges[lastNode].copy()
        if len(neighbors)==1:
            neighbor = neighbors.pop()
            if abs(neighbor) not in [abs(n) for n in self.nodeIds]: # Node has not been visited by path
                rev_neighbors = g.edges[-neighbor]
                if rev_neighbors == {-lastNode}:   
                    self.nodes.append(g.nodes[abs(neighbor)]) 
                    self.nodeIds.append(neighbor)
                    self.nNodes += 1
                    return(True)        
        return(False)

    def extend_linear_left(self,g):
        firstNode = self.nodeIds[0]
        neighbors = g.edges[-firstNode].copy()
        if len(neighbors)==1:
            neighbor = neighbors.pop()
            if abs(neighbor) not in [abs(n) for n in self.nodeIds]: # Node has not been visited by path
                rev_neighbors = g.edges[-neighbor] 
                if rev_neighbors == {firstNode}: # In the case of linear Paths, we also check there is no branching in the opposite direction
                    self.nodes.insert(0,g.nodes[abs(neighbor)]) 
                    self.nodeIds.insert(0,-neighbor)
                    self.nNodes += 1
                    return(True)
        return(False)

    def extend_left(self,g):
        # If the path is extendable,  returns a set containing all the extended paths
        firstNode = self.nodeIds[0]
        neighbors = g.edges[-firstNode].copy()
        extendedPaths = set()
        if len(neighbors)>0:
            for neighbor in neighbors:
                if abs(neighbor) not in [abs(n) for n in self.nodeIds]: # Node has not been visited by path
                    rev_neighbors = g.edges[-neighbor]
                    assert firstNode in rev_neighbors
                    newP = deepcopy(self)
                    newP.nodes.insert(0,g.nodes[abs(neighbor)]) 
                    newP.nodeIds.insert(0,-neighbor)
                    newP.nNodes += 1
                    extendedPaths.add(newP)
        if len(extendedPaths) > 0:
            return(extendedPaths)
        else:
            return(False)

    def extend(self,g,dir=0):
        # Try extending a path towards the right, and towards the left if it fails
        extendedPaths = set()
        extended = False
        assert dir in (-1,0,1)

        if dir >= 0:
            extR = self.extend_right(g)
            if extR != False:
                extendedPaths = extR
                # extended = True
                return(extendedPaths)

        if dir <= 0:
            extL = self.extend_left(g)

            if extL != False:
                # extended = True
                extendedPaths = extL
                return(extendedPaths)
        
        self.extendable = False
        return({self})

            


    def getSeq(self,g):
        seq = ''
        for node in self.nodeIds:
            nodeSeq = g.nodes[abs(node)].nodeSeq
            if node < 0:
                nodeSeq = reverse_complement(nodeSeq)
            if seq != '':
                nodeSeq = nodeSeq[g.overlap:]    
            seq = seq + nodeSeq
        return(seq)

    def getName(self,g):
        name = ''
        rev = False
        for node in self.nodeIds:
            nodeName = g.nodes[abs(node)].nodeName
            if node < 0:
                rev = not rev
            if rev:
                nodeName = nodeName + "_Rc"
            if name != '':
                nodeName = "_" + nodeName   
            name = name + nodeName
        return(name)

    def merge(self,g):
        newName = self.getName(g)
        newSeq = self.getSeq(g)
        g.add_node(newName,newSeq)
        newId = g.maxId

        neighbors_left = g.get_neighbors(-self.nodeIds[0])
        for n in neighbors_left:
            g.add_edge(-newId,n)

        neighbors_right = g.get_neighbors(self.nodeIds[-1])
        for n in neighbors_right:
            g.add_edge(newId,n)
        
        for node in self.nodeIds:
            g.rem_node(abs(node))

            
def setExtend(paths,g,dir=0):
    # extends a set of paths
    # dir = 0 : extend in both directions
    # dir = -1/1 : extend to the left/right
    extendedPaths = set()
    extended=False

    for p in paths:
        extension = p.extend(g,dir)
        if len(extension) > 1 or list(extension)[0].extendable == True:
            extended = True

        extendedPaths.update(extension)

    return(extendedPaths,extended)
