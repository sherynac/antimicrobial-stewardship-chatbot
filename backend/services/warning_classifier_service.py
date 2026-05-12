import json
import torch
import torch.nn.functional as F
import pandas as pd
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification


class WarningClassifierService:

    def __init__(self, model_dir: str, signal_words_csv: str, max_len: int = 128):
        self.max_len = max_len
        self.device  = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Load label names
        with open(f'{model_dir}/label_encoder_classes.json', 'r') as f:
            self.labels = json.load(f)

        # Load signal words from CSV
        sig_df = pd.read_csv(signal_words_csv)
        self.warning_signal_words = (
            sig_df['signal_word']
            .astype(str)
            .str.strip()
            .str.lower()
            .tolist()
        )

        # Load tokenizer and model
        self.tokenizer = DistilBertTokenizerFast.from_pretrained(model_dir)
        self.model     = DistilBertForSequenceClassification.from_pretrained(model_dir)
        self.model.to(self.device)
        self.model.eval()

        print(f'WarningClassifierService ready')
        print(f'  Model dir    : {model_dir}')
        print(f'  Device       : {self.device}')
        print(f'  Labels       : {self.labels}')
        print(f'  Signal words : {len(self.warning_signal_words)} loaded from {signal_words_csv}')

    def has_warning_signal(self, text: str) -> bool:
        text_lower = text.lower()
        return any(sig in text_lower for sig in self.warning_signal_words)

    def predict(self, text: str) -> dict:
        if not self.has_warning_signal(text):
            return {
                'text'                  : text,
                'has_warning_signal'    : False,
                'predicted_warning_type': None,
                'confidence'            : None,
            }

        inputs = self.tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=self.max_len,
            return_tensors='pt'
        )
        input_ids      = inputs['input_ids'].to(self.device)
        attention_mask = inputs['attention_mask'].to(self.device)

        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)

        probs            = F.softmax(outputs.logits, dim=-1)
        top_prob, top_id = torch.max(probs, dim=-1)

        return {
            'text'                  : text,
            'has_warning_signal'    : True,
            'predicted_warning_type': self.labels[top_id.item()],
            'confidence'            : round(top_prob.item(), 4),
        }

    def predict_batch(self, texts: list) -> list:
        candidate_texts   = []
        candidate_indices = []
        results           = [None] * len(texts)

        for i, text in enumerate(texts):
            if self.has_warning_signal(text):
                candidate_texts.append(text)
                candidate_indices.append(i)
            else:
                results[i] = {
                    'text'                  : text,
                    'has_warning_signal'    : False,
                    'predicted_warning_type': None,
                    'confidence'            : None,
                }

        if candidate_texts:
            inputs = self.tokenizer(
                candidate_texts,
                truncation=True,
                padding=True,
                max_length=self.max_len,
                return_tensors='pt'
            )
            input_ids      = inputs['input_ids'].to(self.device)
            attention_mask = inputs['attention_mask'].to(self.device)

            with torch.no_grad():
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)

            probs              = F.softmax(outputs.logits, dim=-1)
            top_probs, top_ids = torch.max(probs, dim=-1)

            for i, (top_id, top_prob) in enumerate(zip(top_ids.tolist(), top_probs.tolist())):
                results[candidate_indices[i]] = {
                    'text'                  : candidate_texts[i],
                    'has_warning_signal'    : True,
                    'predicted_warning_type': self.labels[top_id],
                    'confidence'            : round(top_prob, 4),
                }

        return results