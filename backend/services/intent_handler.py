import services.ontology_service as ontology_service
from services.helpers import add_space_to_pascal_case

# Every method still needs to fetch the references and saving to a response

def handle_about_chatbot():
    return "Ophiuchus is an antimicrobial stewardship chatbot designed to provide information about antibiotics, their uses, side effects, interactions, and more. It aims to help users make informed decisions about antibiotic use and promote responsible stewardship."

def handle_antibiotic_info(onto, entities, query_type):
    
    if query_type == 'generic_brand':
        generic_name = entities.get('Antibiotic', [None])[0]
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(onto, brand_name)
        generic_obj = ontology_service.query_ontology(onto, generic_name)
        presentation_obj = brand_obj.hasPresentation
        print("Presentation Object: ", presentation_obj)
        
        presentation = presentation_obj[0].is_a
        print("Generic: ", generic_name)
        print("Brand: ", brand_name)
        print("Presentation: ", presentation.name)
    
    elif query_type == 'generic':
        generic_name = entities.get('Antibiotic', [None])[0]
        generic_obj = ontology_service.query_ontology(onto, generic_name)
        drug_class = generic_obj.hasDrugClass
        brands_obj = generic_obj.hasBrandName
        presentations = []
        for brand in brands_obj:
            presentation_obj = brand.hasPresentation
            presentation = presentation_obj[0].is_a
            presentations.append(presentation.name)
        
        print("Generic: ", generic_name)
        print("Drug Class: ", drug_class)
        print("Brands: ", brands_obj)
        print("Presentations: ", presentations)
            
    elif query_type == 'brand':
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(onto, brand_name)
        generic_obj = brand_obj.isBrandOf
        generic_name = generic_obj.name
        presentation_obj = brand_obj.hasPresentation
        print("Presentation Object: ", presentation_obj)
        presentation = presentation_obj[0].is_a
        
        print("Brand: ", brand_name)
        print("Generic: ", generic_name)
        print("Presentations: ", presentation.name)
        
    else:
        return "Please specify the antibiotic name or brand for more information."

