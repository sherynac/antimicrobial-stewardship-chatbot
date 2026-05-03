import json
import os
import random

# response_service.py

class ResponseService:
    
    def __init__(self, path):
        self.index = self._load_response_index(path)

    def _load_response_index(self, path):

        with open(path, 'r', encoding='utf-8') as file:
            response_bank = json.load(file)
            print("Loaded JSON vetted response bank")

        index = {}

        for intent_obj in response_bank["IntentDefinitions"]:
            intent = intent_obj["intent"]
            index[intent] = {}

            for response in intent_obj["responses"]:
                condition = response["condition"]
                index[intent][condition] = response
    
        return index


    # ─── Template Fetching ────────────────────────────────────────────
    
    def get_response_template(self, intent: str, variant: str) -> dict:
        return self.index[intent][variant]

    # ─── Primitive Builders ───────────────────────────────────────────

    def build_text_response(self, text: str) -> dict:
        return {"type": "text", "content": text}

    def build_table_response(self, columns: list, rows: list) -> dict:
        return {"type": "table", "columns": columns, "rows": rows}

    def build_reference(self, name: str, title: str, url: str) -> dict:
        return {"type":"reference", "name": name, "title": title, "url": url}


    # ─── Composite Builder ────────────────────────────────────────────

    def build_composite_response(self, responses: list[dict]) -> dict:
        return {"type": "composite", "responses": responses}
    
    def build_reference_list(self, references: list) -> dict:
        return {
            "type": "reference_list",
            "sources": [
                self.build_reference(ref["name"], ref["title"], ref["url"])
                for ref in references
            ]
        }

    # ─── High-Level Intent Builders ───────────────────────────────────

    def build_antibiotic_multiple(self, brand_info, table_details, reference):
        print("MULTIPLE GET ANTIBIOTIC INFO")
        template = self.get_response_template("GET_ANTIBIOTIC_INFO", "brand_multiple")
        response_text = random.choice(template['responseTexts'])
        reference_json = self.build_reference_list(reference)

        text = response_text.format(
            brand=brand_info["brand"], 
            generic=brand_info["generic"], 
            manufacturer=brand_info["manufacturer"],
            distributor=brand_info["distributor"],
            content=brand_info["content"]
        )

        return self.build_composite_response([
            self.build_text_response(text),
            self.build_table_response(template['columns'], table_details),
            reference_json
        ])

    def build_antibiotic_single(self, brand_info, reference):
        print("SINGLE GET ANTIBIOTIC INFO")
        template = self.get_response_template("GET_ANTIBIOTIC_INFO", "brand_single")
        response_text = random.choice(template['responseTexts'])

        reference_json = self.build_reference_list(reference)

        text = response_text.format(
            brand=brand_info["brand"], 
            generic=brand_info["generic"], 
            manufacturer=brand_info["manufacturer"],
            distributor=brand_info["distributor"],
            content=brand_info["content"],
            presentation=brand_info["presentation"],
            dosage=brand_info["dosage"],
            unit_price=brand_info["unit_price"]
        )

        return self.build_composite_response([
            self.build_text_response(text),
            reference_json
        ])
    
    def build_antibiotic_generic(self, generic_info, table_details, reference):
        print("SINGLE GET ANTIBIOTIC INFO")
        template = self.get_response_template("GET_ANTIBIOTIC_INFO", "generic_only")
        response_text = random.choice(template['responseTexts'])

        reference_json = self.build_reference_list(reference)

        text = response_text.format(
            generic=generic_info["generic"], 
            drug_class=generic_info["drug_class"]
        )

        return self.build_composite_response([
            self.build_text_response(text),
            self.build_table_response(template['columns'], table_details),
            reference_json
        ])

    
response_service = ResponseService('./backend/data/VRB.json')