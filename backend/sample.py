from owlready2 import *

onto = get_ontology("./backend/data/sample-ontology.rdf").load()
print(f"Loaded ontology with {len(list(onto.classes()))} classes")

for class_obj in onto.classes():
    print(class_obj)
