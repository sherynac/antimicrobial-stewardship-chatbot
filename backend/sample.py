from html import entities
from pkgutil import get_data

from owlready2 import *
import string
import json
from ontolgy_traversal import OntologyTraversal

# Variables
onto = get_ontology("./backend/data/sample-ontology.rdf").load()

question = ""
entities = defaultdict(list)
intent = ""


# Functions

def load_data():
    
    print("Ontology:", onto)
    
    global traverse
    print(f"Loaded ontology with {len(list(onto.classes()))} classes")
    
    traverse = OntologyTraversal(onto)
    traverse.apply_reasoning()
    
        
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
    
    if intent == 'interaction':
        intent_interaction(entity_types, entities)
    elif intent == 'warning':
        intent_warning(entity_types, entities)
    
    
        
def intent_interaction(entity_types, entities):
    generic_brand_query = ['Antibiotic', 'Brand']
    brand_query = ['Brand']
    generic_query = ['Antibiotic']
    interaction = ['Substance']
    
    if all(e in entity_types for e in generic_brand_query):
        print("Identified query: Interaction for specific antibiotic brand")
        antibiotic_in_question = [word for word, etype in entities.items() if etype == 'Antibiotic']
        brand_in_question = [word for word, etype in entities.items() if etype == 'Brand']
        brands = traverse.find_brands(antibiotic_in_question[0])
        for brand in brands:
            if brand.lower() == brand_in_question[0].lower():
                print(f"\nInteractions for brand: {brand}")
                interaction_info = traverse.find_interactions(brand)
                print(interaction_info)
    
    elif all(e in entity_types for e in brand_query):
        print("Identified query: Interaction for specific brand")
        brand_in_question = [word for word, etype in entities.items() if etype == 'Brand']
        print(f"\nInteractions for brand: {brand_in_question[0]}")
        interaction_info = traverse.find_interactions(brand_in_question[0])
        print(interaction_info)
        
    elif all(e in entity_types for e in generic_query):
        print("Identified query: Interaction for specific antibiotic")
        antibiotic_in_question = [word for word, etype in entities.items() if etype == 'Antibiotic']
        brands = traverse.find_brands(antibiotic_in_question[0])
        for brand in brands:
            print(f"\nInteractions for brand: {brand}")
            interaction_info = traverse.find_interactions(brand)
            print(interaction_info)
        
    elif all(e in entity_types for e in interaction):
        print("Identified query: Interaction for specific substance")
        substance_in_question = [word for word, etype in entities.items() if etype == 'Substance']
    
def intent_warning(entity_types, entities):
    generic_brand_query = ['Antibiotic', 'Brand']
    brand_query = ['Brand']
    generic_query = ['Antibiotic']
    
    if all(e in entity_types for e in generic_brand_query):
        print("Identified query: Warning for specific antibiotic brand")
        antibiotic_in_question = [word for word, etype in entities.items() if etype == 'Antibiotic']
        brand_in_question = [word for word, etype in entities.items() if etype == 'Brand']
        brands = traverse.find_brands(antibiotic_in_question[0])
        for brand in brands:
            if brand.lower() == brand_in_question[0].lower():
                print(f"\nWarnings for brand: {brand}")
                warning_info = traverse.find_warnings(brand)
                print(warning_info)
    
    elif all(e in entity_types for e in brand_query):
        print("Identified query: Warning for specific brand")
        brand_in_question = [word for word, etype in entities.items() if etype == 'Brand']
        print(f"\nWarnings for brand: {brand_in_question[0]}")
        warning_info = traverse.find_warnings(brand_in_question[0])
        print(warning_info)
        
    elif all(e in entity_types for e in generic_query):
        print("Identified query: Warning for specific antibiotic")
        antibiotic_in_question = [word for word, etype in entities.items() if etype == 'Antibiotic']
        brands = traverse.find_brands(antibiotic_in_question[0])
        for brand in brands:
            print(f"\nWarnings for brand: {brand}")
            warning_info = traverse.find_warnings(brand)
            print(warning_info)



def fallbacks(entities):
    if have_fallback_keywords(entities) == 'about_chatbot':
        print("Fallback: About the chatbot")
        print("Ophiuchus is a chatbot designed to provide information about antibiotics, their interactions, indications, warnings, side effects, and stewardship. It uses an ontology-based approach to understand and answer user queries related to antibiotics.")
    elif have_fallback_keywords(entities) == 'recommendation':
        print("Fallback: Recommendation")
        print("For antibiotic recommendations, it's important to consult with a healthcare professional who can consider your specific condition, medical history, and any potential allergies. Always follow the advice of your healthcare provider when it comes to antibiotic use.")
    elif have_fallback_keywords(entities) == 'dosage_query':
        print("Fallback: Dosage query")
        print("Dosage information for antibiotics can vary widely based on the specific drug, the condition being treated, the patient's age, weight, kidney function, and other factors. Always refer to the prescribing information provided by the manufacturer or consult with a healthcare professional for accurate dosage guidance.")
    elif have_fallback_keywords(entities) == 'general_info':
        print("Fallback: General information")
        print("Antibiotics are medications used to treat bacterial infections. They work by killing bacteria or preventing their growth. There are many different classes of antibiotics, each with its own mechanism of action and spectrum of activity. It's important to use antibiotics responsibly to prevent the development of antibiotic resistance.")
    
def have_fallback_keywords(words):
    
    about_chatbot_keywords = ['about', 'chatbot', 'ophiuchus', 'you', 'who', 'what', 'name']
    recommendation_keywords = ['should', 'recommend', 'best', 'prescribe', 'give', 'take']
    dosage_query_keywords = ['dosage', 'dose', 'how much', 'how many', 'frequency', 'times', 'day', 'duration']
    general_info_keywords = ['type', 'form', 'category', 'class', 'what is', 'what\'s', 'tell me about']
    
    for word in words:
        if any(word in about_chatbot_keywords for word in words):
            return 'about_chatbot'
        elif any(word in recommendation_keywords for word in words):
            return 'recommendation'
        elif any(word in dosage_query_keywords for word in words):
            return 'dosage_query'
        elif any(word in general_info_keywords for word in words):
            return 'general_info'
    return  'none'
    
if __name__ == "__main__":
    load_data()
    fill_entities()
    intro()
    
    print("\n=== Interactive Mode ===")
    get_splitted_question()
    question_entities = look_up_entity(words)
    print(words)
    print(f"Identified entities in question: {question_entities}")
    
    if not question_entities or have_fallback_keywords(words) != 'none':
        print(have_fallback_keywords(words))
        print("fallback triggered")
        if not question_entities:
            print("I'm sorry, I couldn't identify any relevant entities in your question.")
        else:
            fallbacks(words)
    else:
        intent = identify_intent(words)
        print(f"Identified intent: {intent}")
    
        search_method(intent, question_entities)
    