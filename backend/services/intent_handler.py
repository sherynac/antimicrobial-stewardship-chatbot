import services.ontology_service as ontology_service

def handle_about_chatbot():
    return "Ophiuchus is an antimicrobial stewardship chatbot designed to provide information about antibiotics, their uses, side effects, interactions, and more. It aims to help users make informed decisions about antibiotic use and promote responsible stewardship."

def handle_antibiotic_info(onto, entities, query_type):
    
    if query_type == 'generic_brand':
        generic_name = entities.get('Antibiotic', [None])[0]
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(onto, brand_name)
        generic_obj = ontology_service.query_ontology(onto, generic_name)
    
    elif query_type == 'generic':
        generic_name = entities.get('Antibiotic', [None])[0]
        generic_obj = ontology_service.query_ontology(onto, generic_name)
        drug_class = generic_obj.hasDrugClass
        brands_obj = generic_obj.hasBrandName
        
    elif query_type == 'brand':
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(onto, brand_name)
        generic_obj = brand_obj.isBrandOf
        generic_name = generic_obj.name
        
    else:
        return "Please specify the antibiotic name or brand for more information."

def handle_compare_brands(onto, entities, query_type):
    if query_type == 'generic_brand':
        generic_name = entities.get('Antibiotic', [None])[0]
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(onto, brand_name)
        generic_obj = ontology_service.query_ontology(onto, generic_name)
        
        all_brands = list(generic_obj.hasBrandName)
        other_brands = [brand for brand in all_brands if brand.name != brand_obj.name]
        
        presentation_obj = brand_obj.hasPresentation
        
    if query_type == 'generic':
        generic_name = entities.get('Antibiotic', [None])[0]
        generic_obj = ontology_service.query_ontology(onto, generic_name)
        brands_obj = generic_obj.hasBrandName
        
        
    if query_type == 'multiple_brands':
        brand_names = entities.get('Brand', [0])[0:2]
        brand_objs = [ontology_service.query_ontology(onto, name) for name in brand_names]
        generic_objs = [brand.isBrandOf for brand in brand_objs]
        
    return "To compare antibiotic brands, please provide the names of the brands you want to compare."

def handle_uses_indications(onto, entities, query_type):
    if query_type == 'generic_brand':
        generic_name = entities.get('Antibiotic', [None])[0]
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(onto, brand_name)
        generic_obj = ontology_service.query_ontology(onto, generic_name)
        indication_obj = brand_obj.treats
        
    elif query_type == 'brand':
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(onto, brand_name)
        
        generic_obj = brand_obj.isBrandOf
        generic_name = generic_obj.name
        
        indication_obj = brand_obj.treats
    
    elif query_type == 'generic':
        generic_name = entities.get('Antibiotic', [None])[0]
        generic_obj = ontology_service.query_ontology(onto, generic_name)
        
        brands_obj = generic_obj.hasBrandName
        indication_obj = [ontology_service.query_ontology(onto, brand.name).treats for brand in brands_obj]
        
        
    return "To get information about the uses and indications of an antibiotic, please specify the antibiotic name or brand."

def handle_side_effects(onto, entities, query_type):
    if query_type == 'generic_brand_side_effects':
        generic_name = entities.get('Antibiotic', [None])[0]
        brand_name = entities.get('Brand', [None])[0]
        target_side_effects = entities.get('SideEffect', [None])[0]
        brand_obj = ontology_service.query_ontology(onto, brand_name)
        generic_obj = ontology_service.query_ontology(onto, generic_name)
        
        isFound = False
        
        for side_effect_instance in brand_obj.hasSideEffect:
            if side_effect_instance.name.lower() == target_side_effects.lower():
                isFound = True
                side_effecct_obj = ontology_service.query_ontology(onto, side_effect_instance.name)
                
        if not(isFound):
            print("NOT FOUND")
            
    elif query_type == 'generic_brand':
        generic_name = entities.get('Antibiotic', [None])[0]
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(onto, brand_name)
        generic_obj = ontology_service.query_ontology(onto, generic_name)
        
        side_effects = brand_obj.hasSideEffect
        
    elif query_type == 'generic':
        generic_name = entities.get('Antibiotic', [None])[0]
        generic_obj = ontology_service.query_ontology(onto, generic_name)
        
        brands_obj = generic_obj.hasBrandName
        side_effects = []
        for brand in brands_obj:
            brand_side_effects = brand.hasSideEffect
            side_effects.extend(brand_side_effects)
    
    elif query_type == 'generic_side_effects':
        generic_name = entities.get('Antibiotic', [None])[0]
        generic_obj = ontology_service.query_ontology(onto, generic_name)
        target_side_effects = entities.get('SideEffect', [None])[0]
        
        brands_obj = generic_obj.hasBrandName
        side_effects = []
        for side_effect_instance in brand_obj.hasSideEffect:
            if side_effect_instance.name.lower() == target_side_effects.lower():
                side_effecct_obj = ontology_service.query_ontology(onto, side_effect_instance.name)
        
        
    return "To get information about the side effects of an antibiotic, please specify the antibiotic name or brand."

