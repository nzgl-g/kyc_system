from PIL import Image, ImageChops, ImageEnhance


def ela_analysis(image_path, quality=90, output_path="temp/temp_ela_result.jpg"):
    # Open the image
    original = Image.open(image_path).convert("RGB")

    # Save a temporary JPEG with a controlled quality
    temp_path = "temp/temp_ela_check.jpg"
    original.save(temp_path, "JPEG", quality=quality)

    # Reopen the recompressed image
    recompressed = Image.open(temp_path)

    # Compute the absolute difference (Error Level Analysis)
    ela_image = ImageChops.difference(original, recompressed)

    # Enhance differences to make them more visible
    extrema = ela_image.getextrema()
    max_diff = max([ex[1] for ex in extrema])  # Maximum error level
    scale = 255.0 / max_diff if max_diff else 1
    ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)

    # Save the ELA result
    ela_image.save(output_path)

    # Determine the status and message based on error level
    if max_diff < 50:
        status = "success"
        message = "No significant manipulation detected."
    elif 50 <= max_diff < 150:
        status = "flag for review"
        message = "Possible minor modifications. Requires further verification."
    else:
        status = "fail"
        message = "High probability of manipulation detected!"



    # Print Final Report
    report = {
        "status": status,
        "message": message,
        "error_level": max_diff
    }
    return report


# Example usage
# image_path = r"C:\Users\nazguul\Desktop\PFE_Workplace\Resources\ID Cards\360_F_232922178_YCAxIU0vlGoGY2H76ZsATswNrOVbWlUv.jpg" # Replace with your image path
# result = ela_analysis(image_path)
