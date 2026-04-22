import services.response_service as response_service
from utils.helpers import array_to_string, is_yes_or_no, add_space_to_pascal_case
from services.ontology_service import query_ontology, get_indication_severity_type, get_references_list, get_single_reference

def handle_antibiotic_info(entities, ontology, response_index):
    if len(entities) > 1: # brand and generic recognized
        print("BRAND AND GENERIC")
        isBrand = False
        generic_name = entities[0]
        generic_obj = query_ontology(ontology, generic_name)

        brand_name = entities[1] 
        brand_obj = query_ontology(ontology, brand_name)

        reference = get_single_reference(brand_obj)

        if brand_obj.isBrandOf[0] == generic_obj:
            isBrand = True
        
        presentation_obj = brand_obj.hasPresentation

        template = response_service.get_response_template("GET_ANTIBIOTIC_INFO", "brand_and_generic", response_index)
        response = template['responseText'].format(
            is_brand_of = is_yes_or_no(isBrand),
            brand=brand_name,
            generic=generic_name,
            presentation= array_to_string(presentation_obj),
        )

        text_json = response_service.build_text_response(response)
        responses = [text_json, reference]
        return response_service.build_composite_response(responses)

    elif entities[0] in ["Doxin", "Dynadoxy", "Doxyclen", "Biogesic"]:   # brand recognized    
        brand_name = entities[0]
        brand_obj = query_ontology(ontology, brand_name)

        generic_obj = brand_obj.isBrandOf
        brands_obj = generic_obj[0].hasBrandName
        reference_list = get_references_list(brands_obj)
        brands = list(brands_obj)
        brands.remove(brand_obj)

        drug_class = generic_obj[0].hasDrugClass
        presentation_obj = brand_obj.hasPresentation

        template = response_service.get_response_template("GET_ANTIBIOTIC_INFO", "brand_only", response_index)
        response = template['responseText'].format(
            brand=brand_name,
            generic=generic_obj[0].name,
            drug_class=drug_class[0].name,
            presentation=array_to_string(presentation_obj),
            other_brands=array_to_string(brands)
        )

        text_json = response_service.build_text_response(response)
        responses = [text_json, reference_list]
        return response_service.build_composite_response(responses)
    
    elif entities[0] in ["Doxycycline", "Paracetamol"]: # generic recognized
        generic_name = entities[0] if entities else None
        generic_obj = query_ontology(ontology, generic_name)
        
        drug_class = generic_obj.hasDrugClass
        brand_obj = generic_obj.hasBrandName
        reference_list = get_references_list(brand_obj)

        template = response_service.get_response_template("GET_ANTIBIOTIC_INFO", "generic_only", response_index)
        response = template['responseText'].format(
            generic = generic_name,
            drug_class = drug_class[0].name       
        )

        columns = ["Brand Name", "Presentation/Packing"]
        rows = []

        for brand in brand_obj:
            presentation_obj = brand.hasPresentation
            for presentation in presentation_obj:
                row = [brand.name, add_space_to_pascal_case(presentation.name)]
                rows.append(row)

        text_json = response_service.build_text_response(response)
        table_json = response_service.build_table_response(columns, rows)
        responses = [text_json, table_json, reference_list]
        return response_service.build_composite_response(responses)

