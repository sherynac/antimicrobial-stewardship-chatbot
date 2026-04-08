from owlready2 import *
import string


'''
METHODS
'''
# Method for classifying intents
# NOTE: Add elif for questions to output intent
def classifyIntent (question):
    if ("How is DOXYCYCLINE supplied (dosage forms)?" 
        or "How is DOXIN supplied (dosage forms)?" 
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
onto = get_ontology("./backend/data/sample-ontology.rdf").load()
print(f"Loaded ontology with {len(list(onto.classes()))} classes")

print("\n")
print("=" * 10)
print("Welcome to Ophiuchus!")
print("=" * 10)

print("\nAsk a question: ", end="")

question = input()
intent = classifyIntent(question)
entities = recognizeEntities(question)

if intent == "GET_ANTIBIOTIC_INFO":
    print(intent)
    print(entities)
    brand_name = entities[0] if entities else None
    brand_obj = onto.search_one(iri=f"*{brand_name}*")
    print(f"  Presentations: {brand_obj.hasPresentation}")










