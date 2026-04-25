from rdflib import Graph
from owlready2 import get_ontology, sync_reasoner_hermit
from services.response_service import build_text_response, build_reference, build_reference_list
from utils.helpers import add_space_to_pascal_case, is_name_match

def load_ontology():
    '''
    Reads Turtle file (.ttl), converts it to OWL file (.owl), loads the ontology and returns the ontology

    Returns:
        onto: the ontology knowledge base for the AMR chatbot
    '''
    # Load Turtle file
    g = Graph()
    g.parse("./backend/data/sample-ontology.ttl", format="turtle")

    print ("AFTER GRAPH")
    # Save as RDF/XML (.owl)
    g.serialize(destination="./backend/data/sample-ontology.owl", format="xml")

    onto = get_ontology("./backend/data/sample-ontology.owl").load()
    print(f"Loaded ontology with {len(list(onto.classes()))} classes")
    with onto:
        sync_reasoner_hermit()

    return onto

def query_ontology(ontology, entity):
    '''
    Queries ontology for an entity and if it cannot be found returns an error message

    args:
        entity : name of object to be retrieved from the ontology
    
    Returns:
        result : retrieved object from ontology with same entity name
    '''

    result = ontology.search_one(label=entity)
    if not result:  
        raise ValueError(f"I'm sorry I don't have any records for {entity}")

    return result

def get_references_list(entities):
    '''
    Building a reference list from multiple instances

    args:
        entity: object with multiple instances
    
    Returns:
        reference_list: the list of references from multiple entities
    '''
    references = []
    seen_urls = set()

    for entity in entities:
        references_obj = entity.hasReference
        
        for reference in references_obj:
            title, url = get_reference_details(reference)
            
            if url in seen_urls:
                continue 

            parent_class_names = [cls.name for cls in entity.INDIRECT_is_a if hasattr(cls, 'name')]
            
            if "Indication" in parent_class_names:
                indication = entity.is_a      
                if (is_name_match(add_space_to_pascal_case(indication[0].name), title)):
                    reference_json = build_reference(reference.name, title, url)
                    references.append(reference_json)
                    seen_urls.add(url)
            elif "StewardshipPrinciple" in parent_class_names:
                reference_json = build_reference(reference.name, title, url)
                references.append(reference_json)
                seen_urls.add(url)
            elif (entity.name) == title:
                reference_json = build_reference(reference.name, title, url)
                references.append(reference_json)
                seen_urls.add(url)

    reference_list = build_reference_list(references)
    return reference_list

def get_single_reference(entity):
    '''
    Building a reference list from a single instance

    args:
        entity: a single entity that has the :hasReference property
    
    Returns:
        reference_list: the list of references of a single entity
    '''
    references = []
    seen_urls = set()
    references_obj = entity.hasReference

    for reference in references_obj:
        title, url = get_reference_details(reference)

        if url in seen_urls:
            continue 
    
        parent_class_names = [cls.name for cls in entity.INDIRECT_is_a if hasattr(cls, 'name')]
        if "Indication" in parent_class_names:
            indication = entity.is_a      
            if (is_name_match(add_space_to_pascal_case(indication[0].name), title)):
                reference_json = build_reference(reference.name, title, url)
                references.append(reference_json)
                seen_urls.add(url)
        elif "StewardshipPrinciple" in parent_class_names:
            reference_json = build_reference(reference.name, title, url)
            references.append(reference_json)
            seen_urls.add(url)
        elif (entity.name) == title:
            reference_json = build_reference(reference.name, title, url)
            references.append(reference_json)
            seen_urls.add(url)

    reference_list = build_reference_list(references)
    return reference_list

def get_reference_details(reference_obj):
    '''
    Returns title and url of a reference
    '''
    reference_url = reference_obj.retrievedFrom
    reference_title = reference_obj.hasReferenceTitle
    return reference_title[0], reference_url[0]

def get_indication_severity_type (indication):
    indication_name = indication.is_a
    severity = indication.hasSeverity
    disease_type = indication_name[0].is_a

    indication_name = add_space_to_pascal_case(indication_name[0].name)
    severity_name = add_space_to_pascal_case(severity[0].name)
    disease_type = add_space_to_pascal_case(disease_type[0].name)
    disease_type = disease_type.replace(" Disease", "")

    if "Not Specified" in severity_name:
        return indication_name, None, disease_type
    
    return indication_name, severity[0].name, disease_type

def get_brand_info_details (presentation_obj):
    '''
    Retrieve all presentation, dosage and unit price for a brand

    args:
        presentation_obj: all presentations of a brand
    Returns:
        brand_info: array of brand info details
    '''
    brand_info = []
    for presentation in presentation_obj:
        presentation_name, dosage, unit_price = get_presentation_details(presentation)
        row = [presentation_name, dosage, f"Php {unit_price}"]
        brand_info.append(row)
    return brand_info

def get_presentation_details(presentation_obj):
    '''
    Retrieve presentation, dosage and unit price for a single presentation object

    args:
        presentation_obj: a single instance of presentation
    Returns:
        presentation.name: Type of presentation
        dosage: Dosage of the presentation
        unit_price: Price per unit of a presentation
    '''
    presentation = presentation_obj.is_a
    dosage = presentation_obj.hasDosage
    unit_price = presentation_obj.hasUnitPrice
    return add_space_to_pascal_case(presentation[0].name), dosage[0], unit_price[0]