def handle_compare_brands (entities, ontology, response_index):
    if entities[0] in ["Doxycycline", "Paracetamol"]: # generic recognized
        generic_name = entities[0]
        generic_obj = query_ontology(ontology, generic_name)
        
        brands_obj = generic_obj.hasBrandName
        reference_list = get_references_list(brands_obj)

        template = response_service.get_response_template("COMPARE_BRANDS", "generic_only", response_index)

        response = template['responseText'].format(
            generic = generic_name
        )

        columns = ["Brand Name", "Presentation/Packing"]
        rows = []

        for brand in brands_obj:
            presentation_obj = brand.hasPresentation
            for presentation in presentation_obj:
                row = [brand.name, add_space_to_pascal_case(presentation.name)]
                rows.append(row)

        text_json = response_service.build_text_response(response)
        table_json = response_service.build_table_response(columns, rows)
        responses = [text_json, table_json, reference_list]
        return response_service.build_composite_response(responses)

    elif len(entities) > 1 and entities[1] == "Doxycycline": # brand and generic recognized
        brand_name = entities[0]
        brand_obj = query_ontology(ontology, brand_name)
        
        generic_name = entities[1]
        generic_obj = query_ontology(ontology, generic_name)

        brands = list(generic_obj.hasBrandName)
        brands.remove(brand_obj)
        brands_obj = generic_obj.hasBrandName
        reference_list = get_references_list(brands_obj)

        presentation_obj = brand_obj.hasPresentation
        
        template = response_service.get_response_template("COMPARE_BRANDS", "brand_and_generic", response_index)
        
        response = template['responseText'].format(
            brand = brand_name,
            generic = generic_name,
            presentation = array_to_string(presentation_obj)
        )

        columns = ["Brand Name", "Presentation/Packing"]
        rows = []

        for brand in brands_obj:
            presentation_obj = brand.hasPresentation
            for presentation in presentation_obj:
                row = [brand.name, add_space_to_pascal_case(presentation.name)]
                rows.append(row)

        text_json = response_service.build_text_response(response)
        table_json = response_service.build_table_response(columns, rows)
        responses = [text_json, table_json], reference_list
        return response_service.build_composite_response(responses)

    elif entities[0] in ["Doxin", "Dynadoxy", "Doxyclen", "Paracetamol"]: # multiple brands recognized
        if len(entities) < 2:
            return response_service.build_text_response("Apologies. I need at least 2 brands to compare them")

        brands_obj = []
        baseline_generic = ""
        baseline_brand = ""

        for brand in entities: # check if brand exists and same generic
            brand_obj = query_ontology(ontology, brand)
            brands_obj.append(brand_obj)

            if (not baseline_generic) and (not baseline_brand):
                baseline_generic = brand_obj.isBrandOf
                print("IN FOR LOOP", baseline_generic)
                baseline_brand = brand_obj.name
            elif (baseline_generic != brand_obj.isBrandOf):
                current_generic = brand_obj.isBrandOf
                print(baseline_generic)
                print(current_generic)
                return response_service.build_text_response(f"The antibiotics have different generic names. {brand} has generic name of {current_generic[0].name}, while {baseline_brand} has generic name of {baseline_generic[0].name}")

        template = response_service.get_response_template("COMPARE_BRANDS", "multiple_brands", response_index)
        response = template['responseText'].format(
            brands = array_to_string(brands_obj),
            generic = baseline_generic[0].name
        )

        columns = ["Brand Name", "Presentation/Packing"]
        rows = []

        reference_list = get_references_list(brands_obj)
        for brand in brands_obj:
            presentation_obj = brand.hasPresentation
            for presentation in presentation_obj:
                row = [brand.name, add_space_to_pascal_case(presentation.name)]
                rows.append(row)

        text_json = response_service.build_text_response(response)
        table_json = response_service.build_table_response(columns, rows)
        responses = [text_json, table_json, reference_list]
        return response_service.build_composite_response(responses)

