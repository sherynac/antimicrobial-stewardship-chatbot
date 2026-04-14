import services.response_service as response_service
from utils.helpers import array_to_string, is_yes_or_no, add_space_to_pascal_case

def handle_antibiotic_info(entities, ontology, response_index):
    if len(entities) > 1: # brand and generic recognized
        isBrand = False
        generic_name = entities[0] if entities else None
        brand_name = entities[1] if entities else None

        generic_obj = ontology.search_one(iri=f"*{generic_name}")
        brand_obj = ontology.search_one(iri=f"*{brand_name}")

        if brand_obj.isBrandOf[0] == generic_obj:
            isBrand = True
        
        presentation_obj = brand_obj.hasPresentation

        template = response_service.get_response_template("GET_ANTIBIOTIC_INFO", "both_generic_and_brand", response_index)
        response = template.format(
            is_brand_of = is_yes_or_no(isBrand),
            brand=brand_name,
            generic=generic_name,
            presentation= array_to_string(presentation_obj),
        )
        return response_service.build_text_response(response)

    elif entities[0] in ["Doxin", "Dynadoxy", "Doxyclen"]:        
        brand_name = entities[0] if entities else None
        brand_obj = ontology.search_one(iri=f"*{brand_name}*")
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
    
    elif entities[0] == "Doxycycline":
        generic_name = entities[0] if entities else None
        generic_obj = ontology.search_one(iri=f"*{generic_name}*")
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


def handle_uses_indications(entities, ontology, response_index):
    