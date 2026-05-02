import services.intent_service as intent_service
import services.ontology_service as ontology_service
import services.entities_service as entities_service
import services.question_service as question_service
onto = ontology_service.load_ontology()
entities = entities_service.fill_entities(onto)

def terminal_test():
    print(entities)
    print("\n")
    print("=" * 10)
    print("Welcome to Ophiuchus!")
    print("=" * 10)

    print("\nAsk a question: ", end="")

    question = input()
    words = question_service.get_splitted_question(question)
    raw_entities = entities_service.look_up_entity(onto, words)
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
        
    intent_service.handle_intent(onto, intent, query_type, question_entities)
if __name__ == "__main__":
    terminal_test()