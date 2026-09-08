import re
from datetime import datetime


# =========================================================
# WHATSAPP CHAT PARSER
# =========================================================

def parse_whatsapp_chat(file_bytes):
    """
    Parse a WhatsApp exported .txt chat into structured messages.

    Supports common formats such as:

    12/08/26, 10:30 pm - Dwarika: hello
    12/08/2026, 10:30 PM - Dwarika: hello
    [12/08/26, 10:30 PM] Dwarika: hello
    """

    text = file_bytes.decode("utf-8", errors="replace")

    lines = text.splitlines()

    messages = []

    current_message = None

    # -----------------------------------------------------
    # Common WhatsApp message patterns
    # -----------------------------------------------------

    patterns = [
        # 12/08/26, 10:30 pm - Name: Message
        re.compile(
            r"^(\d{1,2}/\d{1,2}/\d{2,4}),\s+"
            r"(\d{1,2}:\d{2}(?:\s?[APap][Mm])?)\s*-\s*"
            r"([^:]+):\s?(.*)$"
        ),

        # [12/08/26, 10:30 PM] Name: Message
        re.compile(
            r"^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s+"
            r"(\d{1,2}:\d{2}(?:\s?[APap][Mm])?)\]\s*"
            r"([^:]+):\s?(.*)$"
        ),
    ]

    # -----------------------------------------------------
    # Parse line by line
    # -----------------------------------------------------

    for line in lines:

        matched = None

        for pattern in patterns:
            matched = pattern.match(line)

            if matched:
                break

        # -------------------------------------------------
        # New message
        # -------------------------------------------------

        if matched:

            # Save previous message
            if current_message is not None:
                messages.append(current_message)

            date_str = matched.group(1)
            time_str = matched.group(2)
            sender = matched.group(3).strip()
            message_text = matched.group(4).strip()

            timestamp = parse_datetime(
                date_str,
                time_str
            )

            current_message = {
                "id": len(messages) + 1,
                "timestamp": timestamp,
                "sender": sender,
                "text": message_text
            }

        # -------------------------------------------------
        # Continuation line
        # -------------------------------------------------

        else:

            if current_message is not None:

                if line.strip():

                    current_message["text"] += "\n" + line.strip()

    # -----------------------------------------------------
    # Save last message
    # -----------------------------------------------------

    if current_message is not None:
        messages.append(current_message)

    return messages


# =========================================================
# DATE PARSER
# =========================================================

def parse_datetime(date_str, time_str):

    formats = [
        "%d/%m/%y %I:%M %p",
        "%d/%m/%Y %I:%M %p",
        "%d/%m/%y %H:%M",
        "%d/%m/%Y %H:%M",
        "%m/%d/%y %I:%M %p",
        "%m/%d/%Y %I:%M %p",
        "%m/%d/%y %H:%M",
        "%m/%d/%Y %H:%M",
    ]

    combined = f"{date_str} {time_str}"

    for fmt in formats:

        try:
            return datetime.strptime(
                combined,
                fmt
            ).isoformat()

        except ValueError:
            continue

    # If date cannot be parsed,
    # keep original information rather than crashing.
    return combined