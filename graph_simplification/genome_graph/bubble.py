class Bubble:
    def __init__(self,g,sId,tId,nodes_inside_ids):
        # We store both the node objects and the node ids (whose sign gives directionality)
        self.g = g
        self.s = self.g.nodes[abs(sId)]
        self.sId = sId
        self.t = self.g.nodes[abs(tId)]
        self.tId = tId
        # sorted tuple to make bubbles hashable :
        self.nodes_inside_ids = tuple(sorted(list(nodes_inside_ids)))
        self.nodes_inside = {g.nodes[abs(id)] for id in nodes_inside_ids}

    def __repr__(self):
        
        if self.sId > 0:
            sName = self.s.nodeName
        else:
            sName = self.s.nodeName + "_rc"
        
        if self.tId > 0:
            tName = self.t.nodeName
        else:
            tName = self.t.nodeName + "_rc"
        res = (
            f'Bubble from node {sName}'
            f' to {tName}'
            f' containing nodes {[self.g.nodes[-n].nodeName+"_rc" if n<0 else self.g.nodes[n].nodeName for n in self.nodes_inside_ids]}'
        )
        return res

    def reverse(self):
        # b and b.reverse() are actually equivalent
        return Bubble(
            self.g,
            -self.tId,
            -self.sId,
            tuple(sorted(list(map(lambda x:-x,self.nodes_inside_ids))))
            )

    def is_included(self,other):
        # Return if the bubble is included in another
        # i.e. it's seed and target are nodes of the other
        # it's not necessary to check directionality
        if (self.s in other.nodes_inside and
            self.t in other.nodes_inside):
            return(True)
        else:
            return(False)

    def __eq__(self,other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return(False)

    def __hash__(self):
        return hash((
            self.sId,
            self.tId,
            self.nodes_inside_ids
        ))