from typing import List
import services.ontology_service as ontology_service
import services.intent_handler as intent_handler

def identify_intent(words):
    
    if any(word in ['antibiotic_info'] for word in words):
        return 'get_antibiotic_info'
    
    elif any(word in ['uses_indications'] for word in words):
        return 'get_uses_indications'
    
    elif any(word in ['side_effects'] for word in words):
        return 'get_side_effects'
    
    elif any(word in ['substance_interaction'] for word in words):
        return 'get_substance_interaction'
    
    elif any(word in ['warning_precautions'] for word in words):
        return 'get_warning_precautions'
    
    elif any(word in ['monitoring_instruction'] for word in words):
        return 'get_monitoring_instruction'
    
    elif any(word in ['storage_instruction'] for word in words):
        return 'get_storage_instruction'
    
    elif any(word in ['proper_use_of_medicine'] for word in words):
        return 'get_proper_use_of_medicine'
    
    elif any(word in ['antibiotic adherence'] for word in words):
        return 'get_antibiotic_adherence'
    
    elif any(word in ['not_recognized'] for word in words):
        return 'is_not_recognized'
    
    elif any(word in ['medicine query'] for word in words):
        return 'redirect_medicine_query'
    
    elif any(word in ['dosage_query'] for word in words):
        return 'redirect_dosage_query'
    
    elif any(word in ['general_answer'] for word in words):
        return 'get_general_answer'
    
    else:
        return 'unknown_intent'
    
def identify_entities_present(entity_types):
    generic_brand = ['Antibiotic', 'Brand']
    generic = ['Antibiotic']
    brand = ['Brand']
    substance = ['Substance']
    generic_substance = ['Antibiotic', 'Substance']
    brand_substance = ['Brand', 'Substance']
    warning = ['Warning']
    generic_brand_side_effects = ['Antibiotic', 'Brand', 'SideEffect']
    generic_side_effects = ['Antibiotic', 'SideEffect']

    if all (e in entity_types for e in generic_substance):
        return 'generic_substance'
    elif all (e in entity_types for e in brand_substance):
        return 'brand_substance'
    elif all (e in entity_types for e in warning):
        return 'warning'
    elif all (e in entity_types for e in generic_brand_side_effects):
        return 'generic_brand_side_effects'
    elif all (e in entity_types for e in generic_side_effects):
        return 'generic_side_effects'
    elif all (e in entity_types for e in generic_brand):
        return 'generic_brand'
    elif all (e in entity_types for e in generic):
        return 'generic'
    elif all(e == 'Brand' for e in entity_types):
        entity_types_list = list(entity_types)
        if entity_types_list.count('Brand') > 1:
            return 'multiple_brands'
        return 'brand'
    elif all (e in entity_types for e in substance):
        return 'substance'
    else:
        return 'unknown_entity_combination'
    
def handle_intent(intent, query_type, question_entities):
    if intent == 'get_about_chatbot':
        return intent_handler.handle_about_chatbot()
    elif intent == 'get_antibiotic_info':
        return intent_handler.handle_antibiotic_info(question_entities, query_type)
    elif intent == 'compare_brands':
        return intent_handler.handle_compare_brands(question_entities, query_type)
    elif intent == 'get_uses_indications':
        return intent_handler.handle_uses_indications(question_entities, query_type)
    elif intent == 'get_side_effects':
        return intent_handler.handle_side_effects(question_entities, query_type)
    elif intent == 'get_substance_interaction':
        return intent_handler.handle_substance_interaction(question_entities, query_type)
    elif intent == 'get_warning_precautions':
        return intent_handler.handle_warning_precautions(question_entities, query_type)
    elif intent == 'get_monitoring_instruction':
        return intent_handler.handle_monitoring_instruction(question_entities, query_type)
    elif intent == 'get_storage_instruction':
        return intent_handler.handle_storage_instruction(question_entities, query_type)
    elif intent == 'get_proper_use_of_medicine':
        return intent_handler.handle_proper_use_of_medicine(question_entities, query_type)
    elif intent == 'get_antibiotic_adherence':
        return intent_handler.handle_antibiotic_adherence(question_entities, query_type)
    elif intent == 'is_not_recognized':
        return intent_handler.handle_is_not_recognized()
    elif intent == 'redirect_medicine_query':
        return intent_handler.handle_redirect_medicine_query()
    elif intent == 'redirect_dosage_query':
        return intent_handler.handle_redirect_dosage_query()
    elif intent == 'get_general_answer':
        return intent_handler.handle_general_answer( query_type, question_entities)
    else:
        print("Sorry, I couldn't understand your question. Could you please rephrase it?")
        return None
    
        