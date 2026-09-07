import json
import random
from datetime import datetime, timedelta

random.seed(42)  # SEED for reproducibility

names = ["Dwarika", "Sugna", "Priyanshi", "Drishti", "Apurva", "Palak", "Argha"]

# Wide variety of casual/messy real-life chat phrases
casual_msgs = [
    "haan bhai", "kab?", "ok", "okk", "theek hai", "kya baat hai", "lol", "haha sahi hai",
    "kal milte hai", "chalo fir", "sahi h", "bata na", "kaha ho tum log", "😂😂😂",
    "true", "yaar seriously", "kuch bhi", "acha thik h", "mai busy hu abhi",
    "call kru?", "wait kr rha hu", "aya nahi abhi tak", "haa", "nahi yr",
    "kya scene hai aaj", "class hai kya kal", "assignment submit kiya?",
    "abhi uthi hu 😭", "so rahi thi sorry", "kal dekhte hai", "pakka na",
    "hostel aa jao", "mess me milte h", "kitna time lagega", "aa rha hu 5 min",
    "traffic h bohot", "network issue tha yaar", "message dikha nhi tha sorry",
    "haan ekdum", "nope busy hu", "kya hua phir", "sunn na ek baat",
    "👍", "👍👍", "🙏", "😭😭", "hahahaha stop", "bhai ye kya tha",
    "seen but forgot reply sry", "ek sec", "call pe baat krte h",
    "wo mail check kiya?", "faculty ne bola kal aana",
    "assignment ka pta h kuch?", "meeting reschedule hui hai",
    "kisne notes banaye the", "share kr do please",
    "attendance kam h meri 😭", "exam form bhara?",
    "fees ki last date kab h", "pta nhi yr, google kr le",
    "kal off hai kya college", "haan holiday hai",
    "*Forwarded*\nHostel mess timing changed w.e.f Monday. New timings: 8-9:30 AM, 1-2:30 PM, 7:30-9 PM.",
    "*Forwarded*\nReminder: Fee submission deadline is this Friday, late fee applicable after.",
    "kisi ne dekha announcement group me?", "haan dekha abhi",
    "kal ka plan kya h", "movie chalein?", "budget kam h yr is week",
]

# Threads that "decide" something concrete — written a bit messier, spread over multiple turns
manali_thread = [
    ("Dwarika", "guys trip plan krni h ek baar, itna time ho gya"),
    ("Priyanshi", "haan yr bolo kaha jaana h"),
    ("Argha", "kuch thanda jagah dekhte h, garmi bhot h yaha"),
    ("Sugna", "manali try karte kya is baar"),
    ("Drishti", "manali sunne me acha lg rha, weather bhi thik rahega"),
    ("Palak", "budget kitna aayega roughly"),
    ("Apurva", "logo pe depend krega, per head 6-7k tak"),
    ("Dwarika", "ok fir chalo manali hi fix krte h, isse jyada discuss krne ki jarurat nhi"),
    ("Sugna", "mai bhi confirm, aa rhi hu"),
    ("Priyanshi", "dates kab ki rakhe"),
    ("Dwarika", "dec ke last week me chalte h sabko exam bhi khatam ho jayenge"),
]

budget_thread = [
    ("Palak", "farewell party ka budget decide krna h aaj"),
    ("Argha", "2000 per head lagta h km rahega itne me"),
    ("Priyanshi", "2500 rakh lo, safe side pe"),
    ("Drishti", "venue bhi to dekhna h abhi tk kuch fix nhi"),
    ("Apurva", "haan venue ka bhi budget isi me aa jana chahiye"),
    ("Palak", "chalo fir mai 2500 hi final kr deti hu sabse"),
    ("Sugna", "ok done"),
]

deadline_thread = [
    ("Drishti", "project ki deadline extend hui kya kisi ko pta h"),
    ("Apurva", "haan maam ne bola 20 tarikh tk kr skte h ab"),
    ("Dwarika", "confirm h ye? kahi aisa na ho fir change kr de"),
    ("Apurva", "haan mail bhi aaya tha group me check kr"),
    ("Argha", "thank god yr, thoda relax mila"),
    ("Priyanshi", "chalo ab thodi neend le skte h 😭"),
]

def random_text():
    return random.choice(casual_msgs)

def generate_corpus(num_messages=4200):
    messages = []
    start_date = datetime(2026, 1, 3, 9, 15)
    current_date = start_date
    msg_id = 1

    thread_positions = sorted(random.sample(range(200, num_messages - 200), 3))
    threads = [manali_thread, budget_thread, deadline_thread]
    thread_idx = 0
    i = 0

    while i < num_messages:
        gap_minutes = random.choice([1, 1, 2, 2, 3, 5, 8, 15, 30, 60, 90, 180, 60*6, 60*20])
        current_date += timedelta(minutes=gap_minutes)

        if thread_idx < len(thread_positions) and i >= thread_positions[thread_idx]:
            thread = threads[thread_idx]
            for sender, text in thread:
                messages.append({
                    "id": msg_id,
                    "timestamp": current_date.isoformat(),
                    "sender": sender,
                    "text": text
                })
                msg_id += 1
                i += 1
                current_date += timedelta(minutes=random.choice([1, 2, 3, 4]))
            thread_idx += 1
            continue

        sender = random.choice(names)
        text = random_text()
        messages.append({
            "id": msg_id,
            "timestamp": current_date.isoformat(),
            "sender": sender,
            "text": text
        })
        msg_id += 1
        i += 1

    return messages

if __name__ == "__main__":
    corpus = generate_corpus()
    with open("data/chat.jsonl", "w", encoding="utf-8") as f:
        for msg in corpus:
            f.write(json.dumps(msg, ensure_ascii=False) + "\n")
    print(f"Generated {len(corpus)} messages -> data/chat.jsonl")