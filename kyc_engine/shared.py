import base64
import json
import os
import time

import requests
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL= os.getenv("GEMINI_MODEL")
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
# Global prompt for extraction and comparison
GLOBAL_OCR_PROMPT = """
You are an ADVANCED AI specialized in data extraction and verification. You are provided with an image of an ID card and a JSON form containing the following keys:
- `form_full_name`
- `form_dob`
- `form_nationality`
- `form_id_number`

Your task is to use the values in the form as anchors and search for these exact pieces of data within the ID card image. Do not perform a free extraction of all text; instead, focus solely on locating and verifying the provided form values on the card.

It is imperative that the image is of an ID card. If it is not, immediately exit the check and include the message: "no id card recognized."

Instructions:

1. **Full Name:**
   - Locate the full name on the card by matching it with the provided `form_full_name`.
   - Use fuzzy matching to tolerate minor typos and slight differences, including variations due to language differences (e.g., Arabic vs. English). Ensure that the match is sufficiently close.

2. **Date of Birth (dob):**
   - Identify the date of birth on the card and compare it with `form_dob`.
   - Account for variations in date formats (e.g., MM/DD/YYYY vs. DD/MM/YYYY) when comparing.

3. **Nationality:**
   - If the nationality appears on the card (either as text or via identifiable logos/titles), compare it with `form_nationality`.
   - Accept acceptable variations (for example, "Algerian" versus "Algeria").
   - If the nationality is not recognized, output "not found" and exclude it from the similarity scoring.
   - When the nationality is not found, do not mention this in the message field.

4. **ID Number:**
   - Search for the ID number by ignoring spaces in the recognized text, then compare it with `form_id_number`.
   - If the ID number is not found, note that it wasn’t located, but do not mark this as a failure in the OCR scan.

**Output:**

Return the result strictly in the following JSON structure (with no extra commentary):

{{
  "status": "success | fail | flag for review",
  "Similarity Score": <0-100>,
  "detailed_result": {{
    "full_name": {{
      "form_value": "{form_full_name}",
      "founded_value": "<value>",
      "match": true | false
    }},
    "dob": {{
      "form_value": "{form_dob}",
      "founded_value": "<value>",
      "match": true | false
    }},
    "nationality": {{
      "form_value": "{form_nationality}",
      "founded_value": "<value> | not found",
      "match": true | false
    }},
    "id_number": {{
      "form_value": "{form_id_number}",
      "founded_value": "<value>",
      "match": true | false
    }}
  }},
  "message": "Additional note if comparison failed"
}}

Perform the extraction and comparison using the provided form data as the basis for your search on the ID card image. Ensure that your output follows the JSON structure exactly as specified.

Have fun, and may the matching odds be ever in your favor!
"""


# --------------------------------------------------------------------
# Global prompt for metadata analyze
GLOBAL_TAMPERING_PROMPT = """
You are a digital forensics expert specializing in EXIF metadata analysis. Your task is to analyze the complete metadata extracted from an image file and detect any signs of tampering or manipulation. Please perform the following checks:

1. Authenticity Checks:
   - Software: Identify any editing tools such as Photoshop, GIMP, Snapseed, etc.
   - Compression & Resolution: Check for anomalies in compression or resolution that might indicate re-saving or modification.

2. Consistency Checks:
   - Make & Model: Ensure that the camera's make and model are present and consistent.
   - ImageUniqueID: Verify the presence of this field; its absence may indicate editing.
   - ExifVersion: Confirm that this field exists as it should in genuine images.

3. Tampering Signs:
   - GPS Data: If available, analyze the GPS information for logical consistency.
   - Unusual Metadata Gaps: Note any missing key fields that could suggest manipulation.

If any required field is missing directly fail the analysis .

Respond strictly in JSON format with no extra commentary using the following structure:

{{
  "status": "success" or "fail",
  "message": "<detailed explanation of the forensic analysis, noting any inconsistencies, tampering, or fraud indicators>"
}}
Any output deviating from this format is strictly forbidden. Process the data methodically and return only the structured decision.

Complete Metadata:
{metadata}
"""
# --------------------------------------------------------------------
GLOBAL_DECISION_PROMPT = """
You are an elite AI designed for strict data analysis and decisive judgment. Your task is to evaluate two specific fields in a dataset generated by our verification pipeline: 

  - **Status** (Primary field for decision-making)
  - **Message** (Supplementary field for explanation)

The dataset may also contain:
  - OCR Verification (Highest priority in judgment; ignore only if missing)
  - Metadata Verification (High priority in judgment)
  - Error Level Analysis (ELA) (Medium priority in judgment)
  - Image Forensics Check (Low priority in judgment)

### RULES:
1. **Your decision must be based ONLY on the `status` and `message` fields.if no message field provided rely just on statu**
2. **If OCR Verification is present, it must be given the highest weight.** If missing, rely on other available datasets.
3. **Your output must follow this exact JSON format, with no extra text, variations, or explanations:**

{{
  "decision": "<accept/deny/flag for review>",
  "reason": "<brief, data-driven explanation>"
}}
"""


def parse_json(input_str):
    start = input_str.find('{')
    end = input_str.rfind('}') + 1
    json_content = input_str[start:end]

    # Parse the cleaned string into a JSON object
    try:
        parsed_json = json.loads(json_content)
        return parsed_json
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None

def encode_image(img_path):
    """Encodes an image file to a Base64 string."""
    with open(img_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")


def api_call(endpoint, prompt_text, img_path=None, retries=3, delay=2):
    """Handles both text-only and text-with-image API calls with retry logic."""
    payload = {"contents": [{"parts": [{"text": prompt_text}]}]}

    if img_path:
        image_data = encode_image(img_path)
        if image_data:
            payload["contents"][0]["parts"].append({
                "inline_data": {"mime_type": "image/jpeg", "data": image_data}
            })

    headers = {"Content-Type": "application/json"}

    for attempt in range(retries):
        try:
            response = requests.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text",
                                                                                                "No response received.")
        except Exception as e:
            print(f"\tAttempt {attempt + 1} failed: {str(e)}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                return json.dumps({
                    "status": "fail",
                    "message": f"API call failed after multiple attempts, Endpoint {endpoint}",
                })
