from services.ontology_service import ontology_service
from services.response_service import response_service
from utils.helpers import add_space_to_pascal_case, split_commas, array_to_string

# TODO: check referencing for side effect (once data is finished), price when not specified

# Every method still needs to fetch the references and saving to a response

def handle_antibiotic_info(entities, query_type):
    
    if query_type == 'generic_brand':
        generic_name = entities.get('Antibiotic', [None])[0]
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(brand_name)
        generic_obj = ontology_service.query_ontology(generic_name)
        ontology_service.is_correct_generic(generic_name, brand_obj)

        presentation_obj = brand_obj.hasPresentation
        manufacturer = brand_obj.hasManufacturers
        distributor = brand_obj.hasDistributors
        content = brand_obj.hasContents
        reference = ontology_service.get_reference_from_entity(brand_obj)

        if len(presentation_obj) > 1:
            brand_info = {
                "brand" : brand_name, 
                "generic" : generic_name, 
                "manufacturer" : manufacturer[0], 
                "distributor" : distributor[0], 
                "content" : content[0], 
            }
            table_details = ontology_service.get_brand_presentations(presentation_obj)
            return response_service.build_antibiotic_multiple(brand_info, table_details, reference)
        
        elif len(presentation_obj) == 1:
            presentation, dosage, unit_price = ontology_service.get_presentation_details(presentation_obj[0])
            brand_info = {
                "brand" : brand_name, 
                "generic" : generic_name, 
                "manufacturer" : manufacturer[0], 
                "distributor" : distributor[0], 
                "content" : content[0], 
                "presentation" : presentation, 
                "dosage" : dosage, 
                "unit_price" : unit_price}
            return response_service.build_antibiotic_single(brand_info, reference)
        
        else:
            return response_service.build_text_response("No presentation data found.")


    elif query_type == 'generic':
        generic_name = entities.get('Antibiotic', [None])[0]
        generic_obj = ontology_service.query_ontology(generic_name)
        drug_class = generic_obj.hasDrugClass
        brands_obj = generic_obj.hasBrandName
        reference_list = ontology_service.get_reference_from_entities(brands_obj)

        generic_info = {
            "generic" : generic_name,
            "drug_class" :drug_class[0]
        }

        table_details = []
        for brand in brands_obj:
            presentation_obj = brand.hasPresentation
            table_details.extend(ontology_service.get_brand_presentations(presentation_obj))

        return response_service.build_antibiotic_generic(generic_info, table_details, reference_list)

    elif query_type == 'brand':
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(brand_name)
        generic_obj = brand_obj.isBrandOf
        generic_name = generic_obj.name
        presentation_obj = brand_obj.hasPresentation

        manufacturer = brand_obj.hasManufacturers
        distributor = brand_obj.hasDistributors
        content = brand_obj.hasContents
        reference = ontology_service.get_reference_from_entity(brand_obj)

        if len(presentation_obj) > 1:
            brand_info = {
                "brand" : brand_name, 
                "generic" : generic_name, 
                "manufacturer" : manufacturer[0], 
                "distributor" : distributor[0], 
                "content" : content[0], 
            }
            table_details = ontology_service.get_brand_presentations(presentation_obj)
            return response_service.build_antibiotic_multiple(brand_info, table_details, reference)
        
        elif len(presentation_obj) == 1:
            presentation, dosage, unit_price = ontology_service.get_presentation_details(presentation_obj[0])
            brand_info = {
                "brand" : brand_name, 
                "generic" : generic_name, 
                "manufacturer" : manufacturer[0], 
                "distributor" : distributor[0], 
                "content" : content[0], 
                "presentation" : presentation, 
                "dosage" : dosage, 
                "unit_price" : unit_price}
            return response_service.build_antibiotic_single(brand_info, reference)
        else:
            return response_service.build_text_response("No presentation data found.")
    else:
        return "Please specify the antibiotic name or brand for more information."

