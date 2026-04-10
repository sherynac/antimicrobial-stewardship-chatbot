from owlready2 import *
import string
import json

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

'''
PROGRAM START
'''

onto = get_ontology("https://gist.githubusercontent.com/sherynac/b5326e231c5e4aa6530f825fc1e7b54a/raw/sample-ontology.rdf").load()
print(f"Loaded ontology with {len(list(onto.classes()))} classes")

with open('./backend/data/vetted_response.json', 'r') as file:
    response_bank = json.load(file)
    print("Loaded JSON vetted response bank")

print("\n")
print("=" * 10)
print("Welcome to Ophiuchus!")
print("=" * 10)

print("\nAsk a question: ", end="")

question = input()
# question = "How is DOXIN supplied?"
intent = classifyIntent(question)
entities = recognizeEntities(question)

if intent == "GET_ANTIBIOTIC_INFO":
    # Brand is recognized
    brand_name = entities[0] if entities else None
    brand_obj = onto.search_one(iri=f"*{brand_name}*")
    presentation_obj = brand_obj.hasPresentation
    generic_obj = brand_obj.isBrandOf
    drug_class = generic_obj[0].hasDrugClass

    intent_data = response_bank["IntentDefinitions"][0]

    response_template = None
    for r in intent_data["responses"]:
        if r["responseID"] == 3:
            response_template = r["responseText"]
            break

    response = response_template.format(
        brand=brand_name,
        generic=generic_obj[0].name,
        drug_class=drug_class[0].name,
        presentation=presentation_obj[0].name
    )

    print(response)

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












