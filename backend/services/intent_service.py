from typing import List

def identify_intent(words):
    if any(word in ['about_chatbot'] for word in words):
        return 'get_about_chatbot'
    
    elif any(word in ['antibiotic_info'] for word in words):
        return 'get_antibiotic_info'
    
    elif any(word in ['compare'] for word in words):
        return 'compare_brands'
    
    elif any(word in ['uses_indications'] for word in words):
        return 'get_uses_indications'
    
    elif any(word in ['side effects'] for word in words):
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
    multiple_brands = ['Brand', 'Brand']
    susbtance = ['Substance']
    warning = ['Warning']
    generic_brand_side_effects = ['Antibiotic', 'Brand', 'SideEffect']
    generic_side_effects = ['Antibiotic', 'SideEffect']

    if all (e in entity_types for e in generic_brand):
        return 'generic_brand'
    elif all (e in entity_types for e in generic):
        return 'generic'
    elif all (e in entity_types for e in brand):
        return 'brand'
    elif all (e in entity_types for e in susbtance):
        return 'substance'
    elif all (e in entity_types for e in warning):
        return 'warning'
    elif all (e in entity_types for e in multiple_brands):
        return 'multiple_brands'
    elif all (e in entity_types for e in generic_brand_side_effects):
        return 'generic_brand_side_effects'
    else:
        return 'unknown_entity_combination'