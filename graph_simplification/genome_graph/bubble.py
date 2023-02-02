class Bubble:
    def __init__(self,g,s,t,nodes_inside):
        self.g = g
        self.s = s
        self.t = t
        self.nodes_inside = tuple(sorted(list(nodes_inside)))

    def __repr__(self):
        
        if self.s > 0:
            sName = self.g.nodes[self.s].nodeName
        else:
            sName = self.g.nodes[-self.s].nodeName + "_rc"
        
        if self.t > 0:
            tName = self.g.nodes[self.t].nodeName
        else:
            tName = self.g.nodes[-self.t].nodeName + "_rc"
        res = (
            f'Bubble from node {sName}'
            f' to {tName}'
            f' containing nodes {[self.g.nodes[-n].nodeName+"_rc" if n<0 else self.g.nodes[n].nodeName for n in self.nodes_inside]}'
        )
        return res

    def reverse(self):
        # b and b.reverse() are actually equivalent
        return Bubble(
            self.g,
            -self.t,
            -self.s,
            map(lambda x:-x,self.nodes_inside)
            )

    def get_st_nodes(self):
        return((self.s,self.t))

    def get_all_nodes(self):
        return(self.nodes_inside.union(self.get_st_nodes))

    def __eq__(self,other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return(False)

    def __hash__(self):
        return hash((
            self.s,
            self.t,
            self.nodes_inside
        ))
