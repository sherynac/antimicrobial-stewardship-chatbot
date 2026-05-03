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

    def build_bullet(self, description:str, main_text: str = "") -> dict:
        return {"type": "bullet", "main_text": main_text, "description": description}


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

    def build_bullet_list(self, list: list) -> dict:
        return {
            "type": "bullet_list",
            "items": list
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
        print("GENERIC GET ANTIBIOTIC INFO")
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
    
    def build_indications_single(self, indication_info, symptoms_array, reference):
        print("SINGLE INDICATION")
        template = self.get_response_template("GET_USES_INDICATIONS", "single_indication")
        response_text = random.choice(template['responseTexts'])

        reference_json = self.build_reference_list(reference)

        text = response_text.format(
            brand = indication_info['brand'],
            generic = indication_info['generic'],
            disease = indication_info['disease']
        )

        return self.build_composite_response([
            self.build_text_response(text),
            self.build_bullet_list(symptoms_array),
            reference_json
        ])
    
    def build_indications_multiple(self, indication_info, indication_final, symptoms_obj, reference):
        print("MULTIPLE INDICATIONS")
        template = self.get_response_template("GET_USES_INDICATIONS", "multiple_indications")
        response_text = random.choice(template['responseTexts'])
        bullet_template = template['itemFormat']

        reference_json = self.build_reference_list(reference)

        text = response_text.format(
            brand=indication_info['brand'],
            generic=indication_info['generic'],
        )

        bullet_list = self.build_bullet_list([
            self.build_bullet(
                main_text=indication,
                description=bullet_template['description'].format(symptoms=symptoms)
            )
            for indication, symptoms in zip(indication_final, symptoms_obj)
        ])

        return self.build_composite_response([
            self.build_text_response(text),
            bullet_list,
            reference_json
        ])

    def build_indications_generic(self, generic_name, table_details, reference):
        print("GENERIC INDICATIONS")
        template = self.get_response_template("GET_USES_INDICATIONS", "generic_only")
        response_text = random.choice(template['responseTexts'])

        reference_json = self.build_reference_list(reference)

        text = response_text.format(
            generic=generic_name,
        )

        return self.build_composite_response([
            self.build_text_response(text),
            self.build_table_response(template['columns'], table_details),
            reference_json
        ])
    
    def build_side_effect_all_match(self, isFound, side_effect_info, reference):
        print("GENERIC, BRAND, SIDE EFFECT MATCH")

        if not(isFound):
            template = self.get_response_template("GET_SIDE_EFFECTS", "generic_brand_verify_no_match")
        else:
            template = self.get_response_template("GET_SIDE_EFFECTS", "generic_brand_verify_match")

        response_text = random.choice(template['responseTexts'])
        reference_json = self.build_reference_list(reference)

        text = response_text.format(
            generic=side_effect_info['generic'],
            brand = side_effect_info['brand'],
            side_effect = side_effect_info['side_effect']
        )

        return self.build_composite_response([
            self.build_text_response(text),
            reference_json
        ])
    
    def build_side_effect_brand_match(self, isFound, side_effect_info, reference):
        print("BRAND, SIDE EFFECT MATCH")

        if not(isFound):
            template = self.get_response_template("GET_SIDE_EFFECTS", "brand_verify_no_match")
        else:
            template = self.get_response_template("GET_SIDE_EFFECTS", "brand_verify_match")

        response_text = random.choice(template['responseTexts'])
        reference_json = self.build_reference_list(reference)

        text = response_text.format(
            brand = side_effect_info['brand'],
            side_effect = side_effect_info['side_effect']
        )

        return self.build_composite_response([
            self.build_text_response(text),
            reference_json
        ])
    
    def build_side_effect_generic_match(self, isFound, side_effect_info, reference):
        print("GENERIC, SIDE EFFECT MATCH")

        if not(isFound):
            template = self.get_response_template("GET_SIDE_EFFECTS", "generic_verify_no_match")
        else:
            template = self.get_response_template("GET_SIDE_EFFECTS", "generic_verify_match")

        response_text = random.choice(template['responseTexts'])
        reference_json = self.build_reference_list(reference)

        text = response_text.format(
            generic = side_effect_info['generic'],
            brands = side_effect_info['brands'],
            side_effect = side_effect_info['side_effect']
        )

        return self.build_composite_response([
            self.build_text_response(text),
            reference_json
        ])

    def build_side_effect_generic_brand(self, info, side_effect_list, reference): 
        print("GENERIC, BRAND SIDE EFFECT")
        template = self.get_response_template("GET_SIDE_EFFECTS", "generic_brand_only")
        response_text = random.choice(template['responseTexts'])

        text = response_text.format(
            generic = info['generic'],
            brand = info['brand']
        )

        bullet_template = template['groupFormat']
        formatted_effects = []

        for se in side_effect_list:
            if se['pattern']:
                main_text = bullet_template['mainWithPattern'].format(
                    side_effect=se['side_effect'],
                    pattern=se['pattern']
                )
            else:
                main_text = bullet_template['mainNoPattern'].format(
                    side_effect=se['side_effect']
                )
            
            formatted_effects.append(
                self.build_bullet(
                    main_text=main_text,  
                    description=se['description']
                )
            )

        reference_json = self.build_reference_list(reference)

        return self.build_composite_response([
            self.build_text_response(text),
            self.build_bullet_list(formatted_effects),
            reference_json
        ])
    
    def build_side_effect_generic(self, side_effect_info: dict, reference: list):
        print("GENERIC, SIDE EFFECTS")
        template = self.get_response_template("GET_SIDE_EFFECTS", "generic_only")
        response_text = random.choice(template['responseTexts'])
        reference_json = self.build_reference_list(reference)

        text = response_text.format(generic=side_effect_info['generic'])

        # build a section per brand
        brand_sections = []
        for brand_data in side_effect_info['brands']:
            bullets = []
            for se in brand_data['side_effects']:
                if se['pattern']:
                    main_text = template['groupFormat']['mainWithPattern'].format(
                        side_effect=se['side_effect'],
                        pattern=se['pattern']
                    )
                else:
                    main_text = template['groupFormat']['mainNoPattern'].format(
                        side_effect=se['side_effect']
                    )
                bullets.append(self.build_bullet(
                    main_text=main_text,
                    description=se['description']
                ))

            brand_sections.append({
                "type": "section",
                "title": brand_data['brand'],  # "Doxin"
                "items": bullets               # list of bullets
            })

        return self.build_composite_response([
            self.build_text_response(text),
            *brand_sections,
            reference_json
        ])

    def build_side_effect_brand(self, brand, side_effect_list, reference):
        print("BRAND SIDE EFFECT")
        template = self.get_response_template("GET_SIDE_EFFECTS", "brand_only")
        response_text = random.choice(template['responseTexts'])

        text = response_text.format(
            brand = brand
        )

        bullet_template = template['itemFormat']
        formatted_effects = []

        for se in side_effect_list:
            if se['pattern']:
                main_text = bullet_template['mainWithPattern'].format(
                    side_effect=se['side_effect'],
                    pattern=se['pattern']
                )
            else:
                main_text = bullet_template['mainNoPattern'].format(
                    side_effect=se['side_effect']
                )
            
            formatted_effects.append(
                self.build_bullet(
                    main_text=main_text,  
                    description=se['description']
                )
            )

        reference_json = self.build_reference_list(reference)

        return self.build_composite_response([
            self.build_text_response(text),
            self.build_bullet_list(formatted_effects),
            reference_json
        ])
response_service = ResponseService('./backend/data/VRB.json')