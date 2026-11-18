"""Polite-phrase notes for the robot conversation (thanks / please).

Kept apart from genai/data/corpus.json so the GenAI corpus stays exactly as evaluated
(frozen before the D16 evaluation). The robot adds these documents to what it retrieves.
"""
import json
from pathlib import Path

POLITE = json.loads((Path(__file__).with_name('polite_corpus.json')).read_text(encoding='utf-8'))

def polite_documents(text):
    from genai.service import tokens
    words = set(tokens(text))
    scored = []
    for doc in POLITE:
        overlap = len(words & set(tokens(doc['keywords'])))
        if overlap: scored.append((overlap, doc))
    return [doc for _, doc in sorted(scored, key=lambda pair: -pair[0])]