def handle_uses_indications(entities, ontology, response_index):
    if len(entities) > 1: # both generic and brand recognized

        brand_name = entities[0]
        generic_name = entities[1] 

        brand_obj = query_ontology(ontology, brand_name)

        
        generic_obj = query_ontology(ontology, generic_name)

        
        indication_obj = brand_obj.treats

        if len(indication_obj) == 1: # single indication
            severity, disease_type = get_indication_severity_type(indication_obj[0])
            indication = add_space_to_pascal_case(indication_obj[0].name)

            if severity: # Checking if severity is not specified
                indication_final = f"{severity} {indication}"
            else:
                indication_final = indication

            template = response_service.get_response_template("GET_USES_INDICATIONS", "single_indication", response_index)
            response = template['responseText'].format(
                brand = brand_name,
                generic = generic_name,
                disease = indication_final,
                disease_type = disease_type
            )

            symptoms_obj = indication_obj[0].hasSymptoms
            symptoms_array = symptoms_obj[0].split(',')

            symptom_bullets = []

            for symptom in symptoms_array:
                bullet = response_service.build_bullet(description=symptom)
                symptom_bullets.append(bullet)

            text_json = response_service.build_text_response(response)
            bulleted_json = response_service.build_bulleted_response(symptom_bullets)
            responses = [text_json, bulleted_json]

            return response_service.build_composite_response(responses)

        if len(indication_obj) > 1: # multiple indications
            indication_bullets = []
            for indication in indication_obj:
                severity, disease_type = get_indication_severity_type(indication)
                indication_name = indication.name
                symptoms_obj = indication.hasSymptoms

                if severity: # Checking if severity is not specified
                    indication_final = f"{severity} {indication_name}"
                else:
                    indication_final = indication_name
                
                bullet = response_service.build_bullet(main_text=add_space_to_pascal_case(indication_final), description="Typically have symptoms such as " + symptoms_obj[0])
                indication_bullets.append(bullet)
            
            template = response_service.get_response_template("GET_USES_INDICATIONS", "multiple_indications", response_index)
            response = template['responseText'].format(
                brand = brand_name,
                generic = generic_name
            )

            text_json = response_service.build_text_response(response)
            bulleted_json = response_service.build_bulleted_response(indication_bullets)
            responses = [text_json, bulleted_json]
            return response_service.build_composite_response(responses)
    elif (entities[0] in ["Doxin", "Doxyclen", "Dynadoxy"]): # brand recognized
        brand_name = entities[0]
        brand_obj = query_ontology(ontology, brand_name)
        
        generic_obj = brand_obj.isBrandOf
        generic_name = generic_obj[0].name

        indication_obj = brand_obj.treats

        if len(indication_obj) == 1: # single indication
            severity, disease_type = get_indication_severity_type(indication_obj[0])
            indication = add_space_to_pascal_case(indication_obj[0].name)

            if severity: # Checking if severity is not specified
                indication_final = f"{severity} {indication}"
            else:
                indication_final = indication

            template = response_service.get_response_template("GET_USES_INDICATIONS", "single_indication", response_index)
            response = template['responseText'].format(
                brand = brand_name,
                generic = generic_name,
                disease = indication_final,
                disease_type = disease_type
            )

            symptoms_obj = indication_obj[0].hasSymptoms
            symptoms_array = symptoms_obj[0].split(',')

            symptom_bullets = []

            for symptom in symptoms_array:
                bullet = response_service.build_bullet(description=symptom)
                symptom_bullets.append(bullet)

            text_json = response_service.build_text_response(response)
            bulleted_json = response_service.build_bulleted_response(symptom_bullets)
            responses = [text_json, bulleted_json]

            return response_service.build_composite_response(responses)

        if len(indication_obj) > 1: # multiple indications
            indication_bullets = []
            for indication in indication_obj:
                severity, disease_type = get_indication_severity_type(indication)
                indication_name = indication.name
                symptoms_obj = indication.hasSymptoms

                if severity: # Checking if severity is not specified
                    indication_final = f"{severity} {indication_name}"
                else:
                    indication_final = indication_name
                
                bullet = response_service.build_bullet(main_text=add_space_to_pascal_case(indication_final), description="Typically have symptoms such as " + symptoms_obj[0])
                indication_bullets.append(bullet)
            
            template = response_service.get_response_template("GET_USES_INDICATIONS", "multiple_indications", response_index)
            response = template['responseText'].format(
                brand = brand_name,
                generic = generic_name
            )

            text_json = response_service.build_text_response(response)
            bulleted_json = response_service.build_bulleted_response(indication_bullets)
            responses = [text_json, bulleted_json]
            return response_service.build_composite_response(responses)
    elif (entities[0] in ["Doxycycline", "Paracetamol"]): # generic recognized
        generic_name = entities[0]
        generic_obj = query_ontology(ontology, generic_name)
        
        template = response_service.get_response_template("GET_USES_INDICATIONS", "generic_only", response_index)
        response = template['responseText'].format (
            generic = generic_name
        )

        brands_obj = generic_obj.hasBrandName
        columns = ["Brand Name", "Indications/Uses"]
        rows = []

        for brand in brands_obj:
            indication_obj = brand.treats
            row = [brand.name, array_to_string(indication_obj)]
            rows.append(row)

        text_json = response_service.build_text_response(response)
        table_json = response_service.build_table_response(columns, rows)
        responses = [text_json, table_json]
        return response_service.build_composite_response(responses)