def handle_substance_interaction(onto, entities, query_type):
    if query_type == 'generic_brand':
        generic_name = entities.get('Antibiotic', [None])[0]
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(onto, brand_name)
        generic_obj = ontology_service.query_ontology(onto, generic_name)
        interaction_ids = brand_obj.hasInteraction
        interactions = []
        for interaction_id in interaction_ids:
            interaction = interaction_id.interactsWith
            interactions.append(interaction)
        
    elif query_type == 'generic':
        generic_name = entities.get('Antibiotic', [None])[0]
        generic_obj = ontology_service.query_ontology(onto, generic_name)
        brands_obj = generic_obj.hasBrandName
        interactions = []
        for brand in brands_obj:
            brand_name = brand.name
            brand_obj = ontology_service.query_ontology(onto, brand_name)
            interaction_ids = brand_obj.hasInteraction
            for interaction_id in interaction_ids:
                interaction = interaction_id.interactsWith
                interactions.append(interaction)
                
    elif query_type == 'brand':
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(onto, brand_name)
        interaction_ids = brand_obj.hasInteraction
        interactions = []
        for interaction_id in interaction_ids:
            interaction = interaction_id.interactsWith
            interactions.append(interaction)
    else:
        return "To get information about substance interactions with an antibiotic, please specify the antibiotic name or brand."

def handle_warning_precautions(onto, entities, query_type):
    if query_type == 'generic_brand':
        generic_name = entities.get('Antibiotic', [None])[0]
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(onto, brand_name)
        generic_obj = ontology_service.query_ontology(onto, generic_name)
        
        warning_ids = brand_obj.hasWarning
        warnings = []
        for warning_id in warning_ids:
            warning = warning_id.HasWarningHeadline
            warnings.append(warning)
        
        
    elif query_type == 'generic':
        generic_name = entities.get('Antibiotic', [None])[0]
        generic_obj = ontology_service.query_ontology(onto, generic_name)
        brands_obj = generic_obj.hasBrandName
        warnings = []
        for brand in brands_obj:
            brand_name = brand.name
            brand_obj = ontology_service.query_ontology(onto, brand_name)
            warning_ids = brand_obj.hasWarning
            for warning_id in warning_ids:
                warning = warning_id.HasWarningHeadline
                warnings.append(warning)
                
    elif query_type == 'brand':
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(onto, brand_name)
        warning_ids = brand_obj.hasWarning
        warnings = []
        for warning_id in warning_ids:
            warning = warning_id.HasWarningHeadline
            warnings.append(warning)
    
    return "To get information about warnings and precautions for an antibiotic, please specify the antibiotic name or brand."

def handle_monitoring_instruction(onto, entities, query_type):
    if query_type == 'generic_brand':
        generic_name = entities.get('Antibiotic', [None])[0]
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(onto, brand_name)
        generic_obj = ontology_service.query_ontology(onto, generic_name)
        storage_rules_id = brand_obj.hasStorageRule
        storage_rules = []
        
        for storage_id in storage_rules_id:
            storage_rule = storage_id.HasStewardhipDescription
            storage_rules.append(storage_rule)
    
    elif query_type == 'brand':
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(onto, brand_name)
        storage_rules_id = brand_obj.hasStorageRule
        storage_rules = []
        
        for storage_id in storage_rules_id:
            storage_rule = storage_id.HasStewardhipDescription
            storage_rules.append(storage_rule)
            
    elif query_type == 'generic':
        generic_name = entities.get('Antibiotic', [None])[0]
        generic_obj = ontology_service.query_ontology(onto, generic_name)
        brands_obj = generic_obj.hasBrandName
        storage_rules_id = generic_obj.hasStorageRule
        storage_rules = []
        
        for brand in brands_obj:
            brand_name = brand.name
            storage_rules_id = brand.hasStorageRule
            
        for storage_id in storage_rules_id:
            storage_rule = storage_id.HasStewardhipDescription
            storage_rules.append(storage_rule)

def handle_storage_instruction():
    return "To get storage instructions for an antibiotic, please specify the antibiotic name or brand."

def handle_proper_use_of_medicine():
    return "To get information about the proper use of an antibiotic, please specify the antibiotic name or brand."

def handle_antibiotic_adherence():
    return "To get information about antibiotic adherence, please specify the antibiotic name or brand."

def handle_is_not_recognized():
    return "Sorry, I didn't understand your question. Please try rephrasing it or ask about a specific antibiotic or brand."

def handle_redirect_medicine_query():
    return "Redirecting to medicine query handler..."

def handle_redirect_dosage_query():
    return "Redirecting to dosage query handler..."

def handle_get_general_answer():
    return "To get a general answer, please ask a specific question about antibiotics, their uses, side effects, interactions, or any other related topic."