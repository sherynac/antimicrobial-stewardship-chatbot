import os
from rdflib import Graph
from owlready2 import get_ontology, sync_reasoner_hermit
from utils.helpers import add_space_to_pascal_case, is_name_match
from typing import Optional

class OntologyService:
    def __init__(self):
        self.onto = self.load_ontology()

    def load_ontology(self):
        owl_path = "./backend/data/FinalOntology.owl"

        if not os.path.exists(owl_path):
            print("Converting TTL to OWL...")
            g = Graph()
            g.parse("./backend/data/FinalOntology.ttl", format="turtle")
            g.serialize(destination=owl_path, format="xml")
            print("Conversion done, saved to .owl")

        # always load from .owl directly
        onto = get_ontology(owl_path).load()
        print(f"Loaded ontology with {len(list(onto.classes()))} classes")
        # with onto:
        #     sync_reasoner_hermit()
        return onto

    def query_ontology(self, entity):
        result = self.onto.search_one(iri="*" + entity)  # ← self.onto
        if result:
            return result
        raise ValueError(f"Entity '{entity}' not found in the ontology.")

    def find_entities(self, entity_name: str) -> list[str]:
        entities = []
        entity_class = self.onto.search_one(iri="*#" + entity_name)  # ← self.onto

        if entity_class:
            for entity in entity_class.instances():
                entity_name_clean = str(entity).split(".")[-1]
                entities.append(entity_name_clean)
        return sorted(set(entities))

    def find_subclasses(self, entity_name: str) -> list[str]:
        entity_class = self.onto.search_one(iri="*#" + entity_name)
        subclasses = []

        if entity_class:
            for subclass in entity_class.subclasses():
                subclasses.append(subclass.name)
        return sorted(set(subclasses))
    
    def is_correct_generic(self, generic_name, brand_obj):
        generic_obj = brand_obj.isBrandOf
        if (generic_obj.name != generic_name):
            raise AssertionError(f"It seems that {brand_obj.name} is not a {generic_name}, but is actually a {generic_obj.name}.")

    def get_indication_severity_type(self, indication):  # ← self added
        indication_name = indication.is_a
        severity = indication.hasSeverityType
        disease_type = indication_name[0].is_a

        indication_name = add_space_to_pascal_case(indication_name[0].name)
        severity_name = add_space_to_pascal_case(severity[0].name)
        disease_type = add_space_to_pascal_case(disease_type[0].name)
        disease_type = disease_type.replace("Disease", "")

        if "Not Specified" in severity_name:
            return indication_name, None, disease_type
        return indication_name, severity_name, disease_type

    def get_presentation_details(self, presentation_obj):
        presentation = presentation_obj.is_a
        dosage = presentation_obj.hasDosage
        unit_price = presentation_obj.hasUnitPrice
        unit_price_value = unit_price[0] if unit_price else "Not specified"
        return add_space_to_pascal_case(presentation[0].name), dosage[0], unit_price_value
    
    def get_brand_presentations (self, presentation_obj):
        '''
        Retrieve all presentation, dosage and unit price for a brand

        args:
            presentation_obj: all presentations of a brand
        Returns:
            brand_info: array of brand info details
        '''
        brand_info = []
        for presentation in presentation_obj:
            presentation_name, dosage, unit_price = self.get_presentation_details(presentation)
            row = [presentation_name, dosage, f"Php {unit_price}"]
            brand_info.append(row)
        return brand_info

    def get_reference_details(self, reference_obj):
        '''
        Returns title and url of a reference
        '''
        reference_url = reference_obj.retrievedFrom
        reference_title = reference_obj.hasReferenceTitle
        return reference_title[0], reference_url[0]

    def get_reference_from_entity(self, entity):
        references = []
        seen_urls = set()
        references_obj = entity.hasReference

        for reference in references_obj:
            title, url = self.get_reference_details(reference)

            if url in seen_urls:
                continue

            parent_class_names = [cls.name for cls in entity.INDIRECT_is_a if hasattr(cls, 'name')]
            
            if "Indication" in parent_class_names:
                indication = entity.is_a
                if is_name_match(add_space_to_pascal_case(indication[0].name), title):
                    references.append({"name": reference.name, "title": title, "url": url})
                    seen_urls.add(url)
            elif "StewardshipPrinciple" in parent_class_names:
                references.append({"name": reference.name, "title": title, "url": url})
                seen_urls.add(url)
            elif entity.name == title:
                references.append({"name": reference.name, "title": title, "url": url})
                seen_urls.add(url)

        return references 

    def get_reference_from_entities(self, entities):
        '''
        Building a reference list from multiple instances
        args:
            entities: object with multiple instances
        
        Returns:
            references: raw list of reference dicts
        '''
        references = []
        seen_urls = set()

        for entity in entities:
            references_obj = entity.hasReference
            
            for reference in references_obj:
                title, url = self.get_reference_details(reference)  # ← self.
                
                if url in seen_urls:
                    continue

                parent_class_names = [cls.name for cls in entity.INDIRECT_is_a if hasattr(cls, 'name')]
                
                if "Indication" in parent_class_names:
                    indication = entity.is_a
                    if is_name_match(add_space_to_pascal_case(indication[0].name), title):
                        references.append({"name": reference.name, "title": title, "url": url})
                        seen_urls.add(url)

                elif "StewardshipPrinciple" in parent_class_names:
                    references.append({"name": reference.name, "title": title, "url": url})
                    seen_urls.add(url)

                elif entity.name == title:
                    references.append({"name": reference.name, "title": title, "url": url})
                    seen_urls.add(url)

        return references
    
    def combine_references(self, *entity_groups):
        seen_urls = set()
        combined = []
        for refs in entity_groups:
            for ref in refs:
                if ref["url"] not in seen_urls:
                    combined.append(ref)
                    seen_urls.add(ref["url"])
        return combined


ontology_service = OntologyService()