# need checking of results
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
    print(query_type)
    if query_type == 'generic_brand':
        print("Handling uses and indications for generic_brand query type")
        generic_name = entities.get('Antibiotic', [None])[0]
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(onto, brand_name)
        generic_obj = ontology_service.query_ontology(onto, generic_name)
        indication_obj = brand_obj.treats
        
        print(len(indication_obj))
        if len(indication_obj) == 1:
            print("Single indication found.")
            
            indication, severity, disease_type = ontology_service.get_indication_severity_type(onto, indication_obj[0])
            
            if severity:
                indication_final = f"{severity} {indication}"
            else:
                indication_final = indication
                
            symptoms_obj = indication_obj[0].hasSymptoms
        else:
            print("Multiple indications found.")
            indication_final = []
            symptoms_obj = []
            for indication in indication_obj:
                indication_name, severity, disease_type = ontology_service.get_indication_severity_type(onto, indication)
                if severity:
                    indication_name = f"{severity} {indication_name}"
                indication_final.append(indication_name)
                symptoms_obj.append(indication.hasSymptoms)
                
        print("Generic: ", generic_name)
        print("Brand: ", brand_name)
        print("Indications: ", indication_final)
        print("Disease Types: ", disease_type)
        print("Symptoms: ", symptoms_obj)
        
    elif query_type == 'brand':
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(onto, brand_name)
        
        generic_obj = brand_obj.isBrandOf
        generic_name = generic_obj.name
        
        indication_obj = brand_obj.treats
        
        if len(indication_obj) == 1:
            print("Single indication found.")
            
            indication, severity, disease_type = ontology_service.get_indication_severity_type(onto, indication_obj[0])
            
            if severity:
                indication_final = f"{severity} {indication}"
            else:
                indication_final = indication
                
            symptoms_obj = indication_obj[0].hasSymptoms
            
        else:
            print("Multiple indications found.")
            indication_final = []
            symptoms_obj = []
            for indication in indication_obj:
                indication_name, severity, disease_type = ontology_service.get_indication_severity_type(onto, indication)
                if severity:
                    indication_name = f"{severity} {indication_name}"
                indication_final.append(indication_name)
                symptoms_obj.extend(indication.hasSymptoms)
        
        print("Brand: ", brand_name)
        print("Generic: ", generic_name)
        print("Indications: ", indication_final)
        print("Disease Types: ", disease_type)
        print("Symptoms: ", symptoms_obj)
    
    elif query_type == 'generic':
        generic_name = entities.get('Antibiotic', [None])[0]
        generic_obj = ontology_service.query_ontology(onto, generic_name)
        
        brands_obj = generic_obj.hasBrandName
        indication_final = []
        symptoms_obj = []
        
        print("Generic: ", generic_name)
        for brand in brands_obj:
            print("Brand: ", brand.name)
            indication_obj = brand.treats
            for indication in indication_obj:
                indication_name, severity, disease_type = ontology_service.get_indication_severity_type(onto, indication)
                if severity:
                    indication_name = f"{severity} {indication_name}"
                    
                print("Indication: ", indication_name)
                print("Disease Type: ", disease_type)
                print("Symptoms: ", indication.hasSymptoms)
                
                indication_final.append(indication_name)
                symptoms_obj.extend(indication.hasSymptoms)
        
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
            ontology_side_effect = side_effect_instance.is_a[0].name
            if target_side_effects.name.lower() == ontology_side_effect.lower():
                isFound = True
                
        if not(isFound):
            print("NOT FOUND")
            side_effect = target_side_effects
            generic = generic_name
            brand = brand_name
            
        print("Generic: ", generic_name)
        print("Brand: ", brand_name)
        print("Side Effect Queried: ", target_side_effects)
        print("Side Effect Found: ", isFound)
            
    elif query_type == 'generic_brand':
        generic_name = entities.get('Antibiotic', [None])[0]
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(onto, brand_name)
        generic_obj = ontology_service.query_ontology(onto, generic_name)
        
        side_effects = brand_obj.hasSideEffect
        side_effects_list = []
        
        for side_effect in side_effects:
            side_effect_class = side_effect.is_a
            pattern_object = side_effect.whichIs
            duration_str = side_effect.lastsFor
            description = side_effect.hasSideEffectDescription
        
            if "FreqruencyNotReported" in pattern_object[0].name:
                pattern = "Frequency not reported"
            else:
                side_effect = side_effect_class[0].name
                pattern = pattern_object[0].name
                
            if "Not Specified" in duration_str[0]:
                description = description[0]
            else:
                description = description[0]
                duration = add_space_to_pascal_case(duration_str[0])
                
            print("Generic: ", generic_name)
            print("Brand: ", brand_name)
            print("Side Effect: ", side_effect)
            print("Pattern: ", pattern)
            print("Duration: ", duration)
            print("Description: ", description)
            
            side_effects_list.append({
                "side_effect": side_effect,
                "pattern": pattern,
                "duration": duration,
                "description": description
            })

    elif query_type == 'generic':
        generic_name = entities.get('Antibiotic', [None])[0]
        generic_obj = ontology_service.query_ontology(onto, generic_name)
        
        brands_obj = generic_obj.hasBrandName
        side_effects_list = []
        
        print("Generic: ", generic_name)
        print("Brands: ", brands_obj)
        for brand in brands_obj:
            brand_side_effects = brand.hasSideEffect
            for side_effect in brand_side_effects:
                side_effect_class = side_effect.is_a
                pattern_object = side_effect.whichIs
                duration_str = side_effect.lastsFor
                description = side_effect.hasSideEffectDescription
            
                if "FreqruencyNotReported" in pattern_object[0].name:
                    pattern = "Frequency not reported"
                else:
                    side_effect = side_effect_class[0].name
                    pattern = pattern_object[0].name
                    
                if "Not Specified" in duration_str[0]:
                    description = description[0]
                else:
                    description = description[0]
                    duration = add_space_to_pascal_case(duration_str[0])
                    
                side_effects_list.append({
                    "side_effect": side_effect,
                    "pattern": pattern,
                    "duration": duration,
                    "description": description
                })
                
                print("Generic: ", generic_name)
                print("Brand: ", brand.name)
                print("Side Effect: ", side_effect)
                print("Pattern: ", pattern)
                print("Duration: ", duration)
                print("Description: ", description)
    
    # have not yet tested , error in creating side_effect entities
    elif query_type == 'generic_side_effects':# have not tested
        generic_name = entities.get('Antibiotic', [None])[0]
        generic_obj = ontology_service.query_ontology(onto, generic_name)
        target_side_effects = entities.get('SideEffect', [None])[0]
        
        brands_obj = generic_obj.hasBrandName
        side_effects = []
        found_brands = []
        
    
        for brand in brands_obj:
            print("Brand_side_effects", brand.hasSideEffect)
            for side_effect_instance in brand.hasSideEffect:
                ontology_side_effect = side_effect_instance.is_a[0].name
                print("Ontology Side Effect: ", ontology_side_effect)
                if target_side_effects.lower() == ontology_side_effect.lower():
                    side_effects.append(side_effect_instance)
                    found_brands.append(brand)
        
        print("Generic: ", generic_name)
        print("Side Effect Queried: ", target_side_effects)
        print("Found in Brands: ", found_brands)
        print("Side Effects Found: ", side_effects)

    elif query_type == 'brand':
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(onto, brand_name)
        target_side_effects = entities.get('SideEffect', [None])[0]
        generic_obj = brand_obj.isBrandOf
        generic_name = generic_obj.name
        
        brand_side_effects = brand_obj.hasSideEffect
        side_effects_list = []
        
        for side_effect_instance in brand_side_effects:
            side_effect_class = side_effect_instance.is_a
            pattern_object = side_effect_instance.whichIs
            duration_str = side_effect_instance.lastsFor
            description = side_effect_instance.hasSideEffectDescription
            
            if "FreqruencyNotReported" in pattern_object[0].name:
                pattern = "Frequency not reported"
            else:
                side_effect = side_effect_class[0].name
                pattern = pattern_object[0].name
                    
            if "Not Specified" in duration_str[0]:
                description = description[0]
            else:
                description = description[0]
                duration = add_space_to_pascal_case(duration_str[0])
                    
            side_effects_list.append({
                "side_effect": side_effect,
                "pattern": pattern,
                "duration": duration,
                "description": description
            })
            
            print("Generic: ", generic_name)
            print("Brand: ", brand_name)
            print("Side Effect: ", side_effect)
            print("Pattern: ", pattern)
            print("Duration: ", duration)
            print("Description: ", description)
            
    return "To get information about the side effects of an antibiotic, please specify the antibiotic name or brand."

