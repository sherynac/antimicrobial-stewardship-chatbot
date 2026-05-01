import os
from rdflib import Graph
from owlready2 import get_ontology

# Base directory (adjust if needed)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build path to TTL file
ontology_path = os.path.join(BASE_DIR, "FinalOntology.ttl")

# Build path to converted OWL file
owl_path = os.path.join(BASE_DIR, "FinalOntology.owl")

# -------- RDFlib --------
# Convert TTL to OWL XML (rdflib handles Turtle parsing correctly)
g = Graph()
g.parse(ontology_path, format="turtle")
g.serialize(destination=owl_path, format="xml")
 
# -------- Owlready2 --------
# Load the converted OWL file (owlready2 parses OWL XML successfully)
onto = get_ontology(f"file://{owl_path}").load()