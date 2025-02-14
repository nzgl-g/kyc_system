from deepface import DeepFace

result = DeepFace.verify(r"C:\Users\nazguul\Desktop\PFE_Workplace\Resources\ID Cards\2023_10_12_11_43_IMG_6550.JPG", r"C:\Users\nazguul\Desktop\PFE_Workplace\Resources\ID Cards\20220327_171259 (1).jpg")
print(result)  # {'verified': True/False, 'distance': value, etc.}
