import re
import os
from transformers import (
    pipeline, AutoModelForTokenClassification, AutoTokenizer, AutoConfig
)
import torch
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any
from services.ontology_service import ontology_service

class NERService:
    """Complete NER + Classification Service"""
    
    def __init__(self):
        self.device = 0 if torch.cuda.is_available() else -1
        self.min_word_length = 3
        self.invalid_types = {'O'}
        
        # Load everything ONCE at startup
        self.custom_terms = self._load_custom_terms()
        self.ner_pipelines = self._load_ner_models()
        self.ontology = self._load_ontology_once()
        
        print(f'NERService initialized on: {"GPU" if self.device == 0 else "CPU"}')
        print(f'Loaded {len(self.custom_terms)} custom terms')
        print(f'Loaded {len(self.ner_pipelines)} NER models')
    
    def _load_custom_terms(self) -> Dict[str, tuple]:
        """Load custom terms ONCE"""
        custom_terms = {}
        base_path = Path(__file__).parent.parent / "data/custom_terms"
        
        csv_files = [
            ('food.csv', 'FOOD'),
            ('beverage.csv', 'BEVERAGE'),
            ('antibiotic brands.csv', 'Brand'),
        ]
        
        for filename, label in csv_files:
            filepath = base_path / filename
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8-sig') as f:
                    for line in f:
                        term = line.strip()
                        if term:
                            custom_terms[term.lower()] = (term, label)
        
        return custom_terms
    
    def _load_ner_models(self) -> List:
        """Load all NER models ONCE"""
        model_base_path = Path("backend/models/biobert_ner_model")
        ner_model_paths = {
            'disease': model_base_path / 'OpenMed_OpenMed-NER-DiseaseDetect-SuperClinical-184M',
            'pharma': model_base_path / 'OpenMed_OpenMed-NER-PharmaDetect-BigMed-278M',
            'adverse': model_base_path / 'jsylee_scibert_scivocab_uncased-finetuned-ner',
        }
        
        pipelines = []
        
        # Standard models
        for name, path in ner_model_paths.items():
            if name == 'adverse' or not path.exists():
                continue
                
            try:
                p = pipeline(
                    'ner', model=str(path), tokenizer=str(path),
                    aggregation_strategy='max', device=self.device
                )
                pipelines.append(p)
                print(f'  [LOADED] {path}')
            except Exception as e:
                print(f'  [FAIL] {path} — {e}')
        
        # Adverse model (special handling)
        adverse_path = ner_model_paths['adverse']
        if adverse_path.exists():
            try:
                id2label = {0: 'O', 1: 'B-DRUG', 2: 'I-DRUG', 3: 'B-EFFECT', 4: 'I-EFFECT'}
                config = AutoConfig.from_pretrained(str(adverse_path), id2label=id2label)
                
                model = AutoModelForTokenClassification.from_pretrained(
                    str(adverse_path), config=config, ignore_mismatched_sizes=True
                )
                tokenizer = AutoTokenizer.from_pretrained(str(adverse_path))
                
                pipeline_obj = pipeline(
                    'ner', model=model, tokenizer=tokenizer,
                    aggregation_strategy='max', device=self.device
                )
                pipelines.append(pipeline_obj)
                print(f'  [LOADED] {adverse_path}')
            except Exception as e:
                print(f'  [FAIL] {adverse_path} — {e}')
        
        return pipelines
    
    def _load_ontology_once(self) -> Dict[str, List[str]]:
        """LOAD ONCE - No more DB queries per entity!"""
        try:
            entities = defaultdict(list)

            brands = ontology_service.find_entities(entity_name="Brand") or []
            antibiotics = ontology_service.find_entities(entity_name="Antibiotic") or []
            side_effect = ontology_service.find_subclasses(entity_name="SideEffect") or []
            
            substances = []
            for substance_type in ["Drug", "Food", "Beverage"]:
                substances.extend(ontology_service.find_entities(substance_type))

            entities['Antibiotic'].extend(antibiotics)
            entities['Brand'].extend(brands)
            entities['SideEffect'].extend(side_effect)
            entities['Substance'].extend(substances)

            print(f"Filled entities: {entities}")

            return entities
        except AttributeError:
            print("⚠️  Ontology methods not found - using empty lists")
            return {'BrandS': [], 'GenericS': [], 'DRUG_CLASSES': [], 'SideEffectS': []}
    
    def clean_entity(self, word: str) -> str:
        """Clean entity text"""
        return re.sub(r'[^\w\s\-]', '', word.strip()).strip()
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities from text"""
        biobert_added = set()
        custom_added = set()
        results = []
        
        # BioBERT NER
        for pipeline in self.ner_pipelines:
            try:
                entities = pipeline(text[:512])
                for ent in entities:
                    word = self.clean_entity(ent['word'])
                    
                    if (word.startswith('##') or 
                        len(word) < self.min_word_length or 
                        ent['entity_group'] in self.invalid_types):
                        continue
                    
                    entity_type = ent['entity_group']
                    if entity_type.startswith('B-') or entity_type.startswith('I-'):
                        entity_type = entity_type[2:]
                    
                    word_lower = word.lower()
                    
                    # Custom term override
                    if word_lower in self.custom_terms:
                        term_original, custom_label = self.custom_terms[word_lower]
                        results.append({
                            'entity': term_original,
                            'entity_type': custom_label,
                            'confidence': round(ent['score'], 4),
                            'source': 'custom'
                        })
                        custom_added.add(word_lower)
                        continue
                    
                    results.append({
                        'entity': word,
                        'entity_type': entity_type,
                        'confidence': round(ent['score'], 4),
                        'source': 'biobert'
                    })
                    biobert_added.add(word_lower)
                    
            except Exception as e:
                print(f"NER pipeline error: {e}")
                continue
        
        # Fallback custom terms
        for term_lower, (term_original, label) in self.custom_terms.items():
            if (re.search(r'\b' + re.escape(term_lower) + r'\b', text.lower()) and 
                term_lower not in custom_added):
                results.append({
                    'entity': term_original,
                    'entity_type': label,
                    'confidence': 1.0,
                    'source': 'custom'
                })
        
        return results
    
    def classify_entities(self, question_entities: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Classify CHEM → Brand/Generic + DISEASE → SideEffect"""
        result = defaultdict(list)
        
        # Classify CHEM (memory lookup only - FAST!)
        for chem in question_entities.get('CHEM', []):
            print("ENTITY CHEM", chem)

            print("CHECKING OF READ ONTOLGOY", self.ontology['Brand'])
            if chem in self.ontology['Brand']:
                result['Brand'].append(chem)
            elif chem in self.ontology['Antibiotic']:
                result['Generic'].append(chem)
            elif chem in self.ontology['Substance']:
                result['Substance'].append(chem)
        
        # Classify DISEASE → SideEffect (memory lookup)
        for disease in question_entities.get('EFFECT', []):
            if disease in self.ontology['SideEffect']:
                result['SideEffect'].append(disease)
        
        return dict(result)
    
    def identify_query_type(self, entity_types: Dict[str, List[str]]) -> str:
        """Determine query type from classified entities"""
        
        patterns = {
            frozenset(['Generic', 'Brand', 'SideEffect']): 'generic_brand_side_effects',
            frozenset(['Generic', 'Brand', 'Substance']): 'generic_brand_substance',
            frozenset(['Brand', 'SideEffect']): 'brand_side_effects',
            frozenset(['Brand', 'Substance']): 'brand_substance',
            frozenset(['Generic', 'SideEffect']): 'generic_side_effects',
            frozenset(['Generic', 'Substance']): 'generic_substance',
            frozenset(['Generic', 'Brand']): 'generic_brand',
            frozenset(['Generic']): 'generic',
            frozenset(['Brand']): 'brand',
            frozenset(['SideEffect']): 'side_effects_only',
        }
        
        for pattern, qtype in patterns.items():
            if pattern.issubset(set(entity_types)):
                return qtype
        
        return 'unknown_query_type'

ner_service = NERService()

