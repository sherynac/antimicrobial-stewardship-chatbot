from rdflib import Graph
from owlready2 import get_ontology

def load_ontology():
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
    return onto