def handle_substance_interaction(onto, entities, query_type):
    if query_type == 'generic_brand':
        generic_name = entities.get('Antibiotic', [None])[0]
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(onto, brand_name)
        generic_obj = ontology_service.query_ontology(onto, generic_name)
        interaction_ids = brand_obj.hasInteraction
        
        print("Generic Name: ", generic_name)
        print("Brand Name: ", brand_name)


        interactions = []
        for interaction_id in interaction_ids:
            substance = interaction_id.interactsWith
            description = interaction_id.hasInteractionDescription
            clinical_effects = interaction_id.hasClinicalEffects
            management_advice = interaction_id.hasManagementAdvice
            
            print("Substance: ", substance)
            print("Description: ", description)
            print("Clinical_effects", clinical_effects)
            print("Management Advice:", management_advice)
            
        
    elif query_type == 'generic':
        generic_name = entities.get('Antibiotic', [None])[0]
        generic_obj = ontology_service.query_ontology(onto, generic_name)
        brands_obj = generic_obj.hasBrandName
        interactions = []
        print("Generic Name: ", generic_name)
        for brand in brands_obj:
            brand_name = brand.name
            print("Brand Name: ", brand_name)
            brand_obj = ontology_service.query_ontology(onto, brand_name)
            interaction_ids = brand_obj.hasInteraction
            for interaction_id in interaction_ids:
                substance = interaction_id.interactsWith
                description = interaction_id.hasInteractionDescription
                clinical_effects = interaction_id.hasClinicalEffects
                management_advice = interaction_id.hasManagementAdvice
                
                print("Substance: ", substance)
                print("Description: ", description)
                print("Clinical_effects", clinical_effects)
                print("Management Advice:", management_advice)
                
    elif query_type == 'brand':
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(onto, brand_name)
        generic_obj = brand_obj.isBrandOf
        generic_name = generic_obj.name
        interaction_ids = brand_obj.hasInteraction
        interactions = []
        
        print("Generic: ", generic_name)
        print("Brnad", brand)
        for interaction_id in interaction_ids:
                substance = interaction_id.interactsWith
                description = interaction_id.hasInteractionDescription
                clinical_effects = interaction_id.hasClinicalEffects
                management_advice = interaction_id.hasManagementAdvice
                
                print("Substance: ", substance)
                print("Description: ", description)
                print("Clinical_effects", clinical_effects)
                print("Management Advice:", management_advice)
            
    # not yet done
    elif query_type == 'substance':
        substance = entities.get('Substance', [None])[0]
        substance_obj = ontology_service.query_ontology(onto, substance)
        interaction_ids = substance_obj.isInvolvedIn
        interactions = []
        brands = []
        for interaction_id in interaction_ids:
            interaction = interaction_id.interactsWith
            interactions.append(interaction)
            brands_obj = interaction_id.isInteractionOf
            for brand in brands_obj:
                brand_name = brand.hasBrandName
                brands.append(brand_name)
                

    elif query_type == 'generic_substance':
        generic_name = entities.get('Antibiotic', [None])[0]
        target_substance = entities.get('Substance', [None])[0]
        generic_obj = ontology_service.query_ontology(onto, generic_name)
        brands_obj = generic_obj.hasBrandName
        interactions = []
        brands = []
        
        print("Generic: ", generic_name)

        for brand in brands_obj:
            brand_name = brand.name
            brand_obj = ontology_service.query_ontology(onto, brand_name)
            interaction_ids = brand_obj.hasInteraction
            for interaction_id in interaction_ids:
                substance = interaction_id.interactsWith
                if target_substance.lower() == substance[0].name.lower():
                    description = interaction_id.hasInteractionDescription
                    clinical_effects = interaction_id.hasClinicalEffects
                    management_advice = interaction_id.hasManagementAdvice
                    
                    print("Brand: ", brand_name)
                    print("Substance: ", substance)
                    print("Description: ", description)
                    print("Clinical_effects", clinical_effects)
                    print("Management Advice:", management_advice)
                    
    elif query_type == 'brand_substance':
        brand_name = entities.get('Brand', [None])[0]
        target_substance = entities.get('Substance', [None])[0]
        brand_obj = ontology_service.query_ontology(onto, brand_name)
        generic_obj = brand_obj.isBrandOf
        generic_name = generic_obj.name
        interaction_ids = brand_obj.hasInteraction
        interactions = []
        
        print("Generic: ", generic_name)
        for interaction_id in interaction_ids:
                substance = interaction_id.interactsWith
                if target_substance.lower() == substance[0].name.lower():
                    description = interaction_id.hasInteractionDescription
                    clinical_effects = interaction_id.hasClinicalEffects
                    management_advice = interaction_id.hasManagementAdvice
                    
                    print("Brand: ", brand_name)
                    print("Substance: ", substance)
                    print("Description: ", description)
                    print("Clinical_effects", clinical_effects)
                    print("Management Advice:", management_advice)
    
    
    else:
        return "To get information about substance interactions with an antibiotic, please specify the antibiotic name or brand."

# need checking of results
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

    return "To get monitoring instructions for an antibiotic, please specify the antibiotic name or brand."

# need checking of results
def handle_storage_instruction(onto, entities, query_type):
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
        
        return "To get storage instructions for an antibiotic, please specify the antibiotic name or brand."

def handle_proper_use_of_medicine():
    return "To get information about the proper use of an antibiotic, please specify the antibiotic name or brand."

def handle_antibiotic_adherence():
    return "To get information about antibiotic adherence, please specify the antibiotic name or brand."

def handle_is_not_recognized():
    return "Sorry, I didn't understand your question. Please try rephrasing it or ask about a specific antibiotic or brand."

def handle_redirect_medicine_query():
    return "Redirecting to medicine query handler..."

def handle_get_general_answer():
    return "To get a general answer, please ask a specific question about antibiotics, their uses, side effects, interactions, or any other related topic."