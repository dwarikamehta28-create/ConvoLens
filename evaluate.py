"""
evaluate.py — Runs all test queries through search.py and reports accuracy + raw score diagnostics.
"""

import json
from search import search, get_raw_score, MIN_SCORE_THRESHOLD

with open("data/test_queries.json", "r", encoding="utf-8") as f:
    test_queries = json.load(f)

correct = 0
total_evaluated = 0
answerable_raw_scores = []
not_covered_scores = []
temporal_skipped = 0

print(f"Running {len(test_queries)} test queries...\n")
print("=" * 70)

for tq in test_queries:
    query = tq["query"]
    expected = tq["answer_id"]

    results, explanation = search(query, top_k=5)
    got_ids = [r["id"] for r in results]

    if expected == "NOT_COVERED":
        top_score = results[0]["score"] if results else 0.0
        not_covered_scores.append(top_score)
        total_evaluated += 1
        status = "PASS (correctly empty)" if not results else f"FAIL (returned {got_ids})"
        if not results:
            correct += 1
        print(f"[{status}] '{query}' | top_score={top_score}")

    elif expected is None:
        temporal_skipped += 1
        print(f"[INFO] '{query}' -> {explanation} | returned {len(results)} results")

    else:
        raw_score = get_raw_score(query, expected)
        answerable_raw_scores.append(raw_score)
        total_evaluated += 1
        hit = expected in got_ids
        status = "PASS" if hit else "FAIL"
        if hit:
            correct += 1
        print(f"[{status}] '{query}'")
        print(f"    expected_id={expected} | got_ids={got_ids} | RAW score of expected answer={raw_score:.3f}")

print("=" * 70)
print(f"\nAccuracy: {correct}/{total_evaluated} ({100*correct/total_evaluated:.1f}%)")
print(f"(Temporal-only queries not auto-scored: {temporal_skipped})")

print(f"\nCurrent threshold: {MIN_SCORE_THRESHOLD}")
if answerable_raw_scores:
    print(f"RAW score of correct answers — min: {min(answerable_raw_scores):.3f} | avg: {sum(answerable_raw_scores)/len(answerable_raw_scores):.3f} | max: {max(answerable_raw_scores):.3f}")
if not_covered_scores:
    print(f"Not-covered top score — min: {min(not_covered_scores):.3f} | avg: {sum(not_covered_scores)/len(not_covered_scores):.3f} | max: {max(not_covered_scores):.3f}")