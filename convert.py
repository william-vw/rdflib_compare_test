from rdflib import Graph

g = Graph()
g.parse("test3.ttl")
g.serialize(destination="test3.xml", format="xml")
