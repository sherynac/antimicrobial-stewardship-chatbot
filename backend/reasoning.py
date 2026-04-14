# Python with reasoning
from owlready2 import *
from rdflib import Graph

# Load Turtle file
g = Graph()
g.parse("./backend/data/reasoning.ttl", format="turtle")

# Save as RDF/XML (.owl)
g.serialize(destination="./backend/data/reasoning.owl", format="xml")


onto = get_ontology("./backend/data/reasoning.owl").load()
sync_reasoner()

doxycycline = onto.search_one(iri="*Doxycycline*")

print(doxycycline)
print(doxycycline.hasSideEffect)