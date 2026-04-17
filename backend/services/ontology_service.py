from rdflib import Graph
from owlready2 import get_ontology
<<<<<<< HEAD
from services.response_service import build_text_response
from utils.helpers import add_space_to_pascal_case
=======
>>>>>>> main

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

def query_ontology(ontology, entity):
    '''
    Queries ontology for an entity and if it cannot be found returns an error message

    Returns:
        entity.obj : retrieved object from the ontology
    '''

    entity_obj = ontology.search_one(iri=f"*{entity}")

    if not entity_obj:  
        return build_text_response(f"Apologies. I couldn't find any information on {entity} in my knowledge base.")

    return entity_obj

def get_indication_severity_type (indication):
    severity_obj = indication.is_a
    severity = severity_obj[0].name
    disease_type_obj = severity_obj[0].is_a
    disease_type = disease_type_obj[0].name

    cleaned_disease_type = disease_type.replace("Disease", "")

    if "NotSpecified" in severity:
        return None, add_space_to_pascal_case(disease_type)

    if disease_type in severity:
        extracted_severity = severity.replace(disease_type, "")
    else:
        extracted_severity = severity
    
    return extracted_severity, add_space_to_pascal_case(cleaned_disease_type)
