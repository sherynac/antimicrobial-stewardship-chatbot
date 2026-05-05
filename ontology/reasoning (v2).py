import os
from rdflib import Graph
from owlready2 import get_ontology, sync_reasoner

# =========================
# PATH SETUP
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ttl_path = os.path.join(BASE_DIR, "FinalOntology.ttl")
owl_path = os.path.join(BASE_DIR, "FinalOntology.owl")

# =========================
# STEP 1: TTL → OWL
# =========================
print("Converting TTL → OWL...")
g = Graph()
g.parse(ttl_path, format="turtle")
g.serialize(destination=owl_path, format="xml")

# =========================
# STEP 2: LOAD + REASON
# =========================
print("Loading ontology...")
onto = get_ontology(f"file://{owl_path}").load()

print("Running reasoner...")
with onto:
    sync_reasoner()

print("Reasoning complete!\n")

# =========================
# CONFIG (REPLACE EXISTING)
# =========================
TARGET_ANTIBIOTIC = "Doxycycline"
MAX_DEPTH = None  # No fixed depth limit (set to integer e.g. 5 if you want a cap later)
MAX_ENTITIES = 500  # Optional: Stop after 500 unique entities (remove this line for no limit at all)
# Dynamically fetch ALL has* properties (no hardcoded subsets)
all_obj_props = onto.object_properties()
OBJ_PROPS = [prop.name for prop in all_obj_props if prop.name.startswith("has")]
OBJ_PROPS += ["treats", "managed_as"]  # Add non-has object properties
all_data_props = onto.data_properties()
DATA_PROPS = [prop.name for prop in all_data_props if prop.name.startswith("has")]

# =========================
# HELPER: GET NAME
# =========================
def get_name(entity):
    try:
        if hasattr(entity, "label") and entity.label:
            return entity.label[0]
        return entity.name
    except:
        return str(entity)

# =========================
# TREE PRINTER
# =========================
def print_tree(entity, depth=0, visited=None, entity_count=None):
    if visited is None:
        visited = set()
    if entity_count is None:
        entity_count = [0]  # Mutable counter to track unique entities across recursions
    indent = "  " * depth
    name = get_name(entity)
    # Prevent infinite loops from cyclic relationships (e.g., A → B → A)
    if entity in visited:
        print(f"{indent}↳ {name} (already visited, skipping)")
        return
    visited.add(entity)
    # Optional: Stop if max entity count is reached
    if MAX_ENTITIES is not None and entity_count[0] >= MAX_ENTITIES:
        print(f"{indent}⚠️ Max entity limit reached, stopping traversal")
        return
    entity_count[0] += 1
    # Root formatting
    if depth == 0:
        entity_type = next((cls.name for cls in entity.is_a if cls in onto.classes()), "Unknown")
        print(f"Root: {name} ({entity_type})")
    else:
        print(f"{indent}├─ {name}")
    # DATA PROPERTIES (unchanged)
    for prop in DATA_PROPS:
        vals = getattr(entity, prop, []) if hasattr(entity, prop) else []
        for val in vals:
            print(f"{indent}  ├─ {prop}: {val}")
    # Only enforce depth limit if MAX_DEPTH is set to an integer
    if MAX_DEPTH is not None and depth >= MAX_DEPTH:
        print(f"{indent}  ⚠️ Max depth reached, stopping further traversal from here")
        return
    # OBJECT PROPERTIES (direct + inferred, unchanged)
    for prop in OBJ_PROPS:
        direct_vals = getattr(entity, prop, []) if hasattr(entity, prop) else []
        indirect_prop = f"INDIRECT_{prop}"
        inferred_vals = getattr(entity, indirect_prop, []) if hasattr(entity, indirect_prop) else []
        all_vals = list(set(direct_vals + inferred_vals))
        
        if all_vals:
            print(f"{indent}  ├─ {prop} (direct: {len(direct_vals)}, inferred: {len(inferred_vals)}) →")
            for val in all_vals:
                print_tree(val, depth + 2, visited, entity_count)
                

# =========================
# RUN QUERY
# =========================
print(f"Searching for: {TARGET_ANTIBIOTIC}\n")
target = onto.search_one(iri=f"*{TARGET_ANTIBIOTIC}*")
if target:
    print_tree(target)
else:
    print(f"❌ Antibiotic '{TARGET_ANTIBIOTIC}' not found.")
# Debug: Show inferred properties for the target antibiotic
print("\n=== DEBUG: Inferred/Chain Relationships ===")
if target:
    print(f"Inferred hasSideEffect (INDIRECT_hasSideEffect): {target.INDIRECT_hasSideEffect}")
    print(f"Inferred hasInteraction (INDIRECT_hasInteraction): {target.INDIRECT_hasInteraction}")
    print(f"Direct hasBrandName: {target.hasBrandName}")