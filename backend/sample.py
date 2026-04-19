from html import entities
from pkgutil import get_data

from owlready2 import *
import string
import json
from ontolgy_traversal import OntologyTraversal

# Variables
onto = get_ontology("https://gist.githubusercontent.com/sherynac/b5326e231c5e4aa6530f825fc1e7b54a/raw/sample-ontology.rdf").load()

traverse = OntologyTraversal(onto)

question = ""
words = []
entities = defaultdict(list)
intent = ""


# Functions

def load_data():
    onto = get_ontology("https://gist.githubusercontent.com/sherynac/b5326e231c5e4aa6530f825fc1e7b54a/raw/sample-ontology.rdf").load()
    print(f"Loaded ontology with {len(list(onto.classes()))} classes")

    with open('./backend/data/vetted_response.json', 'r') as file:
        response_bank = json.load(file)
        print("Loaded JSON vetted response bank")
        
def fill_entities():
    antibiotics = traverse.find_entities('Antibiotic')
    brands = traverse.find_entities('Brand')
    beverages = traverse.find_entities('Beverage')
    drugs = traverse.find_entities('Drug')
    foods = traverse.find_entities('Food')

    entities['Antibiotic'].extend(antibiotics)
    entities['Brand'].extend(brands)
    entities['Substance'].extend(beverages)
    entities['Substance'].extend(drugs)
    entities['Substance'].extend(foods)


def intro():
    print("\n")
    print("=" * 20)
    print("Welcome to Ophiuchus!")
    print("=" * 20)

    
def get_splitted_question():
    global question, words
    question = input("Ask a question: ")
    question = question.lower()
    question = re.sub(r'\s+', ' ', question)
    question = question.strip()
    words = re.findall(r'\b\w+\b', question)
    print(f"Splitted question: {words}")

def look_up_entity(words):
    found_entities = {}
    for word in words:
        for entity_type, names in entities.items():
            if word in [name.lower() for name in names]:
                found_entities[word] = entity_type

    return found_entities

def identify_intent(words):
    if any(word in ['interaction'] for word in words):
        return 'interaction'
    elif any(word in ['indication'] for word in words):
        return 'indication'
    elif any(word in ['warning'] for word in words):
        return 'warning'
    elif any(word in ['side effect'] for word in words):
        return 'side_effect'
    elif any(word in ['stewardship'] for word in words):
        return 'stewardship'
    else:
        return 'unknown'
    
def search_method(intent, entities):
    entity_types = []
    
    for etype in entities.values():
        if etype not in entity_types:
            entity_types.append(etype)
            
    print(f"Entity types in question: {entity_types}")
            
    generic_brand_query = ['Antibiotic', 'Brand']
    brand_query = ['Brand']
    generic_query = ['Antibiotic']
    interaction = ['Substance']
            
    if intent == 'interaction' and all(e in entity_types for e in generic_brand_query):
        print("Identified query: Interaction for specific antibiotic brand")
        antibiotic_in_question = [word for word, etype in entities.items() if etype == 'Antibiotic']
        brand_in_question = [word for word, etype in entities.items() if etype == 'Brand']
        brands = traverse.find_brands(antibiotic_in_question[0])
        for brand in brands:
            if brand.lower() == brand_in_question[0].lower():
                print(f"\nInteractions for brand: {brand}")
                interaction_info = traverse.find_interactions(brand)
                print(interaction_info)
    
    elif intent == 'interaction' and all(e in entity_types for e in brand_query):
        print("Identified query: Interaction for specific brand")
        brand_in_question = [word for word, etype in entities.items() if etype == 'Brand']
        print(f"\nInteractions for brand: {brand_in_question[0]}")
        interaction_info = traverse.find_interactions(brand_in_question[0])
        print(interaction_info)
        
    elif intent == 'interaction' and all(e in entity_types for e in generic_query):
        print("Identified query: Interaction for specific antibiotic")
        antibiotic_in_question = [word for word, etype in entities.items() if etype == 'Antibiotic']
        brands = traverse.find_brands(antibiotic_in_question[0])
        for brand in brands:
            print(f"\nInteractions for brand: {brand}")
            interaction_info = traverse.find_interactions(brand)
            print(interaction_info)
        
    elif intent == 'interaction' and all(e in entity_types for e in interaction):
        print("Identified query: Interaction for specific substance")
        substance_in_question = [word for word, etype in entities.items() if etype == 'Substance']
        interaction_info = traverse.find_entities(substance_in_question[0])
        print(f"\nInteractions for substance: {substance_in_question[0]}")
        print(interaction_info)
                
if __name__ == "__main__":
    load_data()
    fill_entities()
    intro()
    
    print("\n=== Interactive Mode ===")
    get_splitted_question()
    question_entities = look_up_entity(words)
    print(f"Identified entities in question: {question_entities}")
    
    intent = identify_intent(words)
    print(f"Identified intent: {intent}")
    
    search_method(intent, question_entities)
    