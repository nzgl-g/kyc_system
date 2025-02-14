import base64
import requests
import json
from ollama import chat, ChatResponse  # Ensure you have the ollama package installed
import shared


def encode_image(image_path):
    """Encodes an image file to a Base64 string."""
    with open(image_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")

def api_call(endpoint, prompt_text, image_path):
    """Generic function to call an AI API with a prompt and image."""
    image_data = encode_image(image_path)
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_text},
                    {"inline_data": {"mime_type": "image/jpeg", "data": image_data}}
                ]
            }
        ]
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No response received.")
    except Exception as e:
        print(f"Error calling AI API at {endpoint}: {str(e)}")
        return json.dumps({
            "status": "fail",
            "message": "API call failed",
            "detailed_result": {},
            "ps": f"Oops, something went wrong with the API at {endpoint}!"
        })

# --------------------------------------------------------------------
def gemini(form_data, image_path):
    """Processes extraction and comparison using the Gemini API."""
    prompt = shared.GLOBAL_OCR_PROMPT.format(
        form_full_name=form_data.get("full_name"),
        form_dob=form_data.get("dob"),
        form_nationality=form_data.get("nationality"),
        form_id_number=form_data.get("id_number")
    )
    return api_call(shared.GEMINI_ENDPOINT, prompt, image_path)

def ollama(form_data, image_path):
    """
    Processes extraction and comparison using the Ollama API.
    Note: The Ollama Python package currently only accepts text input.
    If image data is needed, consider encoding and appending it to the prompt.
    """
    prompt = shared.GLOBAL_OCR_PROMPT.format(
        form_full_name=form_data.get("full_name"),
        form_dob=form_data.get("dob"),
        form_nationality=form_data.get("nationality"),
        form_id_number=form_data.get("id_number")
    )
    # If you wish to include image data in text form, you could encode it and append.
    # For now, we assume the text prompt is sufficient.
    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]
    response: ChatResponse = chat(model='lminicpm-v:latest', messages=messages)
    return response.message.content


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
        return None

# --------------------------------------------------------------------
if __name__ == "__main__":
    # Static form data as JSON
    form_data = {
        "full_name": "Younes Habbal",
        "dob": "09-22-2002",
        "nationality": "Algerian",
        "id_number": "5843216619642184"
    }
    # Path to the ID card image (update with the actual path)
    image_path = r"C:\Users\nazguul\Desktop\PFE_Workplace\Resources\ID Cards\web-image1.jpg"

    # Process with Gemini
    gemini_result = gemini(form_data, image_path)
    print("Gemini Result:")
    print(gemini_result)
    print(clean_and_parse_json(gemini_result))
    # Process with Ollama
    # ollama_result = ollama_process(form_data, image_path)
    # print("\nOllama Result:")
    # print(ollama_result)
