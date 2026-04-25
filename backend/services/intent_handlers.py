import services.response_service as response_service
from utils.helpers import array_to_string, is_yes_or_no, add_space_to_pascal_case
import services.ontology_service as ontology_service

def handle_antibiotic_info(entities, ontology, response_index):
    if len(entities) > 1: # brand and generic recognized
        generic_name = entities[0]
        brand_name = entities[1] 
        brand_obj = ontology_service.query_ontology(ontology, brand_name)
        return _build_brand_overview_response(brand_obj, generic_name, response_index)
    elif entities[0] in ["Doxin", "Dynadoxy", "Doxyclen", "Biogesic", "Levocin"]:   # brand recognized    
        brand_name = entities[0]
        brand_obj = ontology_service.query_ontology(ontology, brand_name)
        generic_obj = brand_obj.isBrandOf
        generic_name = generic_obj.name
        return _build_brand_overview_response(brand_obj, generic_name, response_index)
    elif entities[0] in ["Doxycycline", "Paracetamol"]: # generic recognized
        generic_name = entities[0] if entities else None
        generic_obj = ontology_service.query_ontology(ontology, generic_name)

from services.ontology_service import query_ontology, get_indication_severity_type

def handle_antibiotic_info(entities, ontology, response_index):
    if len(entities) > 1: # brand and generic recognized
        isBrand = False
        generic_name = entities[0] if entities else None
        generic_obj = query_ontology(ontology, generic_name)

        if isinstance(generic_obj, dict): # check if error
            return generic_obj
        
        brand_name = entities[1] if entities else None
        brand_obj = query_ontology(ontology, brand_name)

        if isinstance(brand_obj, dict): # check if error
            return brand_obj

        if brand_obj.isBrandOf[0] == generic_obj:
            isBrand = True
        
        presentation_obj = brand_obj.hasPresentation

        template = response_service.get_response_template("GET_ANTIBIOTIC_INFO", "brand_and_generic", response_index)
        response = template.format(
            is_brand_of = is_yes_or_no(isBrand),
            brand=brand_name,
            generic=generic_name,
            presentation= array_to_string(presentation_obj),
        )
        return response_service.build_text_response(response)

    elif entities[0] in ["Doxin", "Dynadoxy", "Doxyclen", "Biogesic"]:        
        brand_name = entities[0] if entities else None
        brand_obj = query_ontology(ontology, brand_name)

        if isinstance(brand_obj, dict): # check for errors
            return brand_obj
        
        presentation_obj = brand_obj.hasPresentation

        generic_obj = brand_obj.isBrandOf
        brands = generic_obj[0].hasBrandName
        brands.remove(brand_obj)
        drug_class = generic_obj[0].hasDrugClass

        template = response_service.get_response_template("GET_ANTIBIOTIC_INFO", "brand_only", response_index)
        response = template.format(
            brand=brand_name,
            generic=generic_obj[0].name,
            drug_class=drug_class[0].name,
            presentation=array_to_string(presentation_obj),
            other_brands=array_to_string(brands)
        )

        return response_service.build_text_response(response)
    
    elif entities[0] in ["Doxycycline", "Paracetamol"]:
        generic_name = entities[0] if entities else None
        generic_obj = query_ontology(ontology, generic_name)

        if isinstance(generic_obj, dict):
            return generic_obj
        

        drug_class = generic_obj.hasDrugClass
        brands_obj = generic_obj.hasBrandName

        template = response_service.get_response_template("GET_ANTIBIOTIC_INFO", "generic_only", response_index)
        response = template['responseText'].format(
            generic = generic_name,
            drug_class = drug_class       
        )

        text_json = response_service.build_text_response(response)
        table_json, reference_list = _generate_generic_overview_table(brands_obj, template['columns'])
        return response_service.build_composite_response(text_json, table_json, reference_list)
 
