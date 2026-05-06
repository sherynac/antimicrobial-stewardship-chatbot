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
    print("Retrieved warnings from ontology:" + str(warning))
    
    entities['Antibiotic'].extend(antibiotics)
    entities['Brand'].extend(brands)
    entities['SideEffect'].extend(side_effect)
    entities['Substance'].extend(substances)
    entities['Warning'].extend(warning)
    # print(f"Filled entities: {entities}")
    return entities

def look_up_entity(words, original_text=""):
    entities = fill_entities()
    found_entities = {}
    
    for word in words:
        for entity_type, names in entities.items():
            if entity_type == 'Warning':
                continue  # skip warning — handle separately below
            if word in [name.lower() for name in names]:
                found_entities[word] = entity_type

    # identify warning type from full text instead of word matching
    if original_text:
        warning_type = identify_warning_type(words)
        if warning_type != 'general':
            found_entities[warning_type] = 'Warning'

    return found_entities

WARNING_TYPE_KEYWORDS = {
    'Pregnancy & Lactation': [
        'pregnan', 'lactat', 'breastfeed', 'fetal', 'fertility',
        'maternal', 'labor', 'delivery', 'embryo', 'animal stud',
        'pregnancy category', 'teratogen', 'cardiovascular anomal'
    ],
    'Contraindication': [
        'contraindic', 'hypersensitiv', 'allerg', 'interaction',
        'history of', 'qt prolongation', 'renal impairment',
        'restricted use', 'epilep', 'ticagrelor', 'ranolazine',
        'statin', 'colchicine', 'midazolam', 'ergot'
    ],
    'Age Restriction': [
        'pediatric', 'children', 'adolescent', 'infant', 'age',
        'tooth', 'bone growth', 'enamel', 'discolor', 'young animal'
    ],
    'Overdosage': [
        'overdos', 'overdosage', 'toxicit', 'gastric lavage',
        'dialysis', 'rehydration', 'elimination', 'antidote',
        'management of overdos', 'cns and metabolic'
    ],
    'Patient Condition': [
        'cdad', 'clostridium', 'severe skin', 'photosensitiv',
        'tendon', 'neuropathy', 'qt', 'renal function', 'bun',
        'hypertension', 'intracranial', 'mononucleosis', 'sulfite',
        'crystalluria', 'myasthenia', 'arthralgia', 'anaphylactic',
        'penicillin-sensitive', 'non-susceptible', 'antacid',
        'xanthine', 'sodium metabisulfite', 'peripheral'
    ]
}

def identify_warning_type(words: list) -> str:
    text = " ".join(words).lower()
    
    scores = {wtype: 0 for wtype in WARNING_TYPE_KEYWORDS}
    for wtype, keywords in WARNING_TYPE_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                scores[wtype] += 1

    best = max(scores, key=scores.get)
    
    print(f"[Warning Type] scores: {scores} → {best}")
    
    if scores[best] == 0:
        return 'general'
    
    return best
