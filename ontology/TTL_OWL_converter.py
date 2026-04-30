import os
from rdflib import Graph
from owlready2 import get_ontology

# Base directory (adjust if needed)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build path to TTL file
ontology_path = os.path.join(BASE_DIR, "FinalOntology.ttl")

# -------- RDFlib --------
g = Graph()
g.parse(ontology_path, format="turtle")  # use the same path
g.serialize(destination=os.path.join(BASE_DIR, "FinalOntology.owl"), format="xml")

# -------- Owlready2 --------
onto = get_ontology(f"file://{ontology_path}").load()