def handle_compare_brands (entities, ontology, response_index):
    if entities[0] in ["Doxycycline", "Paracetamol"]: # generic recognized
        generic_name = entities[0]
        generic_obj = ontology_service.query_ontology(ontology, generic_name)
        brands_obj = generic_obj.hasBrandName

        template = response_service.get_response_template("COMPARE_BRANDS", "generic_only", response_index)
        response = template['responseText'].format(
            generic = generic_name
        )

        text_json = response_service.build_text_response(response)
        table_json, reference_list = _generate_generic_overview_table(brands_obj, template['columns'])
        responses = [text_json, table_json, reference_list]
        return response_service.build_composite_response(responses)

    elif len(entities) > 1 and entities[1] == "Doxycycline": # brand and generic recognized
        brand_name = entities[0]
        brand_obj = ontology_service.query_ontology(ontology, brand_name)
        
        generic_name = entities[1]
        generic_obj = ontology_service.query_ontology(ontology, generic_name)

        all_brands = list(generic_obj.hasBrandName)
        other_brands = [b for b in all_brands if b.name != brand_obj.name]

        presentation_obj = brand_obj.hasPresentation
        
        if len(presentation_obj) == 1:
            template = response_service.get_response_template("COMPARE_BRANDS", "brand_and_generic_single", response_index)
            p_name, dosage, price = ontology_service.get_presentation_details(presentation_obj[0])
            response_text = template['responseText'].format(
                brand=brand_name, 
                generic=generic_name,
                presentation=p_name,
                dosage=dosage,
                unit_price=price
            )
            table_json, reference_list = _generate_generic_overview_table(other_brands, template['columns'])
        else:
            template = response_service.get_response_template("COMPARE_BRANDS", "brand_and_generic_multiple", response_index)
            response_text = template['responseText'].format(
                brand=brand_name, 
                generic=generic_name
            )
            table_json, reference_list = _generate_generic_overview_table(all_brands, template['columns'])

        text_json = response_service.build_text_response(response_text)
        return response_service.build_composite_response(text_json, table_json, reference_list)