def handle_uses_indications(entities, query_type):
    if query_type == 'generic_brand':
        print("Handling uses and indications for generic_brand query type")
        generic_name = entities.get('Antibiotic', [None])[0]
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(brand_name)
        generic_obj = ontology_service.query_ontology(generic_name)
        ontology_service.is_correct_generic(generic_name, brand_obj)
        indication_obj = brand_obj.treats
        brand_ref = ontology_service.get_reference_from_entity(brand_obj)
        
        if len(indication_obj) == 1:
            indication, severity, disease_type = ontology_service.get_indication_severity_type(indication_obj[0])
            indication_ref = ontology_service.get_reference_from_entity(indication_obj[0])
            reference_list = ontology_service.combine_references(brand_ref, indication_ref)

            if severity:
                indication_final = f"{severity} {indication}"
            else:
                indication_final = indication
                
            symptoms_obj = indication_obj[0].hasSymptoms
            indication_info = {
                "brand" : brand_name,
                "generic" : generic_name,
                "disease" : indication_final,
            }

            symptoms_obj = indication_obj[0].hasSymptoms
            symptoms_array = split_commas(symptoms_obj)

            return response_service.build_indications_single(indication_info, symptoms_array, reference_list)
        
        else:
            indication_final = []
            symptoms_obj = []
            indication_ref = ontology_service.get_reference_from_entities(indication_obj)
            reference_list = ontology_service.combine_references(brand_ref, indication_ref)

            for indication in indication_obj:
                indication_name, severity, disease_type = ontology_service.get_indication_severity_type(indication)
                if severity:
                    indication_name = f"{severity} {indication_name}"
                indication_final.append(indication_name)
                symptoms = indication.hasSymptoms
                symptoms_obj.append(symptoms[0])

            indication_info = {
                "generic" : generic_name,
                "brand" :brand_name
            }
            
            return response_service.build_indications_multiple(indication_info, indication_final, symptoms_obj, reference_list)
        
    elif query_type == 'brand':
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(brand_name)
        brand_ref = ontology_service.get_reference_from_entity(brand_obj)
        
        generic_obj = brand_obj.isBrandOf
        generic_name = generic_obj.name
        
        indication_obj = brand_obj.treats
        
        if len(indication_obj) == 1:
            print("Single indication found.")
            
            indication, severity, disease_type = ontology_service.get_indication_severity_type(indication_obj[0])
            indication_ref = ontology_service.get_reference_from_entity(indication_obj[0])
            reference_list = ontology_service.combine_references(brand_ref, indication_ref)
            
            if severity:
                indication_final = f"{severity} {indication}"
            else:
                indication_final = indication
                
            symptoms_obj = indication_obj[0].hasSymptoms

            indication_info = {
                "brand" : brand_name,
                "generic" : generic_name,
                "disease" : indication_final,
            }

            symptoms_obj = indication_obj[0].hasSymptoms
            symptoms_array = split_commas(symptoms_obj)

            return response_service.build_indications_single(indication_info, symptoms_array, reference_list)
            
        else:
            print("Multiple indications found.")
            indication_final = []
            symptoms_obj = []
            indication_ref = ontology_service.get_reference_from_entities(indication_obj)
            reference_list = ontology_service.combine_references(brand_ref, indication_ref)

            for indication in indication_obj:
                indication_name, severity, disease_type = ontology_service.get_indication_severity_type(indication)
                if severity:
                    indication_name = f"{severity} {indication_name}"
                indication_final.append(indication_name)
                symptoms_obj.extend(indication.hasSymptoms)

            indication_info = {
                "generic" : generic_name,
                "brand" :brand_name
            }
            
            return response_service.build_indications_multiple(indication_info, indication_final, symptoms_obj, reference_list)
    
    elif query_type == 'generic':
        generic_name = entities.get('Antibiotic', [None])[0]
        generic_obj = ontology_service.query_ontology(generic_name)
        
        brands_obj = generic_obj.hasBrandName
        indication_final = []
        symptoms_obj = []
        table_details = []
        reference_list = ontology_service.get_reference_from_entities(brands_obj)
        
        for brand in brands_obj:
            indication_obj = brand.treats
            for indication in indication_obj:
                indication_name, severity, disease_type = ontology_service.get_indication_severity_type(indication)
                indication_ref = ontology_service.get_reference_from_entity(indication)
                reference_list = ontology_service.combine_references(reference_list, indication_ref)

                table_details.append([
                    indication_name,
                    disease_type,
                    severity or "N/A",
                    ", ".join(indication.hasSymptoms)
                ])

                if severity:
                    indication_name = f"{severity} {indication_name}"

                indication_final.append(indication_name)
                symptoms_obj.extend(indication.hasSymptoms)

        return response_service.build_indications_generic(generic_name, table_details, reference_list)
        
    return "To get information about the uses and indications of an antibiotic, please specify the antibiotic name or brand."

