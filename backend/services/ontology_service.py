from rdflib import Graph

from owlready2 import get_ontology, sync_reasoner_hermit
from owlready2 import get_ontology


def load_ontology():
    global onto
    '''
    Reads Turtle file (.ttl), converts it to OWL file (.owl), loads the ontology and returns the ontology

    Returns:
        onto: the ontology knowledge base for the AMR chatbot
    '''
    # Load Turtle file
    g = Graph()
    g.parse("./backend/data/sample-ontology.ttl", format="turtle")

    print ("AFTER GRAPH")
    # Save as RDF/XML (.owl)
    g.serialize(destination="./backend/data/sample-ontology.owl", format="xml")

    onto = get_ontology("./backend/data/sample-ontology.owl").load()
    print(f"Loaded ontology with {len(list(onto.classes()))} classes")
    with onto:
        sync_reasoner_hermit()

    return onto

def query_ontology(onto, entity):
    result = onto.search_one(iri="*" + entity)
    if result:
        return result
    else:
        raise ValueError(f"Entity '{entity}' not found in the ontology.")

def find_entities(onto, entity_name):
    """Find all instances including subclasses"""
    entities = []
    entity_class = onto.search_one(iri="*" + entity_name)

    if entity_class:
        for entity in entity_class.instances():
            entity_name_clean = str(entity).split(".")[-1]
            entities.append(entity_name_clean)
    return sorted(set(entities))

