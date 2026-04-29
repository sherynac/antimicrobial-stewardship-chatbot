import services.ontology_service as ontology_service
from html import entities
from owlready2 import *

def fill_entities(onto):
    entities = defaultdict(list)
    
    antibiotics = ontology_service.find_entities(onto, "Antibiotic")
    brands = ontology_service.find_entities(onto, "Brand")
    side_effect = ontology_service.find_entities(onto, "SideEffect")
    
    substances = []
    for substance_type in ["Drug", "Food", "Beverage"]:
        substances.extend(ontology_service.find_entities(onto, substance_type))

    # warning = ontology_service.find_entities(onto, "Warning")
    
    entities['Antibiotic'].extend(antibiotics)
    entities['Brand'].extend(brands)
    entities['SideEffect'].extend(side_effect)
    entities['Substance'].extend(substances)
    # entities['Warning'].extend(warning)
    
    return entities

def look_up_entity(onto, words):
    entities = fill_entities(onto)
    found_entities = {}
    for word in words:
        for entity_type, names in entities.items():
            if word in [name.lower() for name in names]:
                found_entities[word] = entity_type

    print(f"Found entities: {found_entities}")
    return found_entities