def handle_side_effects(entities, query_type):
    if query_type == 'generic_brand_side_effects':
        generic_name = entities.get('Antibiotic', [None])[0]
        brand_name = entities.get('Brand', [None])[0]
        target_side_effect = entities.get('SideEffect', [None])[0]
        brand_obj = ontology_service.query_ontology(brand_name)
        generic_obj = ontology_service.query_ontology(generic_name)
        reference_list = ontology_service.get_reference_from_entity(brand_obj)

        isFound = False
        side_effect_info = {
            "side_effect" : target_side_effect,
            "brand" : brand_name,
            "generic" : generic_name
        }

        for side_effect_instance in brand_obj.hasSideEffect:
            ontology_service_side_effect = side_effect_instance.is_a[0].name
            if target_side_effect.lower() == ontology_service_side_effect.lower():
                side_effect_ref = ontology_service.get_reference_from_entity(side_effect_instance)
                reference_list = ontology_service.combine_references(reference_list, side_effect_ref)
                isFound = True
            
        return response_service.build_side_effect_all_match(isFound, side_effect_info, reference_list)
            
    elif query_type == 'generic_brand':
        generic_name = entities.get('Antibiotic', [None])[0]
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(brand_name)
        generic_obj = ontology_service.query_ontology(generic_name)
        ontology_service.is_correct_generic(generic_name, brand_obj)
        brand_ref = ontology_service.get_reference_from_entity(brand_obj)

        side_effects = brand_obj.hasSideEffect
        side_effect_ref = ontology_service.get_reference_from_entities(side_effects)
        reference_list = ontology_service.combine_references(brand_ref, side_effect_ref)
        side_effects_list = []
        
        for side_effect in side_effects:
            side_effect_class = side_effect.is_a
            pattern_object = side_effect.hasPattern
            description = side_effect.hasSideEffectDescription
            
            if not pattern_object:
                pattern = None
            else:
                pattern = pattern_object[0].name

            side_effect = side_effect_class[0].name
            side_effects_list.append({
                "side_effect": side_effect,
                "pattern": pattern,
                "description": description[0]
            })

        info = {
            "brand": brand_name,
            "generic": generic_name,
        }

        return response_service.build_side_effect_generic_brand(info, side_effects_list, reference_list)

    elif query_type == 'generic':
        generic_name = entities.get('Antibiotic', [None])[0]
        generic_obj = ontology_service.query_ontology(generic_name)
        
        brands_obj = generic_obj.hasBrandName
        reference_list = ontology_service.get_reference_from_entities(brands_obj)
        brands_side_effects = []  # ← list of brands, each with their side effects

        for brand in brands_obj:
            brand_side_effects = brand.hasSideEffect
            side_effects_list = []

            side_effect_ref = ontology_service.get_reference_from_entities(brand_side_effects)
            reference_list = ontology_service.combine_references(reference_list, side_effect_ref)

            for side_effect in brand_side_effects:
                side_effect_class = side_effect.is_a
                pattern_object = side_effect.hasPattern

                description = side_effect.hasSideEffectDescription
            
                if not pattern_object:
                    pattern = None
                else:
                    pattern = pattern_object[0].name
                
                side_effect = side_effect_class[0].name
                side_effects_list.append({
                    "side_effect": side_effect,
                    "pattern": pattern,
                    "description": description[0]
                })

            brands_side_effects.append({
            "brand": brand.name,
            "side_effects": side_effects_list
            })

        # what you pass to response_service
        side_effect_info = {
            "generic": generic_name,
            "brands": brands_side_effects  # ← grouped by brand
        }

        return response_service.build_side_effect_generic(side_effect_info, reference_list)
                
    
    elif query_type == 'generic_side_effects':# have not tested
        generic_name = entities.get('Antibiotic', [None])[0]
        generic_obj = ontology_service.query_ontology(generic_name)
        target_side_effect = entities.get('SideEffect', [None])[0]
        
        brands_obj = generic_obj.hasBrandName
        reference_list = ontology_service.get_reference_from_entities(brands_obj)
        side_effects = []
        found_brands = []
        isFound = False
    
        for brand in brands_obj:
            print("Brand_side_effects", brand.hasSideEffect)
            for side_effect_instance in brand.hasSideEffect:
                ontology_service_side_effect = side_effect_instance.is_a[0].name
                print("ontology_service Side Effect: ", ontology_service_side_effect)
                if target_side_effect.lower() == ontology_service_side_effect.lower():
                    isFound= True
                    side_effect_ref = ontology_service.get_reference_from_entity(side_effect_instance)
                    reference_list = ontology_service.combine_references(reference_list, side_effect_ref)
                    side_effects.append(side_effect_instance)
                    found_brands.append(brand)
        
        side_effect_info = {
            "generic" :generic_name,
            "brands" : array_to_string(found_brands),
            "side_effect": target_side_effect
        }

        return response_service.build_side_effect_generic_match(isFound, side_effect_info, reference_list )

    elif query_type == 'brand':
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(brand_name)
        brand_ref = ontology_service.get_reference_from_entity(brand_obj)

        side_effects = brand_obj.hasSideEffect
        side_effect_ref = ontology_service.get_reference_from_entities(side_effects)
        reference_list = ontology_service.combine_references(brand_ref, side_effect_ref)
        side_effects_list = []
        
        for side_effect in side_effects:
            side_effect_class = side_effect.is_a
            pattern_object = side_effect.hasPattern
            description = side_effect.hasSideEffectDescription
            
            if not pattern_object:
                pattern = None
            else:
                pattern = pattern_object[0].name

            side_effect = side_effect_class[0].name
            side_effects_list.append({
                "side_effect": side_effect,
                "pattern": pattern,
                "description": description[0]
            })

        return response_service.build_side_effect_brand(brand_name, side_effects_list, reference_list)

    elif query_type == 'brand_side_effects':
        brand_name = entities.get('Brand', [None])[0]
        target_side_effect = entities.get('SideEffect', [None])[0]
        brand_obj = ontology_service.query_ontology(brand_name)
        reference_list = ontology_service.get_reference_from_entity(brand_obj)

        isFound = False
        side_effect_info = {
            "side_effect" : target_side_effect,
            "brand" : brand_name,
        }

        for side_effect_instance in brand_obj.hasSideEffect:
            ontology_service_side_effect = side_effect_instance.is_a[0].name
            if target_side_effect.lower() == ontology_service_side_effect.lower():
                side_effect_ref = ontology_service.get_reference_from_entity(side_effect_instance)
                reference_list = ontology_service.combine_references(reference_list, side_effect_ref)
                isFound = True
            
        return response_service.build_side_effect_brand_match(isFound, side_effect_info, reference_list)
    
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

