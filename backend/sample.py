import services.intent_service as intent_service
import services.ontology_service as ontology_service
import services.entities_service as entities_service
import services.question_service as question_service

onto = ontology_service.load_ontology()
entities = entities_service.fill_entities(onto)

def terminal_test():
    print("\n")
    print("=" * 10)
    print("Welcome to Ophiuchus!")
    print("=" * 10)

    print("\nAsk a question: ", end="")

    question = input()
    words = question_service.get_splitted_question(question)
    question_entities = entities_service.look_up_entity(onto, words)
    intent = intent_service.identify_intent(words)
    print(f"Identified intent: {intent}")
    query_type = intent_service.identify_entities_present(question_entities.values())
    print(f"Identified query type: {query_type}")
if __name__ == "__main__":
    terminal_test()