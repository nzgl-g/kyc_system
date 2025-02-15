from ollama import chat, ChatResponse  # Ensure you have the ollama package installed
from kyc_engine.shared import *



def gemini(form_data, img_path):
    """Processes extraction and comparison using the Gemini API."""
    prompt = GLOBAL_OCR_PROMPT.format(
        form_full_name=form_data.get("full_name"),
        form_dob=form_data.get("dob"),
        form_nationality=form_data.get("nationality"),
        form_id_number=form_data.get("id_number")
    )
    return parse_json(api_call(GEMINI_ENDPOINT, prompt, img_path))


def ollama(form_data, image_path):
    """
    Processes extraction and comparison using the Ollama API.
    Note: The Ollama Python package currently only accepts text input.
    If image data is needed, consider encoding and appending it to the prompt.
    """
    prompt = GLOBAL_OCR_PROMPT.format(
        form_full_name=form_data.get("full_name"),
        form_dob=form_data.get("dob"),
        form_nationality=form_data.get("nationality"),
        form_id_number=form_data.get("id_number")
    )
    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]
    response: ChatResponse = chat(model='lminicpm-v:latest', messages=messages)
    return response.message.content


if __name__ == "__main__":
    # Static form data as JSON
    form_data = {
        "full_name": "Younes Habbal",
        "dob": "09-22-2002",
        "nationality": "Algerian",
        "id_number": "5843216619642184"
    }
    # Path to the ID card image (update with the actual path)
    image_path = r"C:\Users\nazguul\Pictures\Screenshots\Capture d'écran 2025-01-18 215829.png"

    # Process with Gemini
    gemini_result = gemini(form_data, image_path)
    print("Gemini Result:")
    print(gemini_result)
    # Process with Ollama
    # ollama_result = ollama(form_data, image_path)
    # print("\nOllama Result:")
    # print(ollama_result)