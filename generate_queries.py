import json

with open("data/chat.jsonl", "r", encoding="utf-8") as f:
    messages = [json.loads(line) for line in f]

def find_id(text_snippet, sender=None):
    for m in messages:
        if text_snippet.lower() in m["text"].lower():
            if sender is None or m["sender"] == sender:
                return m["id"]
    return None

queries = [
    # --- Semantic queries (paraphrased, meaning-based) ---
    {"query": "which place did the group finally agree to visit", "answer_id": find_id("chalo manali hi fix")},
    {"query": "did they pick a cold hill station for the trip", "answer_id": find_id("manali try karte")},
    {"query": "how much budget was approved for the farewell party", "answer_id": find_id("mai 2500 hi final")},
    {"query": "till what date is the project submission extended", "answer_id": find_id("20 tarikh tk")},
    {"query": "is it confirmed that the deadline was pushed", "answer_id": find_id("confirm h ye")},
    {"query": "when is the group planning to travel", "answer_id": find_id("dec ke last week")},
    {"query": "how much money does each person need for the trip", "answer_id": find_id("per head 6-7k")},
    {"query": "did someone want to go somewhere cool because of the heat", "answer_id": find_id("thanda jagah dekhte")},
    {"query": "who said they will join the trip", "answer_id": find_id("mai bhi confirm")},
    {"query": "was there an announcement about mess meal timings", "answer_id": find_id("mess timing changed")},
    {"query": "is there a deadline for paying college fees", "answer_id": find_id("fee submission deadline")},
    {"query": "did people feel relieved after the deadline news", "answer_id": find_id("thodi neend le skte")},
    {"query": "was low attendance mentioned as a concern", "answer_id": find_id("attendance kam h")},
    {"query": "is college closed tomorrow", "answer_id": find_id("haan holiday hai")},
    {"query": "did someone ask if the exam form was filled", "answer_id": find_id("exam form bhara")},

    # --- Attributed queries (person-based) ---
    {"query": "what did Palak say about the party budget", "answer_id": find_id("2500 hi final", sender="Palak")},
    {"query": "what did Dwarika decide about the manali trip", "answer_id": find_id("chalo manali hi fix", sender="Dwarika")},
    {"query": "what update did Apurva give about the deadline", "answer_id": find_id("20 tarikh tk", sender="Apurva")},
    {"query": "what did Argha suggest for the trip location", "answer_id": find_id("thanda jagah", sender="Argha")},
    {"query": "what did Priyanshi ask about the trip dates", "answer_id": find_id("dates kab", sender="Priyanshi")},
    {"query": "did Sugna confirm she's coming on the trip", "answer_id": find_id("mai bhi confirm", sender="Sugna")},
    {"query": "what concern did Drishti raise about the venue", "answer_id": find_id("venue bhi to dekhna", sender="Drishti")},
    {"query": "what did Apurva mention about the deadline mail", "answer_id": find_id("mail bhi aaya", sender="Apurva")},

    # --- Temporal queries ---
    {"query": "what did we discuss in January", "answer_id": None},
    {"query": "what did we discuss last month", "answer_id": None},
    {"query": "any messages from March", "answer_id": None},

    # --- Mixed (attributed + temporal) ---
    {"query": "what did Dwarika say recently", "answer_id": None},

    # --- Hard semantic: NO word overlap with answer ---
    {"query": "who is responsible for covering the venue cost", "answer_id": find_id("venue ka bhi budget")},
    {"query": "was the holiday destination finalized", "answer_id": find_id("chalo manali hi fix")},
    {"query": "did the group feel less stressed after the deadline update", "answer_id": find_id("thank god")},
    {"query": "is low attendance a worry for anyone", "answer_id": find_id("attendance kam h")},
    {"query": "was a change in dining hall timing announced", "answer_id": find_id("mess timing changed")},
    {"query": "did anyone agree to come for the group outing", "answer_id": find_id("mai bhi confirm")},
    {"query": "has the cost per head for the trip been settled", "answer_id": find_id("per head 6-7k")},
    {"query": "did people feel thankful about the new due date", "answer_id": find_id("thank god")},

    # --- Extra plain queries ---
    {"query": "someone stuck in traffic", "answer_id": find_id("traffic h bohot")},
    {"query": "someone just woke up", "answer_id": find_id("abhi uthi hu")},
    {"query": "internet connectivity issue", "answer_id": find_id("network issue")},
    {"query": "request to share class notes", "answer_id": find_id("notes banaye")},
    {"query": "plan to watch a movie together", "answer_id": find_id("movie chalein")},

    # --- Genuinely NOT covered ---
    {"query": "kal weather kaisa rahega", "answer_id": "NOT_COVERED"},
    {"query": "kisne exam diya aur kisne nahi", "answer_id": "NOT_COVERED"},
    {"query": "office ka wifi password kya hai", "answer_id": "NOT_COVERED"},
    {"query": "kaunsa restaurant best hai yaha", "answer_id": "NOT_COVERED"},
]

with open("data/test_queries.json", "w", encoding="utf-8") as f:
    json.dump(queries, f, ensure_ascii=False, indent=2)

print(f"Generated {len(queries)} test queries -> data/test_queries.json")