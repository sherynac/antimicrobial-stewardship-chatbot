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

    def build_section(self, title:str, items: list) -> dict:
        return {
            "type": "section",
            "title": title,
            "items": items
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
        unit_price_text = f" and costs Php {brand_info['unit_price']}" if brand_info['unit_price'] != "Not specified" else ""

        text = response_text.format(
            brand=brand_info["brand"], 
            generic=brand_info["generic"], 
            manufacturer=brand_info["manufacturer"],
            distributor=brand_info["distributor"],
            content=brand_info["content"],
            presentation=brand_info["presentation"],
            dosage=brand_info["dosage"],
            unit_price_text=unit_price_text
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

        bullets = [self.build_bullet(description=symptom) for symptom in symptoms_array]

        return self.build_composite_response([
            self.build_text_response(text),
            self.build_bullet_list(bullets),
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

            brand_sections.append(self.build_section(brand_data['brand'], bullets))  # ← cleaner

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
    
    def build_storage_single(self, antibiotic_info, storage_rule, reference):
        print("Storage Single")
        template = self.get_response_template("GET_STORAGE_INSTRUCTIONS", "single_storage")
        response_text = random.choice(template['responseTexts'])
        reference_json = self.build_reference_list(reference)

        text = response_text.format(
            generic = antibiotic_info['generic'],
            brand = antibiotic_info['brand'],
            stewardship_description = storage_rule[0]
        )

        return self.build_composite_response([
            self.build_text_response(text),
            reference_json
        ])

    def build_storage_multiple(self, antibiotic_info, storage_rules, reference):
        print("Storage Multiple")
        template = self.get_response_template("GET_STORAGE_INSTRUCTIONS", "multiple_storage")
        response_text = random.choice(template['responseTexts'])
        reference_json = self.build_reference_list(reference)

        text = response_text.format(
            generic = antibiotic_info['generic'],
            brand = antibiotic_info['brand'],
        )

        bullets = [
        self.build_bullet(description=rule[0] if isinstance(rule, list) else rule)
        for rule in storage_rules
        ]

        return self.build_composite_response([
            self.build_text_response(text),
            self.build_bullet_list(bullets),
            reference_json
        ])

    def build_storage_none(self, antibiotic_info, reference):
        print("Storage Single")
        template = self.get_response_template("GET_STORAGE_INSTRUCTIONS", "no_match")
        response_text = random.choice(template['responseTexts'])
        reference_json = self.build_reference_list(reference)

        text = response_text.format(
            generic = antibiotic_info['generic'],
            brand = antibiotic_info['brand'],
        )

        return self.build_composite_response([
            self.build_text_response(text),
            reference_json
        ])
    
    def build_storage_generic(self, storage_info: dict, reference: list):
        print("Storage Generic")
        template = self.get_response_template("GET_STORAGE_INSTRUCTIONS", "generic_only")
        response_text = random.choice(template['responseTexts'])
        reference_json = self.build_reference_list(reference)

        text = response_text.format(generic=storage_info['generic'])

        brand_sections = []
        for brand_data in storage_info['brands']:
            if brand_data['storage_rules']:
                bullets = [
                    self.build_bullet(description=rule)
                    for rule in brand_data['storage_rules']
                ]
            else:
                bullets = [
                    self.build_bullet(
                        description=f"{brand_data['brand']} has no specified storage instructions"
                    )
                ]

            brand_sections.append({
                "type": "section",
                "title": brand_data['brand'],
                "items": bullets
            })

        return self.build_composite_response([
            self.build_text_response(text),
            *brand_sections,
            reference_json
        ])

    def build_food_and_timing_single(self, antibiotic_info, food_and_timing_rule, reference):
        print("Food and Timing Single")
        template = self.get_response_template("GET_FOOD_AND_TIMING", "single_food_and_timing")
        response_text = random.choice(template['responseTexts'])
        reference_json = self.build_reference_list(reference)

        text = response_text.format(
            generic = antibiotic_info['generic'],
            brand = antibiotic_info['brand'],
            stewardship_description =food_and_timing_rule[0]
        )

        return self.build_composite_response([
            self.build_text_response(text),
            reference_json
        ])

    def build_food_and_timing_multiple(self, antibiotic_info, food_and_timing_rules, reference):
        print("Food and Timing Multiple")
        template = self.get_response_template("GET_FOOD_AND_TIMING", "multiple_food_and_timing")
        response_text = random.choice(template['responseTexts'])
        reference_json = self.build_reference_list(reference)

        text = response_text.format(
            generic = antibiotic_info['generic'],
            brand = antibiotic_info['brand'],
        )

        bullets = [
        self.build_bullet(description=rule[0] if isinstance(rule, list) else rule)
        for rule in food_and_timing_rules
        ]

        return self.build_composite_response([
            self.build_text_response(text),
            self.build_bullet_list(bullets),
            reference_json
        ])

    def build_food_and_timing_none(self, antibiotic_info, reference):
        print("Food and Timing None")
        template = self.get_response_template("GET_FOOD_AND_TIMING", "no_match")
        response_text = random.choice(template['responseTexts'])
        reference_json = self.build_reference_list(reference)

        text = response_text.format(
            generic = antibiotic_info['generic'],
            brand = antibiotic_info['brand'],
        )

        return self.build_composite_response([
            self.build_text_response(text),
            reference_json
        ])
    
    def build_food_and_timing_generic(self, food_and_timing_info: dict, reference: list):
        print("Food and timing Generic")
        template = self.get_response_template("GET_FOOD_AND_TIMING", "generic_only")
        response_text = random.choice(template['responseTexts'])
        reference_json = self.build_reference_list(reference)

        text = response_text.format(generic=food_and_timing_info['generic'])

        brand_sections = []
        for brand_data in food_and_timing_info['brands']:
            if brand_data['food_and_timing_rules']:
                bullets = [
                    self.build_bullet(description=rule)
                    for rule in brand_data['food_and_timing_rules']
                ]
            else:
                bullets = [
                    self.build_bullet(
                        description=f"{brand_data['brand']} has no specified food and timing instructions"
                    )
                ]

            brand_sections.append({
                "type": "section",
                "title": brand_data['brand'],
                "items": bullets
            })

        return self.build_composite_response([
            self.build_text_response(text),
            *brand_sections,
            reference_json
        ])

    def build_administration_single(self, antibiotic_info, administration_rule, reference):
        print("Administration Single")
        template = self.get_response_template("GET_ADMINISTRATION_INSTRUCTIONS", "single_administration")
        response_text = random.choice(template['responseTexts'])
        reference_json = self.build_reference_list(reference)

        text = response_text.format(
            generic = antibiotic_info['generic'],
            brand = antibiotic_info['brand'],
            stewardship_description =administration_rule[0]
        )

        return self.build_composite_response([
            self.build_text_response(text),
            reference_json
        ])

    def build_administration_multiple(self, antibiotic_info, administration_rules, reference):
        print("Administration Multiple")
        template = self.get_response_template("GET_ADMINISTRATION_INSTRUCTIONS", "multiple_administration")
        response_text = random.choice(template['responseTexts'])
        reference_json = self.build_reference_list(reference)

        text = response_text.format(
            generic = antibiotic_info['generic'],
            brand = antibiotic_info['brand'],
        )

        bullets = [
        self.build_bullet(description=rule[0] if isinstance(rule, list) else rule)
        for rule in administration_rules
        ]

        return self.build_composite_response([
            self.build_text_response(text),
            self.build_bullet_list(bullets),
            reference_json
        ])

    def build_administration_none(self, antibiotic_info, reference):
        print("Administration None")
        template = self.get_response_template("GET_ADMINISTRATION_INSTRUCTIONS", "no_match")
        response_text = random.choice(template['responseTexts'])
        reference_json = self.build_reference_list(reference)

        text = response_text.format(
            generic = antibiotic_info['generic'],
            brand = antibiotic_info['brand'],
        )

        return self.build_composite_response([
            self.build_text_response(text),
            reference_json
        ])
    
    def build_administration_generic(self, administration_info: dict, reference: list):
        print("Administration Generic")
        template = self.get_response_template("GET_ADMINISTRATION_INSTRUCTIONS", "generic_only")
        response_text = random.choice(template['responseTexts'])
        reference_json = self.build_reference_list(reference)

        text = response_text.format(generic=administration_info['generic'])

        brand_sections = []
        for brand_data in administration_info['brands']:
            if brand_data['administration_rules']:
                bullets = [
                    self.build_bullet(description=rule)
                    for rule in brand_data['administration_rules']
                ]
            else:
                bullets = [
                    self.build_bullet(
                        description=f"{brand_data['brand']} has no specified administration and adherence instructions"
                    )
                ]

            brand_sections.append({
                "type": "section",
                "title": brand_data['brand'],
                "items": bullets
            })

        return self.build_composite_response([
            self.build_text_response(text),
            *brand_sections,
            reference_json
        ])

    def build_interaction_single(self, interaction_info, reference):
        print("Interaction Single")
        template = self.get_response_template("GET_SUBSTANCE_INTERACTION", "single_interaction")
        response_text = random.choice(template['responseTexts'])
        reference_json = self.build_reference_list(reference)

        header = response_text.format(
            brand=interaction_info['brand'],
            generic=interaction_info['generic']
        )

        section = self.build_section(
            title=f"{interaction_info['substance_name']} ({interaction_info['substance_type']})",
            items=[
                self.build_bullet(main_text="About", description=interaction_info['substance_description']),
                self.build_bullet(main_text="Interaction", description=interaction_info['interaction_description'])
            ]
        )

        return self.build_composite_response([
            self.build_text_response(header),
            section,
            reference_json
        ])

    def build_interaction_multiple(self, interaction_info, interactions, reference):
        print("Interaction Multiple")
        template = self.get_response_template("GET_SUBSTANCE_INTERACTION", "multiple_interactions")
        response_text = random.choice(template['responseTexts'])
        reference_json = self.build_reference_list(reference)

        header = response_text.format(
            brand=interaction_info['brand'],
            generic=interaction_info['generic']
        )

        rows = [
            [
                f"{i['substance_name']} ({i['substance_type']})",
                i['substance_description'],
                i['interaction_description']
            ]
            for i in interactions
        ]

        return self.build_composite_response([
            self.build_text_response(header),
            self.build_table_response(
                columns=["Substance", "Substance Description", "Interaction"],
                rows=rows
            ),
            reference_json
        ])

    def build_interaction_none(self, interaction_info, reference):
        print("Interaction Brand None")
        template = self.get_response_template("GET_SUBSTANCE_INTERACTION", "substance_no_match")
        response_text = random.choice(template['responseTexts'])
        reference_json = self.build_reference_list(reference)

        text = response_text.format(
            brand=interaction_info['brand'],
            generic=interaction_info['generic']
        )

        return self.build_composite_response([
            self.build_text_response(text),
            reference_json
        ])

    def build_interaction_match(self, interaction_info, interactions, reference):
        print("Interaction Match")
        template = self.get_response_template("GET_SUBSTANCE_INTERACTION", "substance_verify_match")
        response_text = random.choice(template['responseTexts'])
        reference_json = self.build_reference_list(reference)

        text = response_text.format(
            substance=interaction_info['substance'],
            generic=interaction_info['generic'],
        )

        sections = [
            self.build_section(
                title=i['brand_name'],
                items=[
                    self.build_bullet(main_text="About", description=i['substance_description']),
                    self.build_bullet(main_text="Interaction", description=i['interaction_description'])
                ]
            )
            for i in interactions
        ]

        return self.build_composite_response([
            self.build_text_response(text),
            *sections,
            reference_json
        ])

    def build_interaction_generic(self, generic_name, interactions, reference):
        print("Interaction Generic")
        template = self.get_response_template("GET_SUBSTANCE_INTERACTION", "generic_only")
        response_text = random.choice(template['responseTexts'])
        reference_json = self.build_reference_list(reference)

        header = response_text.format(generic=generic_name)

        rows = [
            [
                f"{i['brand_name']}",
                f"{i['substance_name']} ({i['substance_type']})",
                i['substance_description'],
                i['interaction_description']
            ]
            for i in interactions
        ]

        return self.build_composite_response([
            self.build_text_response(header),
            self.build_table_response(
                columns=template['columns'],
                rows=rows
            ),
            reference_json
        ])

    def build_interaction_generic_none(self, interaction_info, reference):
        print("Interaction Generic None")
        template = self.get_response_template("GET_SUBSTANCE_INTERACTION", "generic_no_match")
        response_text = random.choice(template['responseTexts'])
        reference_json = self.build_reference_list(reference)

        text = response_text.format(
            generic=interaction_info['generic'],
            substance = interaction_info['substance']
        )

        return self.build_composite_response([
            self.build_text_response(text),
            reference_json
        ])
response_service = ResponseService('./data/VRB.json')