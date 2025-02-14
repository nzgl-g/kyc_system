import requests

import ocr_check
import ela_check
import metadata_check
import image_forensics
import json
import shared
def run_pipeline(form_data, image_path):
    """
    Runs the KYC verification pipeline in the following order:
      1. OCR Extraction using Gemini
      2. Metadata Extraction & Tampering Detection
      3. Error Level Analysis (ELA)
      4. Pixel-level Forensic Analysis

    Returns:
      A dictionary with all outputs organized by step.
    """
    results = {}

    # Step 1: OCR Extraction using Gemini
    try:
        print("DEBUG: Step 1 - Starting OCR Extraction using Gemini...")
        ocr_output = ocr_check.gemini(form_data, image_path)
        parsed_ocr = ocr_check.clean_and_parse_json(ocr_output)
        results["OCR"] = parsed_ocr if parsed_ocr else {"raw_output": ocr_output}
        print("DEBUG: Step 1 complete. OCR result obtained.")
    except Exception as e:
        print(f"DEBUG: Step 1 failed: {e}")
        results["OCR"] = {"error": str(e)}

    # Step 2: Metadata Extraction & Tampering Detection
    try:
        print("DEBUG: Step 2 - Starting Metadata Extraction and Tampering Detection...")
        metadata_output = metadata_check.detect_tampering(image_path)
        parsed_metadata = metadata_check.clean_and_parse_json(metadata_output)
        results["Metadata"] = parsed_metadata if parsed_metadata else {"raw_output": metadata_output}
        print("DEBUG: Step 2 complete. Metadata result obtained.")
    except Exception as e:
        print(f"DEBUG: Step 2 failed: {e}")
        results["Metadata"] = {"error": str(e)}

    # Step 3: Error Level Analysis (ELA)
    try:
        print("DEBUG: Step 3 - Starting Error Level Analysis (ELA)...")
        ela_output = ela_check.ela_analysis(image_path)
        results["ELA"] = ela_output
        print("DEBUG: Step 3 complete. ELA result obtained.")
    except Exception as e:
        print(f"DEBUG: Step 3 failed: {e}")
        results["ELA"] = {"error": str(e)}

    # Step 4: Pixel-level Forensic Analysis
    try:
        print("DEBUG: Step 4 - Starting Pixel-level Forensic Analysis...")
        forensics_output = image_forensics.pixel_level_check(image_path)
        results["Forensics"] = forensics_output
        print("DEBUG: Step 4 complete. Forensics result obtained.")
    except Exception as e:
        print(f"DEBUG: Step 4 failed: {e}")
        results["Forensics"] = {"error": str(e)}

    aggregated_results = json.dumps(results, indent=4)
    print("DEBUG: Pipeline execution complete. Aggregated results:")
    print(aggregated_results)

    return results

def api_call(endpoint, prompt_text):
    """
    Calls the Gemini API with the provided text prompt.
    """
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_text}
                ]
            }
        ]
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        response_text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text",
                                                                                                     "No response received.")
        return response_text
    except Exception as e:
        print(f"Error calling AI API at {endpoint}: {str(e)}")
        return json.dumps({
            "status": "fail",
            "message": "API call failed"
        })


def kyc_decision (pipline_result):
    prompt = shared.GLOBAL_DECISION_PROMPT + json.dumps(pipline_result)

    decision_result = api_call(shared.GEMINI_ENDPOINT, prompt)
    return decision_result


if __name__ == "__main__":
    form_data = {
        "full_name": "steven hinn",
        "dob": "07-07-98",
        "nationality": "Algerian",
        "id_number": "100020029048620002"
    }
    image_path = r"C:\Users\nazguul\Desktop\PFE_Workplace\Resources\ID Cards\new_york_fake_id-scaled-e1601065688702-1600x1029.jpg"

    final_results = run_pipeline(form_data, image_path)
    print(kyc_decision(final_results))
