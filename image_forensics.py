import cv2
import numpy as np
import json
from skimage.util import random_noise
from skimage.metrics import structural_similarity as ssim


def analyze_edges(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    edges = np.hypot(sobelx, sobely)
    return float(np.mean(edges))


def analyze_noise(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    noise_estimate = random_noise(gray, mode='gaussian')
    noise_difference = cv2.absdiff(gray, (noise_estimate * 255).astype(np.uint8))
    return float(np.mean(noise_difference))


def detect_cloning(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    block_size = 50
    clone_scores = []

    for y in range(0, h - block_size + 1, block_size):
        for x in range(0, w - block_size + 1, block_size):
            block = gray[y:y + block_size, x:x + block_size]
            res = cv2.matchTemplate(gray, block, cv2.TM_CCOEFF_NORMED)
            if y < res.shape[0] and x < res.shape[1]:
                res[y, x] = 0
            clone_scores.append(np.max(res))

    return float(max(clone_scores)) if clone_scores else 0.0


def jpeg_artifact_analysis(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, compressed = cv2.imencode('.jpg', gray, [cv2.IMWRITE_JPEG_QUALITY, 50])
    decompressed = cv2.imdecode(compressed, cv2.IMREAD_GRAYSCALE)
    score, _ = ssim(gray, decompressed, full=True)
    return float(1 - score)


def pixel_level_check(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return {"status": "error", "message": "Image not found"}

    edge_strength = analyze_edges(image)
    noise_level = analyze_noise(image)
    clone_score = detect_cloning(image)
    artifact_score = jpeg_artifact_analysis(image)

    thresholds = {
        "clone": 0.90,
        "noise": 25.0,
        "edge": 35.0,
        "artifact": 0.10
    }

    weights = {"clone": 0.4, "noise": 0.3, "edge": 0.2, "artifact": 0.1}
    score = sum(
        max(0, (metric - thresholds[key]) * weights[key])
        for key, metric in zip(weights.keys(), [clone_score, noise_level, edge_strength, artifact_score])
    )

    if score >= 1.0:
        status = "fail"
    elif score >= 0.5:
        status = "flag for review"
    else:
        status = "success"

    result = {
        "status": status,
        "score": round(score, 2),
        "details": {
            "edge_strength": round(edge_strength, 2),
            "noise_level": round(noise_level, 2),
            "cloning_score": round(clone_score, 2),
            "artifact_score": round(artifact_score, 2)
        }
    }

    print(json.dumps(result, indent=4))
    return result


# Example usage:
# pixel_level_check(r"C:\Users\nazguul\Desktop\PFE_Workplace\Resources\ID Cards\IMG_0184_(1).jpg")
