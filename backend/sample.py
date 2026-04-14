import services.ner_service as ner_service
import services.intent_service as intent_service
import services.intent_handlers as intent_handler
import services.response_service as response_service
import services.ontology_service as ontology_service

from services.intent_handlers import handle_antibiotic_info
from utils.helpers import array_to_string, is_yes_or_no, add_space_to_pascal_case

from flask import jsonify
import json

''' 
PROGRAM START
'''

onto = ontology_service.load_ontology()
response_index = response_service.build_response_index()

INTENT_ROUTER = {
    "GET_ANTIBIOTIC_INFO": handle_antibiotic_info
    # "GET_DOSAGE": handle_dosage_info,
    # "GET_SIDE_EFFECTS": handle_side_effects
}

def main(question):
    print("\n")
    print("=" * 10)
    print("Welcome to Ophiuchus!")
    print("=" * 10)

    print("\nAsk a question: ", end="")

    # question = input()
    question = question
    print(question)
    intent = intent_service.classify_intent(question)
    entities = ner_service.recognize_entities(question)

    handler_function = INTENT_ROUTER.get(intent)

    if handler_function:
        final_response = handler_function(entities, onto, response_index)
        print(final_response)
    else:
        print(f"I recognized the intent '{intent}', but I don't know how to handle it yet.")
    
# Testing
main("How is DOXYCYCLINE supplied?")
main("How is DOXIN supplied?")
main("What dosage forms are available for the generic antibiotic DOXYCYCLINE and the brand-name antibiotic DYNADOXY ?")