def handle_side_effects(entities, ontology, response_index):
    if  (len(entities) == 3): # generic, brand and side effect found
        brand_name = entities[0]
        brand_obj = query_ontology(ontology, brand_name)

        generic_name = entities[1]
        generic_obj = query_ontology(ontology, generic_name)

        target_side_effect = entities[2] 

        isFound = False

        for side_effect_instance in brand_obj.hasSideEffect:
                onto_side_effect_name = side_effect_instance.is_a[0].name
                if target_side_effect.lower() == onto_side_effect_name.lower():
                    isFound = True
        
        if not(isFound):
            print("NOT FOUND")
            template = response_service.get_response_template("GET_SIDE_EFFECTS", "generic_brand_verify_no_match", response_index)
            response = template['responseText'].format(
                side_effect = target_side_effect,
                generic = generic_name,
                brand = brand_name, 
            )
            return response_service.build_text_response(response)
        else:
            print("FOUND")
            template = response_service.get_response_template("GET_SIDE_EFFECTS", "generic_brand_verify_match", response_index)
            response = template['responseText'].format(
                side_effect = target_side_effect,
                brand = brand_name,
                generic = generic_name
            )
            return response_service.build_text_response(response)
    elif (len(entities) ==  2) and (entities[0] in ["Doxin", "Doxyclen", "Dynadoxy"]) and (entities[1] in ["Doxycycline"]): # brand and generic recognized
        brand_name = entities[0]
        generic_name = entities[1]
        brand_obj = query_ontology(ontology, brand_name)

        template = response_service.get_response_template("GET_SIDE_EFFECTS", "generic_brand_only", response_index)
        response = template['responseText'].format(
            brand = brand_name,
            generic = generic_name
        )
        text_json = response_service.build_text_response(response)

        responses = [text_json]

        side_effects_obj = brand_obj.hasSideEffect
        side_effects = []

        for side_effect in side_effects_obj:
            side_effect_class = side_effect.is_a
            pattern_obj  = side_effect.whichIs
            duration_obj = side_effect.lastsFor
            description = side_effect.hasSideEffectDescription

            if "FrequencyNotReported" in pattern_obj[0].name: # no occurrence pattern specified
                template = response_service.get_response_template("GET_SIDE_EFFECTS", "generic_brand_only", response_index)
                bullet_main_text = template['bulletNoPattern'].format(
                side_effect = side_effect_class[0].name,
                )
            else: # occurrence pattern is specified 
                template = response_service.get_response_template("GET_SIDE_EFFECTS", "generic_brand_only", response_index)
                bullet_main_text = template['bulletWithPattern'].format(
                    side_effect = side_effect_class[0].name,
                    pattern =pattern_obj[0].name,
                )

            if "DurationNotReported" in duration_obj[0].name: # template for bullet description with no duration
                template = response_service.get_response_template("GET_SIDE_EFFECTS", "generic_brand_only", response_index)
                bullet_desc = template['descNoDuration'].format(
                    description = description[0]
                )
            else: # template for bullet description with duration
                template = response_service.get_response_template("GET_SIDE_EFFECTS", "generic_brand_only", response_index)
                bullet_desc = template['descWithDuration'].format(
                    description = description[0],
                    duration = add_space_to_pascal_case(duration_obj[0].name)
                )

            bullet_json = response_service.build_bullet(bullet_main_text, bullet_desc)
            side_effects.append(bullet_json)

        responses.append(response_service.build_bulleted_response(side_effects))
        return response_service.build_composite_response(responses)
    elif (len(entities) == 1 and entities[0] in ["Doxycycline"]): # generic is found
        generic_name = entities[0]
        generic_obj = query_ontology(ontology, generic_name)

        template = response_service.get_response_template("GET_SIDE_EFFECTS", "generic_only", response_index)
        response = template['responseText'].format(
            generic = generic_name
        )
        text_json = response_service.build_text_response(response)

        responses = [text_json]

        brand_obj = generic_obj.hasBrandName

        for brand in brand_obj:
            side_effects = []
            header_json = response_service.build_header_response(brand.name)
            responses.append(header_json)
            side_effects_obj = brand.hasSideEffect

            for side_effect in side_effects_obj:
                side_effect_class = side_effect.is_a
                pattern_obj  = side_effect.whichIs
                duration_obj = side_effect.lastsFor
                description = side_effect.hasSideEffectDescription

                if "FrequencyNotReported" in pattern_obj[0].name: # no occurrence pattern specified
                    template = response_service.get_response_template("GET_SIDE_EFFECTS", "generic_only", response_index)
                    bullet_main_text = template['bulletNoPattern'].format(
                        side_effect = side_effect_class[0].name,
                    )
                else: # occurrence pattern is specified 
                    template = response_service.get_response_template("GET_SIDE_EFFECTS", "generic_only", response_index)
                    bullet_main_text = template['bulletWithPattern'].format(
                        side_effect = side_effect_class[0].name,
                        pattern =pattern_obj[0].name,
                        generic = generic_name
                    )

                if "DurationNotReported" in duration_obj[0].name: # template for bullet description with no duration
                    template = response_service.get_response_template("GET_SIDE_EFFECTS", "generic_only", response_index)
                    bullet_desc = template['descNoDuration'].format(
                        description = description[0]
                    )
                else: # template for bullet description with duration
                    template = response_service.get_response_template("GET_SIDE_EFFECTS", "generic_only", response_index)
                    bullet_desc = template['descWithDuration'].format(
                        description = description[0],
                        duration = add_space_to_pascal_case(duration_obj[0].name)
                    )
                bullet_json = response_service.build_bullet(bullet_main_text, bullet_desc)
                side_effects.append(bullet_json)

            responses.append(response_service.build_bulleted_response(side_effects))
        return response_service.build_composite_response(responses)
    elif (len(entities) == 2 and entities[0] in ["Doxycycline"]): # generic and side effect is found
        generic_name = entities[0]
        generic_obj = query_ontology(ontology, generic_name)
        
        target_side_effect = entities[1] 
        found_brands = []

        brands_obj = generic_obj.hasBrandName

        for brand in brands_obj:
            for side_effect_instance in brand.hasSideEffect:
                onto_side_effect_name = side_effect_instance.is_a[0].name
                if target_side_effect.lower() == onto_side_effect_name.lower():
                    if brand.name not in found_brands:
                        found_brands.append(brand)
                    break 
        
        if len(found_brands) < 1:
            template = response_service.get_response_template("GET_SIDE_EFFECTS", "generic_verify_no_match", response_index)
            response = template['responseText'].format(
                side_effect = target_side_effect,
                generic = generic_name, 
            )
            return response_service.build_text_response(response)
        else:
            template = response_service.get_response_template("GET_SIDE_EFFECTS", "generic_verify_match", response_index)
            response = template['responseText'].format(
                side_effect = target_side_effect,
                generic = generic_name, 
                brands = array_to_string(found_brands)
            )
            return response_service.build_text_response(response)
    elif (len(entities) == 1 and entities [0] in ["Doxin", "Dynadoxy", "Doxyclen"]): # brand is recognized
        brand_name = entities[0]
        brand_obj = query_ontology(ontology, brand_name)

        template = response_service.get_response_template("GET_SIDE_EFFECTS", "brand_only", response_index)
        response = template['responseText'].format(
            brand = brand_name
        )
        text_json = response_service.build_text_response(response)

        responses = [text_json]

        side_effects_obj = brand_obj.hasSideEffect
        side_effects = []

        for side_effect in side_effects_obj:
            side_effect_class = side_effect.is_a
            pattern_obj  = side_effect.whichIs
            duration_obj = side_effect.lastsFor
            description = side_effect.hasSideEffectDescription

            if "FrequencyNotReported" in pattern_obj[0].name: # no occurrence pattern specified
                template = response_service.get_response_template("GET_SIDE_EFFECTS", "brand_only", response_index)
                bullet_main_text = template['bulletNoPattern'].format(
                side_effect = side_effect_class[0].name,
                )
            else: # occurrence pattern is specified 
                template = response_service.get_response_template("GET_SIDE_EFFECTS", "brand_only", response_index)
                bullet_main_text = template['bulletWithPattern'].format(
                    side_effect = side_effect_class[0].name,
                    pattern =pattern_obj[0].name,
                )

            if "DurationNotReported" in duration_obj[0].name: # template for bullet description with no duration
                template = response_service.get_response_template("GET_SIDE_EFFECTS", "brand_only", response_index)
                bullet_desc = template['descNoDuration'].format(
                    description = description[0]
                )
            else: # template for bullet description with duration
                template = response_service.get_response_template("GET_SIDE_EFFECTS", "brand_only", response_index)
                bullet_desc = template['descWithDuration'].format(
                    description = description[0],
                    duration = add_space_to_pascal_case(duration_obj[0].name)
                )

            bullet_json = response_service.build_bullet(bullet_main_text, bullet_desc)
            side_effects.append(bullet_json)

        responses.append(response_service.build_bulleted_response(side_effects))
        return response_service.build_composite_response(responses)
    elif (len(entities) == 2 and entities[0] in ["Doxin", "Dynadoxy", "Doxyclen"]): # brand and side effect is found
        brand_name = entities[0]
        brand_obj = query_ontology(ontology, brand_name)
        target_side_effect = entities[1] 

        isFound = False

        for side_effect_instance in brand_obj.hasSideEffect:
                onto_side_effect_name = side_effect_instance.is_a[0].name
                if target_side_effect.lower() == onto_side_effect_name.lower():
                    isFound = True
        
        if not(isFound):
            print("NOT FOUND")
            template = response_service.get_response_template("GET_SIDE_EFFECTS", "brand_verify_no_match", response_index)
            response = template['responseText'].format(
                side_effect = target_side_effect,
                brand = brand_name, 
            )
            return response_service.build_text_response(response)
        else:
            print("FOUND")
            template = response_service.get_response_template("GET_SIDE_EFFECTS", "brand_verify_match", response_index)
            response = template['responseText'].format(
                side_effect = target_side_effect,
                brand = brand_name
            )
            return response_service.build_text_response(response)

            



