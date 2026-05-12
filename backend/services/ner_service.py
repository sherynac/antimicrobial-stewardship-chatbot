import re
import os
from transformers import (
    pipeline,
    AutoModelForTokenClassification,
    AutoTokenizer,
    AutoConfig,
)
import torch

    
MODEL_BASE_PATH =  r'C:\Users\reyro\Downloads\antimicrobial-stewardship-chatbot\nlp\biobert_ner_model'

NER_MODEL_PATHS = {
    'disease': os.path.join(MODEL_BASE_PATH, 'OpenMed_OpenMed-NER-DiseaseDetect-SuperClinical-184M'),
    'pharma': os.path.join(MODEL_BASE_PATH, 'OpenMed_OpenMed-NER-PharmaDetect-BigMed-278M'),
    'adverse': os.path.join(MODEL_BASE_PATH, 'jsylee_scibert_scivocab_uncased-finetuned-ner'),
}

print("Working dir:", os.getcwd())

for name, path in NER_MODEL_PATHS.items():
    print(f"Checking: {path} | Exists: {os.path.exists(path)}")

WARNING_LABELS = [
    'Contraindication',
    'Pregnancy and Lactation',
    'Overdosage',
    'Patient Condition',
    'Age Restriction',
    'General Warning',
]

# Entity types to filter out
INVALID_TYPES  = {'O'}
MIN_WORD_LENGTH = 3

CUSTOM_TERMS = {}

BASE_PATH = r'C:\Users\reyro\Downloads\antimicrobial-stewardship-chatbot\backend\data\custom_terms'

csv_files = [
    ('food.csv', 'FOOD'),
    ('beverage.csv', 'BEVERAGE'),
    ('antibiotic brands.csv', 'BRAND'),
]

def load_custom_terms_from_file(filepath, label):
    terms = {}
    if not os.path.exists(filepath):
        print(f'Custom terms file not found: {filepath}')
        return terms
    with open(filepath, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
        for line in f:
            t = line.strip()
            if t:
                terms[t.lower()] = (t, label)
    return terms

for filename, label in csv_files:
    filepath = os.path.join(BASE_PATH, filename)
    loaded = load_custom_terms_from_file(filepath, label)
    CUSTOM_TERMS.update(loaded)

print(f"Loaded {len(CUSTOM_TERMS)} custom terms.")


device = 0 if torch.cuda.is_available() else -1
print(f'Loading models on: {"GPU" if device == 0 else "CPU"}')

ner_pipelines = []

# Load standard NER models
for name, path in NER_MODEL_PATHS.items():
    if name == 'adverse':
        continue  # handled separately below
    if not os.path.exists(path):
        print(f'  [MISSING] {path}')
        continue
    try:
        p = pipeline(
            'ner',
            model=path,
            tokenizer=path,
            aggregation_strategy='max',
            device=device
        )
        ner_pipelines.append(p)
        print(f'  [LOADED] {path}')
    except Exception as e:
        print(f'  [FAIL] {path} — {e}')

# Load jsylee adverse effects model with manual label mapping
adverse_path = NER_MODEL_PATHS['adverse']
if os.path.exists(adverse_path):
    try:
        id2label = {0: 'O', 1: 'B-DRUG', 2: 'I-DRUG', 3: 'B-EFFECT', 4: 'I-EFFECT'}
        label2id = {v: k for k, v in id2label.items()}

        config = AutoConfig.from_pretrained(adverse_path)
        config.id2label = id2label
        config.label2id = label2id
        config.num_labels = 5

        jsylee_model = AutoModelForTokenClassification.from_pretrained(
            adverse_path,
            config=config,
            ignore_mismatched_sizes=True
        )
        jsylee_tokenizer = AutoTokenizer.from_pretrained(adverse_path)
        jsylee_pipeline = pipeline(
            'ner',
            model=jsylee_model,
            tokenizer=jsylee_tokenizer,
            aggregation_strategy='max',
            device=device
        )
        ner_pipelines.append(jsylee_pipeline)
        print(f'  [LOADED] {adverse_path}')
    except Exception as e:
        print(f'  [FAIL] {adverse_path} — {e}')

print('All models loaded.')

def clean_entity(word):
    word = word.strip()
    word = re.sub(r'[^\w\s\-]', '', word).strip()
    return word


def extract_entities(text):
    biobert_added = set()
    custom_added  = set()
    results = []

    # BioBERT entities
    for ner_pipeline in ner_pipelines:
        try:
            entities = ner_pipeline(text[:512])
        except Exception as e:
            print("NER pipeline error:", e)
            continue

        for ent in entities:
            word        = clean_entity(ent['word'])
            entity_type = ent['entity_group'].strip()

            if word.startswith('##'):
                continue
            if len(word) < MIN_WORD_LENGTH:
                continue
            if entity_type in INVALID_TYPES:
                continue
            if entity_type.startswith('B-') or entity_type.startswith('I-'):
                entity_type = entity_type[2:]
            if word.lower() in biobert_added:
                continue

            word_lower = word.lower()

            # ---- OVERRIDE: if word is a custom term, use custom label ----
            if word_lower in CUSTOM_TERMS:
                term_original, custom_label = CUSTOM_TERMS[word_lower]
                results.append({
                    'entity'      : term_original,
                    'entity_type' : custom_label,
                    'confidence'  : round(ent['score'], 4),
                    'source'      : 'custom',
                })
                biobert_added.add(word_lower)
                custom_added.add(word_lower)  # prevent duplicate in custom pass
                continue
            # --------------------------------------------------------------

            results.append({
                'entity'      : word,
                'entity_type' : entity_type,
                'confidence'  : round(ent['score'], 4),
                'source'      : 'biobert',
            })
            biobert_added.add(word_lower)

    # Custom terms — catches terms BioBERT missed entirely
    for term_lower, value in CUSTOM_TERMS.items():
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            continue

        term_original, label = value
        pattern = r'\b' + re.escape(term_lower) + r'\b'
        if re.search(pattern, text.lower()) and term_lower not in custom_added:
            results.append({
                'entity'      : term_original,
                'entity_type' : label,
                'confidence'  : 1.0,
                'source'      : 'custom',
            })
            custom_added.add(term_lower)

    return results

def analyze(text):
    """
    Main function — call this from your chatbot backend.
    Returns entities and warning type for a given question.
    """
    return {
        'question'    : text,
        'entities'    : extract_entities(text),
    }

# 
def main():
    test_questions = [
        "What are the contraindications for Doxin?",
        "Can I take Penicillin while pregnant?",
        "What should I do in case of an overdose of Doxycycline?",
        "Are there any warnings for elderly patients taking Doxin?",
        "Is Doxyclen safe for children under 12?",
        "What are the general warnings for Doxin?",
        "What is beer and milk",
        "Do you like Bread",
    ]

    for q in test_questions:
        print(f'Question: {q}')
        entities = extract_entities(q)
        print(f'Extracted Entities: {entities}')

main()