def handle_storage_instruction(entities, query_type):
    if query_type == 'generic':
        generic_name = entities.get('Antibiotic', [None])[0]
        generic_obj = ontology_service.query_ontology(generic_name)
        brands_obj = generic_obj.hasBrandName
        reference_list = []
        brands_storage = []

        for brand in brands_obj:
            storage_rules = []
            for storage_id in brand.hasStorageRule:
                storage_rule = storage_id.hasStewardshipDescription
                storage_rules.append(storage_rule[0] if isinstance(storage_rule, list) else storage_rule)
            
            brands_storage.append({
                "brand": brand.name,
                "storage_rules": storage_rules  # ← empty list if no rules
            })
            reference_list.extend(ontology_service.get_reference_from_entity(brand))

        storage_info = {"generic": generic_name, "brands": brands_storage}
        return response_service.build_storage_generic(storage_info, reference_list)
            
    elif query_type == 'generic_brand':
        generic_name = entities.get('Antibiotic', [None])[0]
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(brand_name)
        ontology_service.is_correct_generic(generic_name, brand_obj)
        storage_rules = []
        
        reference_list = ontology_service.get_reference_from_entities(brand_obj.hasStorageRule)
        for storage_id in brand_obj.hasStorageRule:
            storage_rule = storage_id.hasStewardshipDescription
            storage_rules.append(storage_rule[0])
        
    elif query_type == 'brand':
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(brand_name)
        generic_obj = brand_obj.isBrandOf
        generic_name = generic_obj.name
        storage_rules = []
        
        reference_list = ontology_service.get_reference_from_entities(brand_obj.hasStorageRule)
        for storage_id in brand_obj.hasStorageRule:
            storage_rule = storage_id.hasStewardshipDescription
            storage_rules.append(storage_rule[0])
    
    else:
        return "To get storage instructions for an antibiotic, please specify the antibiotic name or brand."

    antibiotic_info = {
        "generic": generic_name,
        "brand" : brand_name
    }
    if len(storage_rules) > 1:
        return response_service.build_storage_multiple(antibiotic_info, storage_rules, reference_list)
    elif len(storage_rules) == 1:
        return response_service.build_storage_single(antibiotic_info, storage_rules, reference_list)
    else:
        reference_list = ontology_service.get_reference_from_entity(brand_obj)
        return response_service.build_storage_none(antibiotic_info, reference_list)