=======
<<<<<<< HEAD
def handle_compare_brands (entities, ontology, response_index):
    if entities[0] in ["Doxycycline", "Paracetamol"]:
        generic_name = entities[0]
        generic_obj = query_ontology(ontology, generic_name)

        if isinstance(generic_obj, dict): # check errors
            return generic_obj
        
        brands_obj = generic_obj.hasBrandName

        template = response_service.get_response_template("COMPARE_BRANDS", "generic_only", response_index)

        response = template.format(
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
        responses = [text_json, table_json]
        return response_service.build_composite_response(responses)

    elif len(entities) > 1 and entities[1] == "Doxycycline": # brand and generic recognized
        brand_name = entities[0]
        brand_obj = query_ontology(ontology, brand_name)

        if isinstance(brand_obj, dict):
            return brand_obj
        
        generic_name = entities[1]
        generic_obj = query_ontology(ontology, generic_name)

        if isinstance(generic_obj, dict):
            return generic_obj
        
        brands_obj = generic_obj.hasBrandName
        brands_obj.remove(brand_obj)
        presentation_obj = brand_obj.hasPresentation
        
        template = response_service.get_response_template("COMPARE_BRANDS", "brand_and_generic", response_index)
        
        response = template.format(
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
        responses = [text_json, table_json]
        return response_service.build_composite_response(responses)

    elif entities[0] in ["Doxin", "Dynadoxy", "Doxyclen", "Paracetamol"]: # multiple brands recognized
        if len(entities) < 2:
            return response_service.build_text_response("Apologies. I need at least 2 brands to compare them")

        brands_obj = []
        baseline_generic = ""
        baseline_brand = ""

        for brand in entities: # check if brand exists and same generic
            brand_obj = ontology_service.query_ontology(ontology, brand)
            brands_obj.append(brand_obj)

            if (not baseline_generic) and (not baseline_brand):
                baseline_generic = brand_obj.isBrandOf
                baseline_brand = brand_obj.name
            elif (baseline_generic != brand_obj.isBrandOf):
                current_generic = brand_obj.isBrandOf
                print(baseline_generic)
                print(current_generic)
                return response_service.build_text_response(f"The antibiotics have different generic names. {brand} has generic name of {current_generic.name}, while {baseline_brand} has generic name of {baseline_generic.name}")

        template = response_service.get_response_template("COMPARE_BRANDS", "multiple_brands", response_index)
        response = template['responseText'].format(
            brands = array_to_string(brands_obj),
            generic = baseline_generic.name
        )

        table_json, reference_list = _generate_generic_overview_table(brands_obj, template['columns'])
        text_json = response_service.build_text_response(response)
        return response_service.build_composite_response(text_json, table_json, reference_list)

def handle_uses_indications(entities, ontology, response_index):
    '''
    TODO: check reference for brand, check bullets for multiple brands
    '''
    if len(entities) > 1: # both generic and brand recognized

        brand_name = entities[0]
        generic_name = entities[1] 

        brand_obj = ontology_service.query_ontology(ontology, brand_name)
        generic_obj = ontology_service.query_ontology(ontology, generic_name)
        indication_obj = brand_obj.treats

        if len(indication_obj) == 1: # single indication
            print("SINGLE INDICATION")
            indication_ref_json = ontology_service.get_single_reference(indication_obj[0])
            brand_ref_json = ontology_service.get_single_reference(brand_obj)
            reference_list = response_service.combine_reference_list(indication_ref_json, brand_ref_json)
          
            indication, severity, disease_type = ontology_service.get_indication_severity_type(indication_obj[0])

            if severity: # Checking if severity is not specified
                indication_final = f"{severity} {indication}"
            else:
                indication_final = indication

            print(indication_final)
            template = response_service.get_response_template("GET_USES_INDICATIONS", "single_indication", response_index)
            response = template['responseText'].format(
                brand = brand_name,
                generic = generic_name,
                disease = indication_final,
                disease_type = disease_type
            )

            symptoms_obj = indication_obj[0].hasSymptoms
            text_json = response_service.build_text_response(response)
            bulleted_json = _split_commas_to_bullets(symptoms_obj)

            return response_service.build_composite_response(text_json, bulleted_json, reference_list)

        if len(indication_obj) > 1: # multiple indications
            print("MULTIPLE INDICATIONS")
            indication_ref_json = ontology_service.get_references_list(indication_obj)
            brand_ref_json = ontology_service.get_single_reference(brand_obj)
            reference_list = response_service.combine_reference_list(indication_ref_json, brand_ref_json)

            indication_bullets = []
            for indication in indication_obj:
                indication_name, severity, disease_type = ontology_service.get_indication_severity_type(indication)
                symptoms_obj = indication.hasSymptoms

                if severity: # Checking if severity is not specified
                    indication_final = f"{severity} {indication_name}"
                else:
                    indication_final = indication_name
                
                bullet = response_service.build_bullet(main_text=indication_final, description="Typically have symptoms such as " + symptoms_obj[0])
                indication_bullets.append(bullet)
            
            template = response_service.get_response_template("GET_USES_INDICATIONS", "multiple_indications", response_index)
            response = template['responseText'].format(
                brand = brand_name,
                generic = generic_name
            )

            text_json = response_service.build_text_response(response)
            bulleted_json = response_service.build_bulleted_response(indication_bullets)
            return response_service.build_composite_response(text_json, bulleted_json, reference_list)
    elif (entities[0] in ["Doxin", "Doxyclen", "Dynadoxy"]): # brand recognized
        brand_name = entities[0]
        brand_obj = ontology_service.query_ontology(ontology, brand_name)
        
        generic_obj = brand_obj.isBrandOf
        generic_name = generic_obj.name

        indication_obj = brand_obj.treats
        brand_ref_json = ontology_service.get_single_reference(brand_obj)

        if len(indication_obj) == 1: # single indication
            indication, severity, disease_type = ontology_service.get_indication_severity_type(indication_obj[0])
            indication_ref_json = ontology_service.get_single_reference(indication_obj[0])
            reference_list = response_service.combine_reference_list(indication_ref_json, brand_ref_json)

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

            text_json = response_service.build_text_response(response)
            symptoms_obj = indication_obj[0].hasSymptoms
            bulleted_json = _split_commas_to_bullets(symptoms_obj[0])
            return response_service.build_composite_response(text_json, bulleted_json, reference_list)

        if len(indication_obj) > 1: # multiple indications
            indication_bullets = []
            reference_list = brand_ref_json
            for indication in indication_obj:
                indication_name, severity, disease_type = ontology_service.get_indication_severity_type(indication)
                symptoms_obj = indication.hasSymptoms
                indication_ref_json = ontology_service.get_single_reference(indication)
                reference_list = response_service.combine_reference_list(reference_list, indication_ref_json)

                if severity: # Checking if severity is not specified
                    indication_final = f"{severity} {indication_name}"
                else:
                    indication_final = indication_name
                
                bullet = response_service.build_bullet(main_text=indication_final, description="Typically have symptoms such as " + symptoms_obj[0])
                indication_bullets.append(bullet)
            
            template = response_service.get_response_template("GET_USES_INDICATIONS", "multiple_indications", response_index)
            response = template['responseText'].format(
                brand = brand_name,
                generic = generic_name
            )

            text_json = response_service.build_text_response(response)
            bulleted_json = response_service.build_bulleted_response(indication_bullets)
            return response_service.build_composite_response(text_json, bulleted_json, reference_list)
    elif (entities[0] in ["Doxycycline", "Paracetamol"]): # generic recognized
        generic_name = entities[0]
        generic_obj = ontology_service.query_ontology(ontology, generic_name)
        
        template = response_service.get_response_template("GET_USES_INDICATIONS", "generic_only", response_index)
        response = template['responseText'].format (
            generic = generic_name
        )

        brands_obj = generic_obj.hasBrandName
        brands_ref_json = ontology_service.get_references_list(brands_obj)
        indication_ref_json = ""

        rows = []
        for brand in brands_obj:
            indication_obj = brand.treats
            indication_json_1 = ontology_service.get_single_reference(indication_obj[0])
            indication_ref_json = response_service.combine_reference_list(indication_ref_json, indication_json_1)
            row = [brand.name, array_to_string(indication_obj)]
            rows.append(row)

        reference_list = response_service.combine_reference_list(brands_ref_json, indication_ref_json)
        text_json = response_service.build_text_response(response)
        table_json = response_service.build_table_response(template['columns'], rows)
        return response_service.build_composite_response(text_json, table_json, reference_list)

def handle_side_effects(entities, ontology, response_index):
    '''
    TODO: can't distinguish side effect names in references, brand names in side effects
    caused by "Nausea" side effect name but title is "Doxycycline side effects"
    '''
    if  (len(entities) == 3): # generic, brand and side effect found
        brand_name = entities[0]
        brand_obj = ontology_service.query_ontology(ontology, brand_name)

        generic_name = entities[1]
        generic_obj = ontology_service.query_ontology(ontology, generic_name)

        target_side_effect = entities[2] 

        isFound = False
        reference_list = ""

        for side_effect_instance in brand_obj.hasSideEffect:
                onto_side_effect_name = side_effect_instance.is_a[0].name
                if target_side_effect.lower() == onto_side_effect_name.lower():
                    reference_list = ontology_service.get_single_reference(side_effect_instance)
                    isFound = True
        
        if not(isFound):
            print("NOT FOUND")
            template = response_service.get_response_template("GET_SIDE_EFFECTS", "generic_brand_verify_no_match", response_index)
            response = template['responseText'].format(
                side_effect = target_side_effect,
                generic = generic_name,
                brand = brand_name, 
            )

            text_json = response_service.build_text_response(response)
            reference_list = ontology_service.get_single_reference(brand_obj)
            return response_service.build_composite_response(text_json, reference_list)
        else:
            print("FOUND")
            template = response_service.get_response_template("GET_SIDE_EFFECTS", "generic_brand_verify_match", response_index)
            response = template['responseText'].format(
                side_effect = target_side_effect,
                brand = brand_name,
                generic = generic_name
            )
            text_json = response_service.build_text_response(response)
            print("REFERENCE", reference_list)
            return response_service.build_composite_response(text_json, reference_list)
    elif (len(entities) ==  2) and (entities[0] in ["Doxin", "Doxyclen", "Dynadoxy"]) and (entities[1] in ["Doxycycline"]): # brand and generic recognized
        brand_name = entities[0]
        generic_name = entities[1]
        brand_obj = ontology_service.query_ontology(ontology, brand_name)

        template = response_service.get_response_template("GET_SIDE_EFFECTS", "generic_brand_only", response_index)
        response = template['responseText'].format(
            brand = brand_name,
            generic = generic_name
        )
        text_json = response_service.build_text_response(response)

        side_effects_obj = brand_obj.hasSideEffect
        side_effects = []
        reference_list = ontology_service.get_references_list(side_effects_obj)

        for side_effect in side_effects_obj:
            side_effect_class = side_effect.is_a
            pattern_obj  = side_effect.whichIs
            duration_str = side_effect.lastsFor
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

            if "Not Specified" in duration_str[0]: # template for bullet description with no duration
                template = response_service.get_response_template("GET_SIDE_EFFECTS", "generic_brand_only", response_index)
                bullet_desc = template['descNoDuration'].format(
                    description = description[0]
                )
            else: # template for bullet description with duration
                template = response_service.get_response_template("GET_SIDE_EFFECTS", "generic_brand_only", response_index)
                bullet_desc = template['descWithDuration'].format(
                    description = description[0],
                    duration = add_space_to_pascal_case(duration_str[0])
                )

            bullet_json = response_service.build_bullet(bullet_main_text, bullet_desc)
            side_effects.append(bullet_json)

        bullet_json = response_service.build_bulleted_response(side_effects)
        return response_service.build_composite_response(text_json, bullet_json, reference_list)
    elif (len(entities) == 1 and entities[0] in ["Doxycycline"]): # generic is found
        generic_name = entities[0]
        generic_obj = ontology_service.query_ontology(ontology, generic_name)

        template = response_service.get_response_template("GET_SIDE_EFFECTS", "generic_only", response_index)
        response = template['responseText'].format(
            generic = generic_name
        )
        text_json = response_service.build_text_response(response)

        responses = [text_json]

        brand_obj = generic_obj.hasBrandName
        reference_list = ""

        for brand in brand_obj:
            side_effects = []
            header_json = response_service.build_header_response(brand.name)
            responses.append(header_json)
            side_effects_obj = brand.hasSideEffect

            for side_effect in side_effects_obj:
                side_effect_class = side_effect.is_a
                pattern_obj  = side_effect.whichIs
                duration_str = side_effect.lastsFor
                description = side_effect.hasSideEffectDescription

                side_effect_ref_json = ontology_service.get_references_list(side_effects_obj)
                reference_list = response_service.combine_reference_list(reference_list, side_effect_ref_json)

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

                if "Not Specified" in duration_str[0]: # template for bullet description with no duration
                    template = response_service.get_response_template("GET_SIDE_EFFECTS", "generic_only", response_index)
                    bullet_desc = template['descNoDuration'].format(
                        description = description[0]
                    )
                else: # template for bullet description with duration
                    template = response_service.get_response_template("GET_SIDE_EFFECTS", "generic_only", response_index)
                    bullet_desc = template['descWithDuration'].format(
                        description = description[0],
                        duration = add_space_to_pascal_case(duration_str[0])
                    )
                bullet_json = response_service.build_bullet(bullet_main_text, bullet_desc)
                side_effects.append(bullet_json)

            responses.append(response_service.build_bulleted_response(side_effects))
        responses.append(reference_list)
        return response_service.build_composite_response(responses)
    elif (len(entities) == 2 and entities[0] in ["Doxycycline"]): # generic and side effect is found
        generic_name = entities[0]
        generic_obj = ontology_service.query_ontology(ontology, generic_name)
        
        target_side_effect = entities[1] 
        found_brands = []

        brands_obj = generic_obj.hasBrandName
        reference_list = ""

        for brand in brands_obj:
            for side_effect_instance in brand.hasSideEffect:
                onto_side_effect_name = side_effect_instance.is_a[0].name
                if target_side_effect.lower() == onto_side_effect_name.lower():
                    if brand.name not in found_brands:
                        side_effect_ref_json = ontology_service.get_single_reference(side_effect_instance)
                        reference_list = response_service.combine_reference_list(reference_list, side_effect_ref_json)
                        found_brands.append(brand)
                    break 
        
        if len(found_brands) < 1:
            template = response_service.get_response_template("GET_SIDE_EFFECTS", "generic_verify_no_match", response_index)
            reference_list = ontology_service.get_references_list(brands_obj)
            response = template['responseText'].format(
                side_effect = target_side_effect,
                generic = generic_name, 
            )
            text_json = response_service.build_text_response(response)
            return response_service.build_composite_response(text_json, reference_list)
        else:
            template = response_service.get_response_template("GET_SIDE_EFFECTS", "generic_verify_match", response_index)
            response = template['responseText'].format(
                side_effect = target_side_effect,
                generic = generic_name, 
                brands = array_to_string(found_brands)
            )
            text_json = response_service.build_text_response(response)
            return response_service.build_composite_response(response, reference_list)
    elif (len(entities) == 1 and entities [0] in ["Doxin", "Dynadoxy", "Doxyclen"]): # brand is recognized
        brand_name = entities[0]
        brand_obj = ontology_service.query_ontology(ontology, brand_name)

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

            if "Not Specified" in duration_obj[0].name: # template for bullet description with no duration
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
        brand_obj = ontology_service.query_ontology(ontology, brand_name)
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

def handle_storage_instructions(entities, ontology, response_index):
    '''
    TODO: handling there are no storage instructions
    '''
    if len(entities) > 1: # brand, generic
        brand_name = entities[0]
        brand_obj = ontology_service.query_ontology(ontology, brand_name)

        generic_name = entities[1]
        generic_obj = ontology_service.query_ontology(ontology, generic_name)

        storage_rules_id = brand_obj.hasStorageRule
        storage_rules = []
        reference_list = ontology_service.get_references_list(storage_rules_id)

        for storage_id in storage_rules_id:
            storage_rule = storage_id.hasStewardshipDescription
            bullet = response_service.build_bullet(description=storage_rule[0])
            storage_rules.append(bullet)

        template = response_service.get_response_template("GET_STORAGE_INSTRUCTIONS", "generic_brand", response_index)
        response = template['responseText'].format(
            brand = brand_name,
            generic = generic_name
        )

        text_json = response_service.build_text_response(response)
        bulleted_json = response_service.build_bulleted_response(storage_rules)
        return response_service.build_composite_response(text_json, bulleted_json, reference_list)

    elif entities[0] in ["Doxin", "Doxyclen", "Dynadoxy"]: # brand recognized
        brand_name = entities[0]
        brand_obj = ontology_service.query_ontology(ontology, brand_name)

        storage_rules_id = brand_obj.hasStorageRule
        storage_rules = []
        reference_list = ontology_service.get_references_list(storage_rules_id)

        for storage_id in storage_rules_id:
            storage_rule = storage_id.hasStewardshipDescription
            bullet = response_service.build_bullet(description=storage_rule[0])
            storage_rules.append(bullet)

        template = response_service.get_response_template("GET_STORAGE_INSTRUCTIONS", "brand_only", response_index)
        response = template['responseText'].format(
            brand = brand_name
        )

        text_json = response_service.build_text_response(response)
        bulleted_json = response_service.build_bulleted_response(storage_rules)
        return response_service.build_composite_response(text_json, bulleted_json, reference_list)
    elif entities[0] in ["Doxycycline"]: # generic recognized
        generic_name = entities[0]
        generic_obj = ontology_service.query_ontology(ontology, generic_name)

        brands_obj = generic_obj.hasBrandName
        rows = []
        reference_list = []

        for brand in brands_obj:
            brand_name = brand.name
            storage_rules_id = brand.hasStorageRule

            storage_ref_json = ontology_service.get_references_list(storage_rules_id)
            reference_list = response_service.combine_reference_list(reference_list, storage_ref_json)

            for storage_rule_id in storage_rules_id:
                storage_rule = storage_rule_id.hasStewardshipDescription
                rows.append([brand_name, storage_rule[0]])

        template = response_service.get_response_template("GET_STORAGE_INSTRUCTIONS", "generic_only", response_index)
        response = template['responseText'].format(
            generic = generic_name
        )

        text_json = response_service.build_text_response(response)
        table_json = response_service.build_table_response(template['columns'], rows)
        return response_service.build_composite_response(text_json, table_json, reference_list)

# --- Helper Functions for handle antibiotic info  ---
def _build_brand_overview_response(brand_obj, generic_name, response_index):
    presentation_obj = brand_obj.hasPresentation
    brand_name = brand_obj.name
    reference = ontology_service.get_single_reference(brand_obj)
    if len(presentation_obj) > 1:
        template = response_service.get_response_template("GET_ANTIBIOTIC_INFO","brand_multiple", response_index)
        response = template['responseText'].format(
            brand=brand_name,
            generic=generic_name,
        ) 
        presentation_details = ontology_service.get_brand_info_details(presentation_obj)
        table_json = response_service.build_table_response(template['columns'], presentation_details )
        text_json = response_service.build_text_response(response)
        responses = [text_json, table_json, reference]
        return response_service.build_composite_response(responses)

    elif len(presentation_obj) == 1: 
        presentation, dosage, unit_price = ontology_service.get_presentation_details(presentation_obj[0])
        template = response_service.get_response_template("GET_ANTIBIOTIC_INFO", "brand_single", response_index)
        response = template['responseText'].format(
            brand=brand_name,
            generic=generic_name,
            presentation = presentation,
            dosage = dosage,
            unit_price = unit_price
        )
        text_json = response_service.build_text_response(response)
        responses = [text_json, reference]
        return response_service.build_composite_response(responses)

def _generate_generic_overview_table(brands_obj, columns):
    """
    Helper method that builds the table rows and gathers references.
    """    
    rows = []
    for brand in brands_obj:
        presentation_obj = brand.hasPresentation
        for presentation in presentation_obj:
            presentation, dosage, price = ontology_service.get_presentation_details(presentation)
            row = [brand.name, presentation, dosage, price]
            rows.append(row)
        
    table_json = response_service.build_table_response(columns, rows)
    references = ontology_service.get_references_list(brands_obj)
    return table_json, references

def _split_commas_to_bullets(list_item):
    '''
    Creates a bulleted list by splitting commas

    args:
        list_item: sentences that contain commas that can be split
    Returns:
        a bulleted list of items from a sentence
    '''
    items_array = list_item[0].split(',')

    bullets = []

    for item in items_array:
        bullet = response_service.build_bullet(description=item)
        bullets.append(bullet)
    
    return response_service.build_bulleted_response(bullets)

