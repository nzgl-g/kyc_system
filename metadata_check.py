import requests
import json
from PIL import Image, ExifTags
import shared

def extract_metadata(image_path):
    """
    Extracts all available EXIF metadata from an image using Pillow.
    """
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        if not exif_data:
            return {}
        metadata = {}
        for tag, value in exif_data.items():
            decoded = ExifTags.TAGS.get(tag, tag)
            metadata[decoded] = value
        return metadata
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        return {}


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


def detect_tampering(image_path):
    """
    Extracts all metadata and sends it to the AI for forensic analysis.
    """
    full_metadata = extract_metadata(image_path)

    # Convert metadata to JSON, handling non-serializable types
    metadata_json = json.dumps(
        full_metadata,
        indent=2,
        default=lambda o: float(o) if hasattr(o, 'numerator') and hasattr(o, 'denominator') else str(o)
    )
    # Build the prompt with the complete metadata injected
    prompt = shared.GLOBAL_TAMPERING_PROMPT.format(metadata=metadata_json)
    # Call the Gemini API using only the text prompt
    result = api_call(shared.GEMINI_ENDPOINT, prompt)
    return result


def clean_and_parse_json(input_str):
    # Remove code block markers and keep only content inside {}
    start = input_str.find('{')
    end = input_str.rfind('}') + 1
    json_content = input_str[start:end]

    # Parse the cleaned string into a JSON object
    try:
        parsed_json = json.loads(json_content)
        return parsed_json
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")


if __name__ == "__main__":
    # Update the path to your image file
    image_path = r"C:\Users\nazguul\Desktop\PFE_Workplace\Resources\ID Cards\20220327_171259 (1).jpg"
    tampering_result = detect_tampering(image_path)

    print("Tampering Detection Result:")
    print(clean_and_parse_json(tampering_result))