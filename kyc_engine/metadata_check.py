from PIL import Image, ExifTags
from kyc_engine.shared import *

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
    prompt = GLOBAL_TAMPERING_PROMPT.format(metadata=metadata_json)
    # Call the Gemini API using only the text prompt
    result = api_call(GEMINI_ENDPOINT, prompt)
    return parse_json(result)



if __name__ == "__main__":
    # Update the path to your image file
    image_path = r"C:\Users\nazguul\Desktop\PFE_Workplace\Resources\ID Cards\20220327_171259 (1).jpg"
    tampering_result = detect_tampering(image_path)

    print("Tampering Detection Result:")
    print(tampering_result)