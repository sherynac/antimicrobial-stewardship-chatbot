import services.response_service as response_service
from utils.helpers import array_to_string, is_yes_or_no, add_space_to_pascal_case
from services.ontology_service import query_ontology

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
        brand_obj = generic_obj.hasBrandName

        template = response_service.get_response_template("GET_ANTIBIOTIC_INFO", "generic_only", response_index)
        response = template.format(
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
        responses = [text_json, table_json]
        return response_service.build_composite_response(responses)

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

        for brand in entities: # check if brand exists
            brand_obj = query_ontology(ontology, brand)

            if isinstance(brand_obj, dict):
                return brand_obj

            brands_obj.append(brand_obj)

        baseline_generic = brands_obj[0].isBrandOf
        print(brands_obj[0].name)
        for brand in brands_obj[1:]: # checking if same generic name
            current_generic = brand.isBrandOf

            if current_generic != baseline_generic:
                return response_service.build_text_response(f"The antibiotics have different generic names. {brand.name} has generic name of {current_generic[0].name}, while {brands_obj[0].name} has generic name of {baseline_generic[0].name}")

        template = response_service.get_response_template("COMPARE_BRANDS", "multiple_brands", response_index)
        response = template.format(
            brands = array_to_string(brands_obj),
            generic = baseline_generic[0].name
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

    


# # def handle_uses_indications(entities, ontology, response_index):
    