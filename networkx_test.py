import rdflib
from rdflib import Graph
import networkx as nx
import networkx.algorithms.isomorphism as iso

def print_triples(rdf):
    for s, p, o in rdf:
        print(s, p, o)

def to_rdf_term(str):
    if str.startswith("<"):
        return rdflib.term.URIRef(str[1:-1])
    elif str.startswith("_:"):
        return rdflib.term.BNode(str[2:])
    else:
        return rdflib.term.Literal(str[1:-1])

def convert_rdf_nx(rdf):
    G = nx.DiGraph()
    for s, p, o in rdf:
        G.add_node(s.n3(), term=s)
        G.add_node(o.n3(), term=o)
        G.add_edge(s.n3(), o.n3(), term=p)
    return G

# compare edges on their term
em = iso.categorical_edge_match("term", None)
# consider nodes equal if _both_ its terms are blank nodes; else, compare their terms
nm = lambda n1, n2: True if isinstance(n1['term'], rdflib.term.BNode) and isinstance(n2['term'], rdflib.term.BNode) else n1['term'] == n2['term']

def rdf_graph_matcher(g1, g2):
    return iso.DiGraphMatcher(g1, g2, node_match=nm, edge_match=em)

def subtract_iso_from(isos, rdf):
    for iso in isos:
        for node1 in iso:
            for node2 in iso:
                if node1 != node2:
                    term1 = to_rdf_term(node1)
                    term2 = to_rdf_term(node2)
                    rdf.remove((term1, None, term2))
        break

def get_iso_subgraph(isos, rdf):
    subgraph = Graph()
    for iso in isos:
        for node1 in iso:
            for node2 in iso:
                if node1 != node2:
                    term1 = to_rdf_term(node1)
                    term2 = to_rdf_term(node2)
                    # print("iso:", term1, term2)
                    subgraph += rdf.triples((term1, None, term2))
        break
    return subgraph
    
def rdf_graph_diff(rdf1, rdf2):
    g1 = convert_rdf_nx(rdf1)
    g2 = convert_rdf_nx(rdf2)

    if rdf_graph_matcher(g1, g2).is_isomorphic():
        print("g1, g2 are isomorphic")
        return
    else:
        print("g1, g2 are not isomorphic")

    matcher12 = rdf_graph_matcher(g1, g2)
    if matcher12.subgraph_is_isomorphic():
        print ("> g1 subgraph-iso g2")
        subtract_iso_from(matcher12.subgraph_isomorphisms_iter(), rdf1)
        print("extra triples in g1:")
        print_triples(rdf1)
        # print("iso g1 subgraph:")
        # subgraph = get_iso_subgraph(matcher12.subgraph_isomorphisms_iter(), rdf1)
        # print_triples(subgraph)

    matcher21 = rdf_graph_matcher(g2, g1)
    if matcher21.subgraph_is_isomorphic():
        print ("> g2 subgraph-iso g1")
        subtract_iso_from(matcher21.subgraph_isomorphisms_iter(), rdf2)
        print("extra triples in g2:")
        print_triples(rdf2)
        # print("iso g2 subgraph:")
        # subgraph = get_iso_subgraph(matcher21.subgraph_isomorphisms_iter(), rdf2)
        # print_triples(subgraph)

rdf1 = Graph().parse('test1-simple.ttl', format='ttl')
rdf2 = Graph().parse('test2-simple.ttl', format='ttl')

rdf_graph_diff(rdf1, rdf2)


# for c1 in nx.connected_components(G1):
#     cg1 = G1.subgraph(c1).copy()
#     iso_found = False
#     for c2 in nx.connected_components(G2):
#         cg2 = G2.subgraph(c2).copy()
#         if nx.is_isomorphic(cg1, cg2, node_match=cmp_nodes, edge_match=nm):
#             iso_found = True
#         # else:
#         #     print("not iso:", c1, c2)
#     if not iso_found:
#         print("no iso found:")
#         for cell in [( e, cg1.get_edge_data(*e)) for e in cg1.edges]:
#             print(cell)
#         break

# # G1 = nx.DiGraph()
# G1 = nx.Graph()
# G1.add_edge(5, 6, label="e1")
# G1.add_edge(6, 7, label="e2")
# G1.add_edge(6, 8, label="e3")
# G1.add_edge(10, 11, label="e1")
# G1.add_edge(11, 12, label="e2")
# # G1.add_edge(11, 13, label="e3")

# # G2 = nx.DiGraph()
# G2 = nx.Graph()
# G2.add_edge(1, 2, label="e1")
# G2.add_edge(2, 3, label="e2")
# G2.add_edge(2, 4, label="e3")