from typing import List
import services.ontology_service as ontology_service
import services.intent_handler as intent_handler
import os

import torch
import pickle
import numpy as np
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

EXPORT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models/distilbert")
EXPORT_DIR = os.path.normpath(EXPORT_DIR)
MAX_LEN    = 128
DEVICE     = torch.device("cuda" if torch.cuda.is_available() else "cpu")

_model     = DistilBertForSequenceClassification.from_pretrained(EXPORT_DIR).to(DEVICE)
_tokenizer = DistilBertTokenizerFast.from_pretrained(EXPORT_DIR)
_model.eval()

with open(os.path.join(EXPORT_DIR, "label_encoder.pkl"), "rb") as f:
    _le = pickle.load(f)

print(f"Intent model loaded on {DEVICE}")

INTENT_THRESHOLDS = {
    'get_antibiotic_info':          0.70, # adjusted
    'get_uses_indications':         0.50,
    'get_side_effects':             0.85,  # adjusted
    'get_substance_interaction':    0.90,  # adjusted
    'get_warning_precautions':      0.90,  # adjusted
    'get_storage_instruction':      0.75, # adjusted
    'get_food_and_timing':          0.75, # adjusted
    'get_administration_instruction': 0.75, # adjusted
    'redirect_medicine_query':      0.40
}

def identify_intent(text: str) -> str:
    encoding = _tokenizer(
        text,
        max_length=MAX_LEN,
        padding="max_length",
        truncation=True,
        return_tensors="pt"
    )

    input_ids      = encoding["input_ids"].to(DEVICE)
    attention_mask = encoding["attention_mask"].to(DEVICE)

    with torch.no_grad():
        logits = _model(input_ids=input_ids, attention_mask=attention_mask).logits

    probs      = torch.softmax(logits, dim=1).squeeze().cpu().numpy()
    top_idx    = int(np.argmax(probs))
    confidence = float(probs[top_idx])
    intent     = _le.inverse_transform([top_idx])[0]

    # Look up the threshold for this specific predicted label
    threshold = INTENT_THRESHOLDS.get(intent)

    print(f"[Intent] '{intent}' | confidence: {confidence:.2f} | threshold: {threshold}")

    if confidence < threshold:
        return 'is_not_recognized'

    return intent


# ── Replace keyword matching with model prediction ────────────────────────────
def identify_intent(text: str, confidence_threshold: float = 0.4) -> str:
    """
    Takes the raw user question (string) and returns the predicted intent label.
    Falls back to 'unknown_intent' if confidence is too low.
    """
    encoding = _tokenizer(
        text,
        max_length=MAX_LEN,
        padding="max_length",
        truncation=True,
        return_tensors="pt"
    )

    input_ids      = encoding["input_ids"].to(DEVICE)
    attention_mask = encoding["attention_mask"].to(DEVICE)

    with torch.no_grad():
        logits = _model(input_ids=input_ids, attention_mask=attention_mask).logits

    probs      = torch.softmax(logits, dim=1).squeeze().cpu().numpy()
    top_idx    = int(np.argmax(probs))
    confidence = float(probs[top_idx])
    intent     = _le.inverse_transform([top_idx])[0]

    print(f"[Intent] '{intent}' ({confidence:.2f})")  # helpful for debugging

    if confidence < confidence_threshold:
        return 'is_not_recognized'

    return intent

def identify_entities_present(entity_types):
    generic_brand = ['Antibiotic', 'Brand']
    generic = ['Antibiotic']
    substance = ['Substance']
    generic_substance = ['Antibiotic', 'Substance']
    brand_substance = ['Brand', 'Substance']
    warning = ['Warning']
    generic_brand_side_effects = ['Antibiotic', 'Brand', 'SideEffect']
    brand_side_effects = ['Brand', 'SideEffect']
    generic_side_effects = ['Antibiotic', 'SideEffect']
    generic_warning = ['Antibiotic', 'Warning']
    brand_warning = ['Brand', 'Warning']

    if all (e in entity_types for e in generic_substance):
        return 'generic_substance'
    elif all (e in entity_types for e in brand_substance):
        return 'brand_substance'
    elif all (e in entity_types for e in generic_warning):
        return 'generic_warning'
    elif all (e in entity_types for e in brand_warning):
        return 'brand_warning'
    elif all (e in entity_types for e in warning):
        return 'warning'
    elif all (e in entity_types for e in generic_brand_side_effects):
        return 'generic_brand_side_effects'
    elif all (e in entity_types for e in brand_side_effects):
        return 'brand_side_effects'
    elif all (e in entity_types for e in generic_side_effects):
        return 'generic_side_effects'
    elif all (e in entity_types for e in generic_brand):
        return 'generic_brand'
    elif all (e in entity_types for e in generic):
        return 'generic'
    elif all(e == 'Brand' for e in entity_types):
        entity_types_list = list(entity_types)
        if entity_types_list.count('Brand') > 1:
            return 'multiple_brands'
        return 'brand'
    elif all (e in entity_types for e in substance):
        return 'substance'
    else:
        return 'unknown_entity_combination'
    
def handle_intent(intent, query_type, question_entities):
    if intent == 'GET_ANTIBIOTIC_INFO':
        print("TO ROUTE IN INTENT HANDLER")
        return intent_handler.handle_antibiotic_info(question_entities, query_type)
    elif intent == 'GET_USES_INDICATIONS':
        return intent_handler.handle_uses_indications(question_entities, query_type)
    elif intent == 'GET_SIDE_EFFECTS':
        return intent_handler.handle_side_effects(question_entities, query_type)
    elif intent == 'GET_SUBSTANCE_INTERACTION':
        return intent_handler.handle_substance_interaction(question_entities, query_type)
    elif intent == 'GET_WARNING_PRECAUTIONS':
        return intent_handler.handle_warning_precautions(question_entities, query_type)
    elif intent == 'GET_STORAGE_INSTRUCTIONS':
        return intent_handler.handle_storage_instruction(question_entities, query_type)
    elif intent == 'GET_FOOD_AND_TIMING':
        return intent_handler.handle_food_and_timing(question_entities, query_type)
    elif intent == 'GET_ADMINISTRATION_INSTRUCTION':
        return intent_handler.handle_administration_instructions(question_entities, query_type)
    elif intent == 'IS_NOT_RECOGNIZED':
        return intent_handler.handle_is_not_recognized()
    elif intent == 'REDIRECT_MEDICINE_QUER':
        return intent_handler.handle_redirect_medicine_query()
    else:
        print("Sorry, I couldn't understand your question. Could you please rephrase it?")
        return None
    
        
