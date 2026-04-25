import services.ner_service as ner_service
import services.intent_service as intent_service
import services.intent_handlers as intent_handler
import services.response_service as response_service
import services.ontology_service as ontology_service

from services.intent_handlers import handle_antibiotic_info, handle_compare_brands, handle_uses_indications, handle_side_effects, handle_storage_instructions
from utils.helpers import array_to_string, is_yes_or_no, add_space_to_pascal_case

# from flask import jsonify
from owlready2 import sync_reasoner_hermit
import json

''' 
PROGRAM START
'''

onto = ontology_service.load_ontology()
response_index = response_service.build_response_index()

INTENT_ROUTER = {
    "GET_ANTIBIOTIC_INFO": handle_antibiotic_info,
    "COMPARE_BRANDS": handle_compare_brands,
    "GET_USES_INDICATIONS": handle_uses_indications,
    "GET_SIDE_EFFECTS": handle_side_effects,
    "GET_STORAGE_INSTRUCTIONS": handle_storage_instructions
}

def main(question):
    try :
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
        print("ENTITIES:", entities)

        handler_function = INTENT_ROUTER.get(intent)

        if handler_function:
            final_response = handler_function(entities, onto, response_index)
            print(final_response)
        else:
            print(f"I recognized the intent '{intent}', but I don't know how to handle it yet.")
    except ValueError as e: # When entities cannot be found
        error_json = response_service.build_text_response(str(e))
        print(error_json)
    # except Exception as e:
    #     print(f"An unexpected error occurred: {str(e)}")
    
# Testing for get_antibiotic_info
# main("How is LEVOCIN supplied?") 
# main("How is DYNADOXY supplied?")
# main("What dosage forms are available for the generic antibiotic DOXYCYCLINE and the brand-name antibiotic DYNADOXY ?")
# main("What dosage forms are available for the generic antibiotic LEVOFLOXACIN and the brand-name antibiotic LEVOCIN ?")
# main("How is DOXYCYCLINE supplied?") 
# main("How is PARACETAMOL supplied?")
# main("How is BIOGESIC supplied?")
# main("What dosage forms are available for the generic antibiotic PARACETAMOL and the brand-name antibiotic BIOGESIC ?")

# Testing for compare_brands
# main("What is the difference between DOXIN, DOXYCLEN and DYNADOXY?") # more than 2 brands
# main("What is the difference between DOXIN and LEVOCIN?") # brands with not same generic
# main("Compare the different brands of DOXYCYCLINE.") # generic
# main("Compare DOXIN with other brands of DOXYCYCLINE.") # brand, generic

# Testing for uses/indications
# main("i was given DOXYCLEN (DOXYCYCLINE), what is it for?") # single indication, brand, generic
# main("i was given DOXIN (DOXYCYCLINE), what is it for?") # multiple indications, brand, generic
# main("Why was i prescribed DOXYCLEN?") # single indication, brand
# main("Why was i prescribed DOXIN?") # multiple indications, brand
# main("What are the clinical indications for DOXYCYCLINE?") # generic

# Testing for get side effects
# main("What are the side effects of DOXYCYCLINE?") # generic 
main("Will DOXYCYCLINE give me a HEADACHE?") # generic, side effect (side effect is not connected)
main("Will DOXYCYCLINE give me a DIARRHEA?") # generic, side effect (side effect is connected)
# main("What are the common side effects of DYNADOXY?") # brand, single side effect
# main("What are the common side effects of DOXIN?") # brand, multiple side effect
# main("Will DYNADOXY give me a HEADACHE?") # brand, side effect (not connected)
# main("Will DYNADOXY give me a DIARRHEA?") # brand, side effect (connected)
# main("What are the side effects of DYNADOXY (DOXYCYCLINE)?") # brand, generic
# main("Will DYNADOXY (DOXYCYCLINE) give me a HEADACHE?") # brand, generic, side effect (not connected)
# main("Will DYNADOXY (DOXYCYCLINE) give me a DIARRHEA?") # brand, generic, side effect (connected)

# Testing for storage stewardship
# main("How do i keep DOXIN safe at home?")
# # main("How do i keep DOXYCLEN safe at home?") # no storage instruction
# main("How long is this DYNADOXY good for after the pharmacist mixed it?")
# main("Do i need to keep DYNADOXY (DOXYCYCLINE) away from sunlight?")
# main("Can i keep DOXYCYCLINE on my kitchen counter by the window?")

