"""
search.py — ConvoLens semantic search engine
Handles semantic, attributed, temporal, and mixed queries over a chat corpus.
"""

import os
os.environ["HF_HUB_OFFLINE"] = "0"

import json
import re
import numpy as np
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer

DATA_PATH = "data/chat.jsonl"
EMBED_CACHE = "data/embeddings.npy"
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
MIN_SCORE_THRESHOLD = 0.30

print("Loading model...")
model = SentenceTransformer(MODEL_NAME)

with open(DATA_PATH, "r", encoding="utf-8") as f:
    messages = [json.loads(line) for line in f]

for m in messages:
    m["dt"] = datetime.fromisoformat(m["timestamp"])

if os.path.exists(EMBED_CACHE):
    print("Loading cached embeddings...")
    embeddings = np.load(EMBED_CACHE)
else:
    print("Computing embeddings (first run, this takes a minute)...")
    texts = [m["text"] for m in messages]
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    np.save(EMBED_CACHE, embeddings)

CORPUS_START = min(m["dt"] for m in messages)
CORPUS_END = max(m["dt"] for m in messages)

def cosine_scores(query_embedding, candidate_embeddings):
    return candidate_embeddings @ query_embedding

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
}

def detect_sender(query):
    for m in messages:
        if re.search(rf"\b{re.escape(m['sender'].lower())}\b", query.lower()):
            return m["sender"]
    return None

def detect_date_range(query):
    q = query.lower()
    now = CORPUS_END

    if "last month" in q:
        end = now.replace(day=1) - timedelta(days=1)
        start = end.replace(day=1)
        return start, end + timedelta(days=1)

    if "this month" in q:
        start = now.replace(day=1)
        return start, now + timedelta(days=1)

    for month_name, month_num in MONTHS.items():
        if month_name in q:
            year = now.year
            start = datetime(year, month_num, 1)
            end = datetime(year + 1, 1, 1) if month_num == 12 else datetime(year, month_num + 1, 1)
            return start, end

    if "recently" in q or "recent" in q:
        return now - timedelta(days=14), now + timedelta(days=1)

    return None

def get_context(msg_id, window=3):
    idx = next((i for i, m in enumerate(messages) if m["id"] == msg_id), None)
    if idx is None:
        return []
    start = max(0, idx - window)
    end = min(len(messages), idx + window + 1)
    return [
        {"id": messages[i]["id"], "sender": messages[i]["sender"],
         "text": messages[i]["text"], "timestamp": messages[i]["timestamp"]}
        for i in range(start, end)
    ]

def semantic_search(query, candidate_indices=None, top_k=5, recency_boost=False):
    query_embedding = model.encode([query], normalize_embeddings=True)[0]

    if candidate_indices is None:
        candidate_indices = list(range(len(messages)))

    if len(candidate_indices) == 0:
        return []

    candidate_embeddings = embeddings[candidate_indices]
    scores = cosine_scores(query_embedding, candidate_embeddings)

    if recency_boost:
        max_ts = max(messages[i]["dt"].timestamp() for i in candidate_indices)
        min_ts = min(messages[i]["dt"].timestamp() for i in candidate_indices)
        span = max(max_ts - min_ts, 1)
        for j, idx in enumerate(candidate_indices):
            recency = (messages[idx]["dt"].timestamp() - min_ts) / span
            scores[j] = scores[j] * 0.9 + recency * 0.1

    top_k = min(top_k, len(scores))
    top_order = np.argsort(scores)[::-1][:top_k]

    results = []
    for j in top_order:
        score = float(scores[j])
        if score < MIN_SCORE_THRESHOLD:
            continue
        idx = candidate_indices[j]
        msg = messages[idx]
        results.append({
            "id": msg["id"],
            "sender": msg["sender"],
            "text": msg["text"],
            "timestamp": msg["timestamp"],
            "score": round(score, 3),
            "context": get_context(msg["id"]),
        })
    return results

def get_raw_score(query, message_id):
    query_embedding = model.encode([query], normalize_embeddings=True)[0]
    idx = next((i for i, m in enumerate(messages) if m["id"] == message_id), None)
    if idx is None:
        return None
    return float(cosine_scores(query_embedding, embeddings[idx:idx+1])[0])

def search(query, top_k=5):
    sender = detect_sender(query)
    date_range = detect_date_range(query)

    candidate_indices = list(range(len(messages)))
    explanation_parts = []

    if sender:
        candidate_indices = [i for i in candidate_indices if messages[i]["sender"] == sender]
        explanation_parts.append(f"filtering by sender '{sender}'")

    if date_range:
        start, end = date_range
        candidate_indices = [i for i in candidate_indices if start <= messages[i]["dt"] < end]
        explanation_parts.append(f"filtering by date range {start.date()} to {end.date()}")

    recency_boost = date_range is not None

    if sender and date_range:
        query_type = "mixed (attributed + temporal)"
    elif sender:
        query_type = "attributed"
    elif date_range:
        query_type = "temporal"
    else:
        query_type = "semantic"

    explanation = f"Detected: {query_type} query"
    if explanation_parts:
        explanation += " — " + ", ".join(explanation_parts)

    if not candidate_indices:
        return [], explanation + " (no messages match these filters)"

    results = semantic_search(query, candidate_indices=candidate_indices, top_k=top_k, recency_boost=recency_boost)
    return results, explanation

if __name__ == "__main__":
    print(f"\nConvoLens ready. {len(messages)} messages loaded. Model: {MODEL_NAME}")
    print("Type a query (or 'exit' to quit)\n")

    while True:
        query = input("Search> ").strip()
        if query.lower() in ("exit", "quit"):
            break
        if not query:
            continue

        results, explanation = search(query)
        print(f"\n[{explanation}]")

        if not results:
            print("No matching messages found.\n")
            continue

        for r in results:
            print(f"\n  Score: {r['score']}  |  {r['sender']} @ {r['timestamp']}")
            print(f"  >> {r['text']}")
            print("  --- context ---")
            for c in r["context"]:
                marker = ">>" if c["id"] == r["id"] else "  "
                print(f"  {marker} {c['sender']}: {c['text']}")
        print()