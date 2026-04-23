import owlready2
from owlready2 import *
from typing import List, Dict, Any, Optional, Set
import json

class OntologyTraversal:
    def __init__(self, ontology_graph):
        self.graph = ontology_graph
        self.reasoner_applied = False
        self.reasoner_type = None
        
    def apply_reasoning(self, reasoner: str = "builtin") -> bool:
        """Apply reasoner with correct parameters for each type"""
        reasoners = {
            "hermit": self._apply_hermit,
            "builtin": self._apply_builtin,
            "pellet": self._apply_pellet
        }
        
        self.data_test_before_and_after_reasoner(before=True)
        
        try:
            if reasoner in reasoners:
                success = reasoners[reasoner]()
                if success:
                    self.reasoner_type = reasoner
                    print(f"✓ {reasoner.capitalize()} reasoner applied")
                    self.data_test_before_and_after_reasoner(before=False)
                    return True
        except Exception as e:
            print(f"✗ {reasoner} failed: {e}")
            
        print("⚠ Using ontology without reasoning (still fully functional)")
        return False
    
    def _apply_hermit(self) -> bool:
        with self.graph:
            sync_reasoner_hermit(infer_property_values=True)
        self.reasoner_applied = True
        return True
    
    def _apply_builtin(self) -> bool:
        with self.graph:
            sync_reasoner(infer_property_values=True)
        self.reasoner_applied = True
        return True
    
    def _apply_pellet(self) -> bool:
        with self.graph:
            sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)
        self.reasoner_applied = True
        return True
    
    def data_test_before_and_after_reasoner(self, before: bool = True):
        """Comprehensive reasoner testing - shows EXACT differences"""
        reasoner_status = "BEFORE" if before else "AFTER"
        print(f"\n{'='*60}")
        print(f"🔬 REASONER TEST: {reasoner_status} REASONING")
        print(f"{'='*60}")
        
        if not before:
            print(f"Reasoner: ✓ {self.reasoner_type.upper()}")
        
        # 1. BASIC ENTITY DISCOVERY (subclass inference)
        print("\n1️⃣ SUBCLASS INFERENCE:")
        print(f"   Indications: {self.find_entities('Indication')}")
        print(f"   Respiratory: {self.find_entities('RespiratoryDisease')}")
        
        # 2. BIDIRECTIONAL PROPERTIES
        print("\n2️⃣ BIDIRECTIONAL PROPERTIES:")
        doxycycline = self.get_antibiotic_instance("Doxycycline")
        if doxycycline:
            brands_from_anti = [str(b).split(".")[-1] for b in getattr(doxycycline, 'hasBrandName', [])]
            print(f"   Doxycycline → Brands: {brands_from_anti}")
        
        doxin = self.get_brand_instance("Doxin")
        if doxin:
            anti_from_brand = [str(a).split(".")[-1] for a in getattr(doxin, 'isBrandOf', [])]
            print(f"   Doxin → Antibiotic: {anti_from_brand}")
        
        # 3. PROPERTY CHAINING
        print("\n3️⃣ PROPERTY CHAINING:")
        if doxin:
            treatments = [str(t).split(".")[-1] for t in getattr(doxin, 'treats', [])]
            print(f"   Doxin → treats: {treatments}")
        
        # 4. CLASS HIERARCHY
        print("\n4️⃣ CLASS HIERARCHY:")
        atypical = self._get_instance_by_name(self._get_class("Indication"), "AtypicalPneumonia")
        if atypical:
            print(f"   AtypicalPneumonia types: {[c.__name__ for c in atypical.is_a]}")
        
        # 5. INVERSE PROPERTY TEST
        print("\n5️⃣ INVERSE PROPERTIES:")
        if atypical:
            treating_brands = []
            for brand in self._get_class("Brand").instances():
                if hasattr(brand, 'treats') and atypical in getattr(brand, 'treats', []):
                    treating_brands.append(str(brand).split(".")[-1])
            print(f"   Brands treating AtypicalPneumonia: {treating_brands}")
        
        # 6. DATA PROPERTY INFERENCE
        print("\n6️⃣ DATA PROPERTIES:")
        w143 = self.graph.search_one(iri="*W143")
        if w143:
            headline = getattr(w143, 'hasWarningHeadline', ['N/A'])[0]
            print(f"   W143 headline: {headline}")
        
        # 7. COMPLEX QUERY TEST
        print("\n7️⃣ COMPLEX CHAIN: Antibiotic → Brand → Indication")
        chain_result = []
        for antibiotic in self._get_class("Antibiotic").instances():
            for brand in getattr(antibiotic, 'hasBrandName', []):
                for indication in getattr(brand, 'treats', []):
                    chain_result.append({
                        'antibiotic': str(antibiotic).split(".")[-1],
                        'brand': str(brand).split(".")[-1],
                        'indication': str(indication).split(".")[-1]
                    })
        print(f"   Found {len(chain_result)} treatment chains:")
        for item in chain_result[:3]:  # First 3
            print(f"     {item['antibiotic']} → {item['brand']} → {item['indication']}")
        
        # 8. SUBSTANCE INTERACTION BACKTRACKING
        print("\n8️⃣ SUBSTANCE BACKTRACKING:")
        antacids_interactions = self.find_interaction_by_substance("antacids")
        print(f"   Antacids affects {len(antacids_interactions)} interactions")
        
        # SUMMARY
        print(f"\n📊 SUMMARY {reasoner_status}:")
        print(f"   Total classes: {len(list(self.graph.classes()))}")
        print(f"   Total individuals: {len(list(self.graph.individuals()))}")
        print(f"   Antibiotics found: {len(self.find_entities('Antibiotic'))}")
        print(f"   Indications found: {len(self.find_entities('Indication'))}")
        

    # === REASONER-ENHANCED HELPERS ===
    def _get_class(self, class_name: str) -> Optional[owlready2.Class]:
        return self.graph.search_one(iri=f"*#{class_name}")

    def _get_instance_by_name(self, class_obj, name: str, case_sensitive: bool = False) -> Optional[owlready2.Thing]:
        if not class_obj:
            return None
        for instance in class_obj.instances():
            instance_name = str(instance).split(".")[-1]
            if (not case_sensitive and name.lower() in instance_name.lower()) or \
               (case_sensitive and instance_name == name):
                return instance
        return None

    def get_classes(self, class_name):
        """Get all instances of a given class"""
        return self.graph.search(iri=f"*#{class_name}")
        
    def find_entities(self, entity_name: str) -> List[str]:
        """Find all instances including subclasses (reasoner-enhanced)"""
        entities = []
        entity_class = self._get_class(entity_name)
        
        if entity_class:
            for entity in entity_class.instances():
                entity_name_clean = str(entity).split(".")[-1]
                entities.append(entity_name_clean)
        return sorted(set(entities))  # Deduplicate + sort

    def get_antibiotic_instance(self, antibiotic_name: str) -> Optional[owlready2.Thing]:
        """Get antibiotic instance (case-insensitive, reasoner-enhanced)"""
        Antibiotic = self._get_class("Antibiotic")
        return self._get_instance_by_name(Antibiotic, antibiotic_name)

    def get_brand_instance(self, brand_name: str) -> Optional[owlready2.Thing]:
        """Get brand instance (reasoner-enhanced)"""
        Brand = self._get_class("Brand")
        return self._get_instance_by_name(Brand, brand_name)

    # === ENHANCED QUERY METHODS ===
    def find_brands(self, antibiotic_name: str) -> List[str]:
        """Find brands using direct + inverse properties"""
        brands = set()
        antibiotic = self.get_antibiotic_instance(antibiotic_name)
        
        if antibiotic:
            # Direct: hasBrandName
            if hasattr(antibiotic, 'hasBrandName'):
                for brand in getattr(antibiotic, 'hasBrandName', []):
                    brands.add(str(brand).split(".")[-1])
            # Inverse: isBrandOf (reasoner-enhanced)
            if hasattr(antibiotic, 'isBrandOf'):
                for brand in getattr(antibiotic, 'isBrandOf', []):
                    brands.add(str(brand).split(".")[-1])
        return sorted(brands)

    def find_indications(self, brand_name: str) -> List[str]:
        """Find indications (reasoner finds subclasses too)"""
        indications = []
        brand = self.get_brand_instance(brand_name)
        
        if brand and hasattr(brand, 'treats'):
            for indication in getattr(brand, 'treats', []):
                indications.append(str(indication).split(".")[-1])
        return sorted(set(indications))

    def find_warnings(self, brand_name: str) -> List[Dict[str, str]]:
        """Enhanced: Warnings with full details"""
        warnings = []
        brand = self.get_brand_instance(brand_name)
        
        if brand and hasattr(brand, 'hasWarning'):
            for warning in getattr(brand, 'hasWarning', []):
                warning_info = {
                    'name': str(warning).split(".")[-1],
                    'headline': str(getattr(warning, 'hasWarningHeadline', ['N/A'])[0]) if hasattr(warning, 'hasWarningHeadline') else 'N/A',
                    'text': str(getattr(warning, 'hasWarningText', ['N/A'])[0]) if hasattr(warning, 'hasWarningText') else 'N/A'
                }
                warnings.append(warning_info)
        return warnings

    def find_side_effects(self, brand_name: str) -> List[Dict[str, Any]]:
        """Enhanced: Side effects with pattern/duration"""
        side_effects = []
        brand = self.get_brand_instance(brand_name)
        
        if brand and hasattr(brand, 'hasSideEffect'):
            for se in getattr(brand, 'hasSideEffect', []):
                se_info = {
                    'name': str(getattr(se, 'hasSideEffectName', ['N/A'])[0]) if hasattr(se, 'hasSideEffectName') else str(se).split(".")[-1],
                    'description': str(getattr(se, 'hasSideEffectDescription', ['N/A'])[0]) if hasattr(se, 'hasSideEffectDescription') else 'N/A',
                    'pattern': [str(p).split(".")[-1] for p in getattr(se, 'whichIs', [])],
                    'duration': [str(d).split(".")[-1] for d in getattr(se, 'lastsFor', [])]
                }
                side_effects.append(se_info)
        return side_effects

    def find_interactions(self, brand_name: str) -> List[Dict[str, Any]]:
        """Enhanced interactions with full details"""
        interactions = []
        brand = self.get_brand_instance(brand_name)
        
        if brand and hasattr(brand, 'hasInteraction'):
            for interaction in getattr(brand, 'hasInteraction', []):
                interaction_info = {
                    'name': str(interaction).split(".")[-1],
                    'substances': [str(s).split(".")[-1] for s in getattr(interaction, 'interactsWith', [])],
                    'description': str(getattr(interaction, 'hasInteractionDescription', ['N/A'])[0]) if hasattr(interaction, 'hasInteractionDescription') else 'N/A',
                    'clinical_effects': [str(v) for v in getattr(interaction, 'hasClinicalEffects', [])],
                    'management_advice': [str(v) for v in getattr(interaction, 'hasManagementAdvice', [])]
                }
                interactions.append(interaction_info)
        return interactions

    def find_stewardship(self, brand_name: str) -> List[Dict[str, str]]:
        """Enhanced stewardship with descriptions"""
        stewardship = []
        brand = self.get_brand_instance(brand_name)
        
        if brand and hasattr(brand, 'managedBy'):
            for sp in getattr(brand, 'managedBy', []):
                stewardship.append({
                    'name': str(sp).split(".")[-1],
                    'description': str(getattr(sp, 'hasStewardshipDescription', ['N/A'])[0]) if hasattr(sp, 'hasStewardshipDescription') else 'N/A'
                })
        return stewardship
    
    def find_interaction_by_substance(self, substance):
        """Pure backtracking - crystal clear path"""
        # Find substance
        substance_inst = self._get_instance_by_name(self._get_class("Substance"), substance)
        if not substance_inst:
            return []
        
        interactions_by_brand = {}
        
        # Brand → Interaction → Substance (backwards)
        for brand in self._get_class("Brand").instances():
            for interaction in getattr(brand, "hasInteraction", []):
                for substance_in_interaction in getattr(interaction, "interactsWith", []):
                    if substance_in_interaction == substance_inst:
                        brand_name = str(brand).split(".")[-1]
                        if brand_name not in interactions_by_brand:
                            interactions_by_brand[brand_name] = []
                        
                        interactions_by_brand[brand_name].append({
                            'interaction': str(interaction).split(".")[-1],
                            'description': str(getattr(interaction, 'hasInteractionDescription', ['N/A'])[0]),
                            'effects': [str(v) for v in getattr(interaction, 'hasClinicalEffects', [])],
                            'advice': [str(v) for v in getattr(interaction, 'hasManagementAdvice', [])]
                        })
        
        # Format results
        results = []
        for brand_name, interactions in interactions_by_brand.items():
            results.append({
                'brand': brand_name,
                'interactions': interactions
            })
        
        return results
                    

        
    
    def get_full_info(self, antibiotic_name: str) -> Dict[str, Any]:
        """Comprehensive info with per-brand details"""
        info = {
            'antibiotic': antibiotic_name,
            'brands': [],
            'drug_class': [],
            'indications': [],
            'warnings': [],
            'side_effects': [],
            'interactions': [],
            'stewardship': [],
            'brands_details': {}
        }
        
        # Get antibiotic drug class
        antibiotic = self.get_antibiotic_instance(antibiotic_name)
        if antibiotic and hasattr(antibiotic, 'hasDrugClass'):
            info['drug_class'] = [str(dc).split(".")[-1] for dc in getattr(antibiotic, 'hasDrugClass', [])]
        
        brands = self.find_brands(antibiotic_name)
        info['brands'] = brands
        
        # Per-brand details + aggregate
        for brand_name in brands:
            brand_info = {
                'indications': self.find_indications(brand_name),
                'warnings': self.find_warnings(brand_name),
                'side_effects': self.find_side_effects(brand_name),
                'interactions': self.find_interactions(brand_name),
                'stewardship': self.find_stewardship(brand_name)
            }
            info['brands_details'][brand_name] = brand_info
            
            # Aggregate unique values
            info['indications'].extend(brand_info['indications'])
            info['warnings'].extend(brand_info['warnings'])
            info['side_effects'].extend(brand_info['side_effects'])
            info['interactions'].extend(brand_info['interactions'])
            info['stewardship'].extend(brand_info['stewardship'])
        
        # Clean aggregates
        info['indications'] = sorted(set(info['indications']))
        
        return info

    def search_all(self, term: Optional[str] = None) -> Dict[str, List[str]]:
        """Enhanced search across all entity types"""
        results = {
            'antibiotics': self.find_entities('Antibiotic'),
            'brands': self.find_entities('Brand'),
            'indications': self.find_entities('Indication'),
            'warnings': self.find_entities('Warning'),
            'side_effects': self.find_entities('SideEffect'),
            'drug_classes': self.find_entities('DrugClass'),
            'substances': self.find_entities('Substance'),
            'stewardship': self.find_entities('StewardshipPrinciple')
        }
        return results

    def debug(self):
        """Enhanced debug with reasoner status"""
        print("=== Ontology Debug ===")
        print(f"Reasoner: {'✓ ' + self.reasoner_type.upper() if self.reasoner_applied else '✗ NONE'}")
        print(f"Classes: {len(list(self.graph.classes()))}")
        print(f"Individuals: {len(list(self.graph.individuals()))}")
        print(f"Antibiotics: {self.find_entities('Antibiotic')}")
        print(f"Brands: {self.find_entities('Brand')}")
        
        # Test inference
        if self.reasoner_applied:
            Doxin = self.get_brand_instance("Doxin")
            if Doxin:
                print(f"  Doxin treats: {[str(i).split('.')[-1] for i in getattr(Doxin, 'treats', [])]}")

# === USAGE EXAMPLE ===
if __name__ == "__main__":
    # Load ontology
    onto = get_ontology("your-ontology.owl").load()
    traversal = OntologyTraversal(onto)
    
    # Apply reasoner
    traversal.apply_reasoning("builtin")  # or "hermit"
    
    # Test queries
    print("\n=== FULL DOXYCYCLINE INFO ===")
    info = traversal.get_full_info("Doxycycline")
    print(json.dumps(info, indent=2, default=str))
    
    print("\n=== SEARCH ALL ===")
    search = traversal.search_all()
    for k, v in search.items():
        print(f"{k}: {len(v)}")
    
    traversal.debug()