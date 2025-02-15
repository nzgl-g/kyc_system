from PIL import Image, ImageChops, ImageEnhance
import os
import numpy as np
import matplotlib.pyplot as plt


def ela_analysis(image_path, quality=90, output_path="temp/temp_ela_result.jpg"):
    # Open the image and convert to RGB
    original = Image.open(image_path).convert("RGB")

    # Ensure the temp directory exists
    temp_dir = "../temp"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Save a temporary JPEG with controlled quality
    temp_path = os.path.join(temp_dir, "temp_ela_check.jpg")
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

    report = {
        "status": status,
        "message": message,
        "error_level": max_diff
    }
    return report


def generate_composite_ela_image(image_path, quality=90):
    """
    Generates a composite image using matplotlib for ELA analysis.

    The composite includes:
      - Original image
      - Recompressed image
      - ELA result image
      - A summary tile with the final ELA analysis report

    The composite image is saved in the 'temp' folder.
    """
    output_folder = "temp"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Perform ELA analysis and save the result image
    ela_result_path = os.path.join(output_folder, "temp_ela_result.jpg")
    report = ela_analysis(image_path, quality=quality, output_path=ela_result_path)

    # Load images with PIL and convert to NumPy arrays for plotting
    original = Image.open(image_path).convert("RGB")
    recompressed = Image.open(os.path.join(output_folder, "temp_ela_check.jpg")).convert("RGB")
    ela_image = Image.open(ela_result_path).convert("RGB")

    original_np = np.array(original)
    recompressed_np = np.array(recompressed)
    ela_np = np.array(ela_image)

    # Create a 2x2 composite plot using matplotlib
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))

    # Original Image
    axs[0, 0].imshow(original_np)
    axs[0, 0].set_title("Original Image")
    axs[0, 0].axis("off")

    # Recompressed Image
    axs[0, 1].imshow(recompressed_np)
    axs[0, 1].set_title("Recompressed Image")
    axs[0, 1].axis("off")

    # ELA Image
    axs[1, 0].imshow(ela_np)
    axs[1, 0].set_title("ELA Image")
    axs[1, 0].axis("off")

    # Summary Tile with analysis report
    axs[1, 1].axis("off")
    summary_text = (
        f"Status: {report['status']}\n"
        f"Error Level: {report['error_level']}\n"
        f"Message: {report['message']}"
    )
    axs[1, 1].text(0.5, 0.5, summary_text, fontsize=12, ha='center', va='center', wrap=True)
    axs[1, 1].set_title("Summary")

    plt.tight_layout()

    # Save the composite image
    composite_output = os.path.join(output_folder, "composite_ela_image.png")
    plt.savefig(composite_output)
    plt.close(fig)

    return composite_output

# Example usage:
# composite_path = generate_composite_ela_image(r"C:\Users\nazguul\Desktop\PFE_Workplace\Resources\ID Cards\new_york_fake_id-scaled-e1601065688702-1600x1029.jpg" ,quality=90)
# print(f"Composite ELA image saved at: {composite_path}")
# print(ela_analysis(r"C:\Users\nazguul\Desktop\PFE_Workplace\Resources\ID Cards\20220327_171259 (1).jpg"))
