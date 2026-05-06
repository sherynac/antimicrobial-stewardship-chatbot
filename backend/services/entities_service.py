from services.ontology_service import ontology_service
from html import entities
from owlready2 import *


def fill_entities():
    entities = defaultdict(list)
    
    antibiotics = ontology_service.find_entities(entity_name= "Antibiotic")
    brands = ontology_service.find_entities(entity_name="Brand")
    side_effect = ontology_service.find_subclasses(entity_name="SideEffect")
    
    substances = []
    for substance_type in ["Drug", "Food", "Beverage"]:
        substances.extend(ontology_service.find_entities(substance_type))

    # get all subclass of Warning and add to entities
    warning = ontology_service.find_subclasses(entity_name="Warning")
    # print("Retrieved warnings from ontology:" + str(warning))
    
    entities['Antibiotic'].extend(antibiotics)
    entities['Brand'].extend(brands)
    entities['SideEffect'].extend(side_effect)
    entities['Substance'].extend(substances)
    entities['Warning'].extend(warning)
    # print(f"Filled entities: {entities}")
    return entities

def look_up_entity(words):
    entities = fill_entities()
    found_entities = {}
    for word in words:
        for entity_type, names in entities.items():
            if word in [name.lower() for name in names]:
                found_entities[word] = entity_type

    # print(f"Found entities: {found_entities}")
    return found_entities