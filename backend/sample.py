from owlready2 import *
from rdflib import Graph
import string
import json
import random

'''
METHODS
'''
# Method for classifying intents
# NOTE: Add elif for questions to output intent
def classifyIntent (question):
    if ("How is DOXYCYCLINE supplied?" 
        or "How is DOXIN supplied?" 
        or "What dosage forms are available for the generic antibiotic DOXYCYCLINE and the brand-name antibiotic DYNADOXY ?"):
        return "GET_ANTIBIOTIC_INFO"
    elif ("hotdog"):
        return "COMPARE_BRANDS"
    elif ("hotdog2"):
        return "GET_USES_INDICATIONS"

# Method for simulating entity recognition
# NOTE: Add entities in capital letters, convert capital words to Pascal case
def recognizeEntities(question):
    words = question.split()
    entities = []

    for word in words:
        clean_word = word.strip(string.punctuation)
        if clean_word.isupper():
            pascal_word = clean_word.capitalize()
            entities.append(pascal_word)
    
    return entities

# Method to get response template from vetted response bank
# NOTE: type refers to the entity that was recognized (for context)
def getResponseTemplate (given_intent, type):
    for intent_obj in response_bank["IntentDefinitions"]:
        if intent_obj["intent"] == given_intent:
            for response in intent_obj["responses"]:
                if response["condition"] == type:
                    return response["responseText"]

# Method to transform an array into a string 
# EXAMPLE: [hotdog, rocket, phone] = hotdog, rocket and phone
def arrayToString (array):
    result = ""
    for i, element in enumerate(array):
        result += element.name
        
        if i == len(array) - 1:
            # Last element
            pass
        elif i == len(array) - 2:
            # add "and"
            result += " and "
        else:
            # add ','
            result += ", "

    return result

def formatToTable ():
    return table

# Method for resolving booleans into "Yes" or "No" strings
def isYesorNo (boolean):
    if boolean:
        return "Yes"
    return "No"

'''
PROGRAM START
'''

# Load Turtle file
g = Graph()
g.parse("./backend/data/sample-ontology.ttl", format="turtle")

# Save as RDF/XML (.owl)
g.serialize(destination="./backend/data/sample-ontology.owl", format="xml")


onto = get_ontology("./backend/data/sample-ontology.owl").load()
print(f"Loaded ontology with {len(list(onto.classes()))} classes")

with open('./backend/data/vetted_response.json', 'r') as file:
    response_bank = json.load(file)
    print("Loaded JSON vetted response bank")

print("\n")
print("=" * 10)
print("Welcome to Ophiuchus!")
print("=" * 10)

print("\nAsk a question: ", end="")

# question = input()
question = "What dosage forms are available for the generic antibiotic DOXYCYCLINE and the brand-name antibiotic DYNADOXY ?"
intent = classifyIntent(question)
entities = recognizeEntities(question)

if intent == "GET_ANTIBIOTIC_INFO":
    # Brand is recognized
    # brand_name = entities[0] if entities else None
    # brand_obj = onto.search_one(iri=f"*{brand_name}*")
    # presentation_obj = brand_obj.hasPresentation

    # generic_obj = brand_obj.isBrandOf
    # brands = generic_obj[0].hasBrandName
    # brands.remove(brand_obj)
    # drug_class = generic_obj[0].hasDrugClass

    # template = getResponseTemplate("GET_ANTIBIOTIC_INFO", "brand_only")
    # response = template.format(
    #     brand=brand_name,
    #     generic=generic_obj[0].name,
    #     drug_class=drug_class[0].name,
    #     presentation=presentation_obj[0].name,
    #     other_brands=arrayToString(brands)
    # )

    # print(response)

    # Generic is recognized
    # generic_name = entities[0] if entities else None
    # generic_obj = onto.search_one(iri=f"*{generic_name}*")
    # print(generic_obj)
    # drug_class = generic_obj.hasDrugClass
    # print(drug_class)
    # brand_obj = generic_obj.hasBrand
    # print(brand_obj)
    # for brand in brand_obj:
    #     print(brand.hasPresentation)

    # Generic and Brand is recognized
    isBrand = False
    generic_name = entities[0] if entities else None
    brand_name = entities[1] if entities else None

    generic_obj = onto.search_one(iri=f"*{generic_name}")
    brand_obj = onto.search_one(iri=f"*{brand_name}")

    if brand_obj.isBrandOf == generic_obj:
        isBrand = True
    
    presentation_obj = brand_obj.hasPresentation

    template = getResponseTemplate("GET_ANTIBIOTIC_INFO", "both_generic_and_brand")
    response = template.format(
        is_brand_of = isYesorNo(isBrand),
        brand=brand_name,
        generic=generic_name,
        presentation=presentation_obj[0].name,
    )

    print(response)
    