def handle_food_and_timing(entities, query_type):
    if query_type == 'generic':
        generic_name = entities.get('Antibiotic', [None])[0]
        generic_obj = ontology_service.query_ontology(generic_name)
        brands_obj = generic_obj.hasBrandName
        reference_list = []
        brands_food_and_timing= []

        for brand in brands_obj:
            food_and_timing_rules = []
            for food_timing_id in brand.hasFoodAndTimingRule:
                food_and_timing_rule = food_timing_id.hasStewardshipDescription
                food_and_timing_rules.append(food_and_timing_rule[0] if isinstance(food_and_timing_rule, list) else food_and_timing_rule)
            
            brands_food_and_timing.append({
                "brand": brand.name,
                "food_and_timing_rules": food_and_timing_rules
            })
            reference_list.extend(ontology_service.get_reference_from_entity(brand))

        food_and_timing_info = {"generic": generic_name, "brands": brands_food_and_timing}
        return response_service.build_food_and_timing_generic(food_and_timing_info, reference_list)
            
    elif query_type == 'generic_brand':
        generic_name = entities.get('Antibiotic', [None])[0]
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(brand_name)
        ontology_service.is_correct_generic(generic_name, brand_obj)
        food_and_timing_rules = []
        
        reference_list = ontology_service.get_reference_from_entities(brand_obj.hasFoodAndTimingRule)
        for food_timing_id in brand_obj.hasFoodAndTimingRule:
            food_and_timing_rule = food_timing_id.hasStewardshipDescription
            food_and_timing_rules.append(food_and_timing_rule[0])
        
    elif query_type == 'brand':
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(brand_name)
        generic_obj = brand_obj.isBrandOf
        generic_name = generic_obj.name
        food_and_timing_rules = []
        
        reference_list = ontology_service.get_reference_from_entities(brand_obj.hasFoodAndTimingRule)
        for food_timing_id in brand_obj.hasFoodAndTimingRule:
            food_and_timing_rule = food_timing_id.hasStewardshipDescription
            food_and_timing_rules.append(food_and_timing_rule[0])
    
    else:
        return "To get food and timing for an antibiotic, please specify the antibiotic name or brand."

    antibiotic_info = {
        "generic": generic_name,
        "brand" : brand_name
    }
    if len(food_and_timing_rules) > 1:
        return response_service.build_food_and_timing_multiple(antibiotic_info, food_and_timing_rules, reference_list)
    elif len(food_and_timing_rules) == 1:
        print(reference_list)
        return response_service.build_food_and_timing_single(antibiotic_info, food_and_timing_rules, reference_list)
    else:
        reference_list = ontology_service.get_reference_from_entity(brand_obj)
        return response_service.build_food_and_timing_none(antibiotic_info, reference_list)

