# api/bfhl.py
from flask import Flask, request, jsonify
import re
import os

app = Flask(__name__)

def normalize_full_name(name: str) -> str:
    # lower, replace spaces with underscore, remove non-alnum/_ characters
    if not name:
        return "Jessica_Sarah_Koshy"
    name = name.strip().lower().replace(" ", "_")
    name = re.sub(r'[^a-z0-9_]', '', name)
    return name or "Jessica_Sarah_Koshy"

def normalize_dob(dob: str) -> str:
    # Return ddmmyyyy if possible (strip non-digits). Fallback to 17091999
    if not dob:
        return "21112004"
    digits = re.sub(r'\D', '', str(dob))
    if len(digits) == 8:
        return digits
    if len(digits) == 8:
        return digits
    return "21112004"

def extract_letters_from_string(s: str):
    return [ch for ch in s if ch.isalpha()]

def is_integer_string(s):
    return isinstance(s, int) or (isinstance(s, str) and re.fullmatch(r'\d+', s))

@app.route("/", methods=["POST"])
def bfhl_root():
    try:
        body = request.get_json(force=True)
    except Exception:
        return jsonify({"is_success": False, "error": "Invalid JSON body"}), 400

    if not isinstance(body, dict):
        return jsonify({"is_success": False, "error": "JSON object expected"}), 400

    data = body.get("data")
    if not isinstance(data, list):
        return jsonify({"is_success": False, "error": "'data' must be a list"}), 400

    # user info: prefer request-provided values, else environment variables, else defaults
    full_name = body.get("full_name") or os.environ.get("FULL_NAME") or "Jessica_Sarah_Koshy"
    dob = body.get("dob") or os.environ.get("DOB") or "21112004"
    email = body.get("email") or os.environ.get("EMAIL") or "jessicasarahkoshy@gmail.com"
    roll_number = body.get("roll_number") or os.environ.get("ROLL_NUMBER") or "22BCT0051"

    user_id = "{}_{}".format(normalize_full_name(full_name), normalize_dob(dob))

    even_numbers = []
    odd_numbers = []
    alphabets = []
    special_characters = []
    total = 0
    letter_sequence = []   # collects letters in input order for concat_string

    for item in data:
        # treat ints directly
        if isinstance(item, int):
            iv = int(item)
            total += iv
            if iv % 2 == 0:
                even_numbers.append(str(iv))
            else:
                odd_numbers.append(str(iv))
            continue

        # treat strings
        if isinstance(item, str):
            s = item
            # pure numeric string
            if re.fullmatch(r'\d+', s):
                iv = int(s)
                total += iv
                if iv % 2 == 0:
                    even_numbers.append(s)
                else:
                    odd_numbers.append(s)
                continue

            # pure alphabetic string
            if s.isalpha():
                alphabets.append(s.upper())
                # append each char (preserve char letter as-is for alternating logic later)
                for ch in s:
                    if ch.isalpha():
                        letter_sequence.append(ch)
                continue

            # mixed or special: check if contains any letter -> contribute letters to concat only
            letters = extract_letters_from_string(s)
            if letters:
                for ch in letters:
                    letter_sequence.append(ch)
                # keep the original item in special_characters (since it's not pure-alphabet)
                special_characters.append(s)
            else:
                # no letters, not pure number -> special characters
                special_characters.append(s)
            continue

        # other data types (bool, float, None, objects) -> stringify and classify letters
        s = str(item)
        letters = extract_letters_from_string(s)
        if letters:
            for ch in letters:
                letter_sequence.append(ch)
        special_characters.append(s)

    # concat_string: reverse the collected letters, then apply alternating caps starting with UPPER
    reversed_letters = list(reversed(letter_sequence))
    concat_chars = []
    for i, ch in enumerate(reversed_letters):
        if i % 2 == 0:
            concat_chars.append(ch.upper())
        else:
            concat_chars.append(ch.lower())
    concat_string = "".join(concat_chars)

    response = {
        "is_success": True,
        "user_id": user_id,
        "email": email,
        "roll_number": roll_number,
        "odd_numbers": odd_numbers,
        "even_numbers": even_numbers,
        "alphabets": alphabets,
        "special_characters": special_characters,
        "sum": str(total),
        "concat_string": concat_string
    }
    return jsonify(response), 200


# local dev entrypoint
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
