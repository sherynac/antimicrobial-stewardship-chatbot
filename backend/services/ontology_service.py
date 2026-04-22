from rdflib import Graph
from owlready2 import get_ontology, sync_reasoner_hermit
from services.response_service import build_text_response, build_reference, build_reference_list
from utils.helpers import add_space_to_pascal_case

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
    with onto:
        sync_reasoner_hermit()

    return onto

def query_ontology(ontology, entity):
    '''
    Queries ontology for an entity and if it cannot be found returns an error message

    args:
        entity : name of object to be retrieved from the ontology
    
    Returns:
        result : retrieved object from ontology with same entity name
    '''

    result = ontology.search_one(label=entity)
    print(result)

    if not result:  
        raise ValueError(f"I'm sorry I don't have any records for {entity}")

    return result

def get_references_list(entities):
    '''
    Building a reference list from an iterable object
    '''
    references = []
    for entity in entities:
        references_obj = entity.hasReference
        for reference in references_obj:
            title, url = get_reference_details(reference)
            reference_json = build_reference(reference.name, title, url)
            references.append(reference_json)
    
    reference_list = build_reference_list(references)
    return reference_list

def get_single_reference(entity):
    references = []
    references_obj = entity.hasReference
    for reference in references_obj:
        title, url = get_reference_details(reference)
        reference_json = build_reference(reference.name, title, url)
        references.append(reference_json)
    
    reference_list = build_reference_list(references)
    return reference_list

def get_reference_details(reference_obj):
    '''
    Returns title and url of a reference
    '''
    reference_url = reference_obj.retrievedFrom
    reference_title = reference_obj.hasReferenceTitle

    return reference_title[0], reference_url[0]

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
