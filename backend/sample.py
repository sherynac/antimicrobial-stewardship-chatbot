import services.intent_service as intent_service
import services.entities_service as entities_service
from services.ontology_service import ontology_service
from services.response_service import response_service
from utils.helpers import get_splitted_question
entities = entities_service.fill_entities()

def terminal_test(question):
    try:
        # print(entities)
        print("\n")
        print("=" * 10)
        print("Welcome to Ophiuchus!")
        print("=" * 10)

        print("\nAsk a question: ", end="")

        # question = input()
        words = get_splitted_question(question)
        raw_entities = entities_service.look_up_entity(words)
        print(f"RAW question entities: {raw_entities}")
        
        question_entities = {}
        for word, entity_type in raw_entities.items():
            if entity_type not in question_entities:
                question_entities[entity_type] = []
            question_entities[entity_type].append(word.capitalize())
            
        print(f"Processed question entities: {question_entities}")
        
        intent = intent_service.identify_intent(words)
        print(f"Identified intent: {intent}")
        query_type = intent_service.identify_entities_present(raw_entities.values())
        print(f"Identified query type: {query_type}")
            
        response = intent_service.handle_intent(intent, query_type, question_entities)
        print(response)
    except ValueError as e:
        error_json = response_service.build_text_response(str(e))
        print(error_json)   
    except AssertionError as e: 
        error_json = response_service.build_text_response(str(e))
        print(error_json)  

if __name__ == "__main__":
    # test for all possible cases for get_antibiotic_info
    # terminal_test("doxycycline doxin antibiotic_info")
    # terminal_test("levofloxacin levocin antibiotic_info")
    # terminal_test("levofloxacin doxin antibiotic_info")
    # terminal_test("doxycycline levocin antibiotic_info")
    # terminal_test("levocin antibiotic_info")
    # terminal_test("doxin antibiotic_info")
    # terminal_test("doxycycline antibiotic_info")
    # terminal_test("levofloxacin antibiotic_info")

    # test for all possible cases for get_uses_indications
    # terminal_test("doxycycline doxyclen uses_indications") 
    # terminal_test("doxycycline levocin uses_indications") 
    # terminal_test("doxycycline doxin uses_indications")
    # terminal_test("doxyclen uses_indications")
    # terminal_test("doxin uses_indications")
    # terminal_test("doxycycline uses_indications")

    # test for all possible cases for get_side_effects
    # terminal_test("doxycycline doxyclen headache side_effects")
    # terminal_test("doxycycline doxyclen diarrhea side_effects") 
    # terminal_test("doxycycline levocin side_effects") 
    # terminal_test("doxycycline doxin side_effects")
    # terminal_test("doxyclen headache side_effects")
    # terminal_test("doxyclen diarrhea side_effects")
    # terminal_test("doxin side_effects")
    # terminal_test("doxycycline nausea side_effects")
    # terminal_test("doxycycline headache side_effects")
    # terminal_test("doxycycline side_effects")

