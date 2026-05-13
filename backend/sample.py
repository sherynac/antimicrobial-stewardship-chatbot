import services.intent_service as intent_service
from services.ner_service import ner_service
from services.ontology_service import ontology_service
from services.response_service import response_service
from services.warning_classifier_service import warning_classifier
from utils.helpers import to_camel_case
from collections import defaultdict


def terminal_test():
    print("\n")
    print("=" * 10)
    print("Welcome to Ophiuchus!")
    print("=" * 10)
    print("Type 'exit' to quit.\n")

    while True:
        try:
            print("\nAsk a question: ", end="")
            question = input()

            if question.lower() == "exit":
                print("Goodbye!")
                break

            raw_entities = ner_service.extract_entities(question)
            print(f"RAW question entities: {raw_entities}")

            question_entities = defaultdict(list)
            for entity_dict in raw_entities:
                entity_type = entity_dict['entity_type']
                
                # Preserve canonical casing for ontology matches; camel-case only NER output
                if entity_dict.get('source') == 'ontology' or entity_dict.get('source') == 'custom':
                    word = entity_dict['entity']
                else:
                    word = to_camel_case(entity_dict['entity'])
                
                question_entities[entity_type].append(word)
                
            print(f"Processed question entities: {question_entities}")
            
            intent = intent_service.identify_intent(question)
            print(f"Identified intent: {intent}")
            
            classified = ner_service.classify_entities(question_entities)

            if intent == "get_warning_precautions":
                warning_result = warning_classifier.predict(question)
                if warning_result['predicted_warning_type']:
                    classified['WarningType'] = [warning_result['predicted_warning_type']]
            
            print("CLASSIFIED ENTITIES", classified)

            entity_types = list(classified.keys())

            query_type = ner_service.identify_query_type(entity_types)
            print(f"Identified query type: {query_type}", end="\n\n")
                
            response = intent_service.handle_intent(intent, query_type, classified)
            print(response)

        except ValueError as e:
            error_json = response_service.build_text_response(str(e))
            print(error_json)
        except AssertionError as e:
            error_json = response_service.build_text_response(str(e))
            print(error_json)
        except Exception as e:
            print(f"Unexpected error: {e}")  # catch anything else so loop never dies

if __name__ == "__main__":
    terminal_test()
