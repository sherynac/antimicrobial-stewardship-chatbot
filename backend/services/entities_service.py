from services.ontology_service import ontology_service
from html import entities
from owlready2 import *


def fill_entities():
    entities = defaultdict(list)
    
    antibiotics = ontology_service.find_entities(entity_name= "Antibiotic")
    brands = ontology_service.find_entities(entity_name="Brand")
    side_effect = ontology_service.find_entities(entity_name="SideEffect")
    
    ## For side effects, we want to get the class names instead of the instance names
    
    # side_effects = []
    # for side_effect_instance in side_effect:
    #     side_effect_class = side_effect_instance.is_a
    #     side_effect_class_name = side_effect_class[0].name
    #     side_effects.append(side_effect_class_name)
    
    substances = []
    for substance_type in ["Drug", "Food", "Beverage"]:
        substances.extend(ontology_service.find_entities(substance_type))

    # warning = ontology_service.find_entities(onto, "Warning")
    
    entities['Antibiotic'].extend(antibiotics)
    entities['Brand'].extend(brands)
    entities['SideEffect'].extend(side_effect)
    entities['Substance'].extend(substances)
    # entities['Warning'].extend(warning)
    # print(f"Filled entities: {entities}")
    return entities

def look_up_entity(words):
    entities = fill_entities()
    found_entities = {}
    for word in words:
        for entity_type, names in entities.items():
            if word in [name.lower() for name in names]:
                found_entities[word] = entity_type

    print(f"Found entities: {found_entities}")
    return found_entities