def handle_administration_instructions(entities, query_type):
    if query_type == 'generic':
        generic_name = entities.get('Antibiotic', [None])[0]
        generic_obj = ontology_service.query_ontology(generic_name)
        brands_obj = generic_obj.hasBrandName
        reference_list = []
        brands_administration = []

        for brand in brands_obj:
            administration_rules = []
            for administration_id in brand.hasAdministrationAndAdherenceRule:
                administration_rule = administration_id.hasStewardshipDescription
                administration_rules.append(administration_rule[0] if isinstance(administration_rule, list) else administration_rule)
            
            brands_administration.append({
                "brand": brand.name,
                "administration_rules": administration_rules  # ← empty list if no rules
            })
            reference_list.extend(ontology_service.get_reference_from_entity(brand))

        administration_info = {"generic": generic_name, "brands": brands_administration}
        return response_service.build_administration_generic(administration_info, reference_list)
            
    elif query_type == 'generic_brand':
        generic_name = entities.get('Antibiotic', [None])[0]
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(brand_name)
        ontology_service.is_correct_generic(generic_name, brand_obj)
        administration_rules = []
        
        reference_list = ontology_service.get_reference_from_entities(brand_obj.hasAdministrationAndAdherenceRule)
        for administration_id in brand_obj.hasAdministrationAndAdherenceRule:
            administration_rule = administration_id.hasStewardshipDescription
            administration_rules.append(administration_rule[0])
        
    elif query_type == 'brand':
        brand_name = entities.get('Brand', [None])[0]
        brand_obj = ontology_service.query_ontology(brand_name)
        generic_obj = brand_obj.isBrandOf
        generic_name = generic_obj.name
        administration_rules = []
        
        reference_list = ontology_service.get_reference_from_entities(brand_obj.hasAdministrationAndAdherenceRule)
        for administration_id in brand_obj.hasAdministrationAndAdherenceRule:
            administration_rule = administration_id.hasStewardshipDescription
            administration_rules.append(administration_rule[0])
    
    else:
        return "To get administration guidelines for an antibiotic, please specify the antibiotic name or brand."

    antibiotic_info = {
        "generic": generic_name,
        "brand" : brand_name
    }
    if len(administration_rules) > 1:
        return response_service.build_administration_multiple(antibiotic_info, administration_rules, reference_list)
    elif len(administration_rules) == 1:
        return response_service.build_administration_single(antibiotic_info, administration_rules, reference_list)
    else:
        reference_list = ontology_service.get_reference_from_entity(brand_obj)
        return response_service.build_administration_none(antibiotic_info, reference_list)

def handle_is_not_recognized():
    return "Sorry, I didn't understand your question. Please try rephrasing it or ask about a specific antibiotic or brand."

def handle_redirect_medicine_query():
    return "Redirecting to medicine query handler..."
