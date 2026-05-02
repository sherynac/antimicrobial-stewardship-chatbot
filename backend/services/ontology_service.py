import owlready2
from rdflib import Graph

from owlready2 import get_ontology, sync_reasoner_hermit
from owlready2 import get_ontology
from services.helpers import add_space_to_pascal_case
from typing import Optional


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
    print ("ONTO: ",onto)
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

def find_entities(onto, entity_name: str) -> list[str]:
    """Find all instances including subclasses"""
    entities = []
    entity_class = onto.search_one(iri="*#" + entity_name)

    if entity_class:
        for entity in entity_class.instances():
            entity_name_clean = str(entity).split(".")[-1]
            entities.append(entity_name_clean)
    return sorted(set(entities))

def get_indication_severity_type(onto, indication):
    indication_name = indication.is_a
    severity = indication.hasSeverity
    disease_type = indication_name[0].is_a
    
    indication_name = add_space_to_pascal_case(indication_name[0].name)
    severity_name = add_space_to_pascal_case(severity[0].name)
    disease_type = add_space_to_pascal_case(disease_type[0].name)
    disease_type = disease_type.replace("Disease", "")
    
    if "Not Specified" in severity_name:
        return indication_name, None, disease_type
    
    return indication_name, severity_name, disease_type

def get_brand_info_details (presentation_obj):
    brand_info = []
    for presentation in presentation_obj:
        presentation_name, dosage, unit_price =  get_presentation_details(presentation)
        row = [presentation_name, dosage, f"Php {unit_price}"]
        brand_info.append(row)
    return brand_info

def get_presentation_details(presentation_obj):
    presentation = presentation_obj.is_a
    dosage = presentation.hasDosage
    unit_price = presentation.hasUnitPrice
    return add_space_to_pascal_case(presentation[0].name), dosage[0], unit_price[0]
