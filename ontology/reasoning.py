from owlready2 import *
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ontology_path = os.path.join(BASE_DIR, "FinalOntology.owl")  # use .owl

onto = get_ontology(f"file://{ontology_path}").load()

try:
    with onto:
        sync_reasoner()

    print("✅ Ontology is consistent!")

except OwlReadyInconsistentOntologyError:
    print("❌ Ontology is INCONSISTENT!\n")

    print("🔍 Inconsistent classes:")
    for cls in onto.classes():
        if cls in onto.inconsistent_classes():
            print("-", cls) 