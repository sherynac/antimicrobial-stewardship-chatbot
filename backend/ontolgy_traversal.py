class OntologyTraversal:
    def __init__(self, ontology_graph):
        self.graph = ontology_graph

    def find_entities(self, entity_name):
        """Find all instances of a given entity type"""
        entities = []
        entity_class = self.graph.search_one(iri=f"*#{entity_name}")
        
        if entity_class:
            for entity in entity_class.instances():
                entity_name = str(entity).split(".")[-1]  # Fixed parsing
                entities.append(entity_name)
        return entities

    def get_antibiotic_instance(self, antibiotic_name):
        """Get specific antibiotic instance (case-insensitive)"""
        Antibiotic = self.graph.search_one(iri="*#Antibiotic")
        
        for antibiotic in Antibiotic.instances():
            antibiotic_str = str(antibiotic).lower()
            if antibiotic_name.lower() in antibiotic_str or \
               str(antibiotic).split(".")[-1].lower() == antibiotic_name.lower():
                return antibiotic
        return None

    def find_brands(self, antibiotic_name):
        """Find all brands for an antibiotic via hasBrandName"""
        brands = []
        antibiotic_instance = self.get_antibiotic_instance(antibiotic_name)
        
        if antibiotic_instance and hasattr(antibiotic_instance, 'hasBrandName'):
            brand_instances = getattr(antibiotic_instance, 'hasBrandName', [])
            for brand in brand_instances:
                brand_name = str(brand).split(".")[-1]
                brands.append(brand_name)
        return brands

    def find_indications(self, brand_name):
        """Find indications treated by a brand via treats"""
        indications = []
        Brand = self.graph.search_one(iri="*#Brand")
        brand_instance = self._get_brand_instance(brand_name)
        
        if brand_instance and hasattr(brand_instance, 'treats'):
            indication_instances = getattr(brand_instance, 'treats', [])
            for indication in indication_instances:
                indication_name = str(indication).split(".")[-1]
                indications.append(indication_name)
        return indications

    def find_warnings(self, brand_name):
        """Find warnings for a brand via hasWarning"""
        warnings = []
        brand_instance = self._get_brand_instance(brand_name)
        
        if brand_instance and hasattr(brand_instance, 'hasWarning'):
            warning_instances = getattr(brand_instance, 'hasWarning', [])
            for warning in warning_instances:
                warning_name = str(warning).split(".")[-1]
                warnings.append(warning_name)
        return warnings

    def find_side_effects(self, brand_name):
        """Find side effects for a brand via hasSideEffect"""
        side_effects = []
        brand_instance = self._get_brand_instance(brand_name)
        
        if brand_instance and hasattr(brand_instance, 'hasSideEffect'):
            se_instances = getattr(brand_instance, 'hasSideEffect', [])
            for se in se_instances:
                se_name = str(se).split(".")[-1]
                side_effects.append(se_name)
        return side_effects

    def find_interactions(self, brand_name):
        """Find interactions for a brand with full details"""
        interactions = []
        brand_instance = self._get_brand_instance(brand_name)
        
        if brand_instance and hasattr(brand_instance, 'hasInteraction'):
            interaction_instances = getattr(brand_instance, 'hasInteraction', [])
            for interaction in interaction_instances:
                interaction_info = {
                    'name': str(interaction).split(".")[-1],
                    'substances': [],
                    'descriptions': {}
                }
                
                # Get interacting substances
                if hasattr(interaction, 'interactsWith'):
                    substances = getattr(interaction, 'interactsWith', [])
                    for substance in substances:
                        substance_name = str(substance).split(".")[-1]
                        interaction_info['substances'].append(substance_name)
                
                # Get all description properties
                desc_props = ['hasInteractionDescription', 'hasClinicalEffects', 'hasManagementAdvice']
                for prop in desc_props:
                    if hasattr(interaction, prop):
                        values = getattr(interaction, prop, [])
                        interaction_info['descriptions'][prop] = [str(v) for v in values]
                
                interactions.append(interaction_info)
        return interactions

    def find_stewardship(self, brand_name):
        """Find stewardship principles for a brand"""
        stewardship = []
        brand_instance = self._get_brand_instance(brand_name)
        
        if brand_instance and hasattr(brand_instance, 'managedBy'):
            sp_instances = getattr(brand_instance, 'managedBy', [])
            for sp in sp_instances:
                sp_name = str(sp).split(".")[-1]
                stewardship.append(sp_name)
        return stewardship

    def get_full_info(self, antibiotic_name):
        """Get complete information for an antibiotic"""
        info = {
            'antibiotic': antibiotic_name,
            'brands': [],
            'indications': [],
            'warnings': [],
            'side_effects': [],
            'interactions': [],
            'stewardship': []
        }
        
        brands = self.find_brands(antibiotic_name)
        info['brands'] = brands
        
        for brand in brands:
            info['indications'].extend(self.find_indications(brand))
            info['warnings'].extend(self.find_warnings(brand))
            info['side_effects'].extend(self.find_side_effects(brand))
            info['interactions'].extend(self.find_interactions(brand))
            info['stewardship'].extend(self.find_stewardship(brand))
        
        return info

    def _get_brand_instance(self, brand_name):
        Brand = self.graph.search_one(iri="*#Brand")
        for brand in Brand.instances():
            if brand_name.lower() in str(brand).lower():
                return brand
        return None

    def search_all(self, term):
        results = {
            'antibiotics': self.find_entities('Antibiotic'),
            'brands': self.find_entities('Brand'),
            'substances': self.find_entities('Substance')
        }
        return results

    def debug(self):
        """Debug: Print ontology structure"""
        print("=== Ontology Debug ===")
        print(f"Classes: {len(list(self.graph.classes()))}")
        print(f"Antibiotics: {self.find_entities('Antibiotic')}")
        print(f"Brands: {self.find_entities('Brand')[:5]}...")