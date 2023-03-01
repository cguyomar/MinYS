from .bubble import Bubble

def find_bubble_from_node(g,v):
    S = set()
    seen = set()
    visited = set()
    nodes_inside = set()
    S.add(v)
    while len(S) != 0:
        n = S.pop()
        visited.add(n)
        nodes_inside.add(n)
        if n in seen:
            seen.remove(n)
      
        if len(g.get_neighbors(n)) == 0:
            # tip
            break
        for u in g.get_neighbors(n):
            if u == -v:
                # cycle
                break
            seen.add(u)

            u_parents = {-x for x in g.get_neighbors(-u)}

            if u_parents.issubset(visited):
                S.add(u)

        if len(S)==1 and len(seen)==1:
            t = S.pop()
            nodes_inside.remove(v)

            b = Bubble(g,v,t,nodes_inside)
            return(b)