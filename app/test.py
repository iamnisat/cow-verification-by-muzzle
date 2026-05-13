
import os
import requests
import random
import matplotlib.pyplot as plt
from PIL import Image

API_URL = "http://localhost:8000/verify"
DATASET_PATH = r"D:/project/cow-verification-by-muzzle/datasets/cow-muzzle-dataset/test/images"
NUM_PAIRS = 5

def get_all_image(dataset_path):
    image_paths = []
    
    for file in os.listdir(dataset_path):
        image_paths.append(os.path.join(dataset_path, file))
    return image_paths[:NUM_PAIRS*2]

def call_api(image1, image2):
    with open(image1, 'rb') as img1, open(image2, 'rb') as img2:
        files = {
            'muzzleimage1': img1,
            'muzzleimage2': img2
        }
        response = requests.post(API_URL, files=files)
    return response.json()

def show_all_results(results):
    fig, axes = plt.subplots(NUM_PAIRS, 3, figsize=(12, NUM_PAIRS * 2.2))

    for i, item in enumerate(results):
        image1_path = item["image1"]
        image2_path = item["image2"]
        response = item["response"]

        img1 = Image.open(image1_path)
        img2 = Image.open(image2_path)

        data = response.get("data")

        if data:
            result_text = (
                f"Pair {i + 1}\n"
                f"Same Cow: {data.get('same_cow')}\n"
                f"Similarity: {data.get('similarity_score'):.4f}\n"
            )
        else:
            result_text = (
                f"Pair {i + 1}\n"
                f"{response.get('message', 'No response')}"
            )

        axes[i, 0].imshow(img1)
        axes[i, 0].set_title("Image 1", fontsize=9)
        axes[i, 0].axis("off")

        axes[i, 1].imshow(img2)
        axes[i, 1].set_title("Image 2", fontsize=9)
        axes[i, 1].axis("off")

        axes[i, 2].axis("off")
        axes[i, 2].text(
            0,
            0.5,
            result_text,
            fontsize=10,
            va="center",
            ha="left"
        )

    plt.tight_layout()
    plt.show()
    
def main():
    image_paths = get_all_image(DATASET_PATH)

    results = []

    for i in range(NUM_PAIRS):
        image1_path, image2_path = random.sample(image_paths, 2)

        response = call_api(image1_path, image2_path)

        results.append({
            "image1": image1_path,
            "image2": image2_path,
            "response": response,
        })

    show_all_results(results)  
if __name__ == "__main__":
    main()