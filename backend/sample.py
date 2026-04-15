import services.ner_service as ner_service
import services.intent_service as intent_service
import services.intent_handlers as intent_handler
import services.response_service as response_service
import services.ontology_service as ontology_service

from services.intent_handlers import handle_antibiotic_info, handle_compare_brands
from utils.helpers import array_to_string, is_yes_or_no, add_space_to_pascal_case

from flask import jsonify
import json

''' 
PROGRAM START
'''

onto = ontology_service.load_ontology()
response_index = response_service.build_response_index()

INTENT_ROUTER = {
    "GET_ANTIBIOTIC_INFO": handle_antibiotic_info,
    "COMPARE_BRANDS": handle_compare_brands
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
    
# Testing for get_antibiotic_info
# main("How is DOXYCYCLINE supplied?")
# main("How is DOXIN supplied?")
# main("What dosage forms are available for the generic antibiotic DOXYCYCLINE and the brand-name antibiotic DYNADOXY ?")
# main("How is PARACETAMOL supplied?")
# main("How is BIOGESIC supplied?")
# main("What dosage forms are available for the generic antibiotic PARACETAMOL and the brand-name antibiotic BIOGESIC ?")

# Testing for compare_brands
# main("What is the difference between DOXIN and DOXYCLEN?")
# main("What is the difference between DOXIN, DOXYCLEN and DYNADOXY?")
# main("What is the difference between DOXIN and LEVOCIN?")
# main("Compare the different brands of DOXYCYCLINE.")
# main("Compare DOXIN with other brands of DOXYCYCLINE.")

# Testing for uses/indications
# main("I was given DYNADOXY (DOXYCYCLINE), what is it for?")
# main("Why was I prescribed DYNADOXY?")
# main("What are the clinical indications for DOXYCYCLINE?")