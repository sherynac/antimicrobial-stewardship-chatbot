from owlready2 import *
import os

# Build correct path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ontology_path = os.path.join(BASE_DIR, "FinalOntology.owl")

# Load ontology
onto = get_ontology(f"file://{ontology_path}").load()

# Run reasoner
with onto:
    sync_reasoner()

print("Reasoning complete!")

# 🔍 Test: get Dynadoxy
Dynadoxy = onto.search_one(iri="*Dynadoxy*")

print("Individual:", Dynadoxy)

# Check side effects
if Dynadoxy:
    print("Side Effects:", list(Dynadoxy.hasSideEffect))
else:
    print("Dynadoxy not found.")

for ind in onto.individuals():
    print(ind, list(ind.hasSideEffect))

print(list(onto.object_properties()))