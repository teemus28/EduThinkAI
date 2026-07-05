from dotenv import load_dotenv
load_dotenv()  
from PIL import Image
import requests
from io import BytesIO
import base64
import os
from huggingface_hub import InferenceClient

client = InferenceClient(
    model="google/gemma-3-4b-it",
    token=os.environ["HF_TOKEN"],
)


def ask_gemma_text(prompt, max_tokens=512):

    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]

    response = client.chat_completion(
        messages=messages,
        max_tokens=max_tokens,
    )

    return response.choices[0].message.content





def ask_gemma_visual(image, prompt, max_new_tokens=200):
    """
    Run Gemma-3 vision-language inference.

    Args:
        image: PIL.Image, URL string, or local file path
        prompt: text question/instruction about the image
        max_new_tokens: max tokens to generate

    Returns:
        str: model's response
    """
    # Case 1: image is already a URL -> pass directly, no download needed
    if isinstance(image, str) and image.startswith("http"):
        image_url = image

    else:
        # Case 2: local file path -> load as PIL Image
        if isinstance(image, str):
            image = Image.open(image).convert("RGB")
        # Case 3: already a PIL Image
        elif isinstance(image, Image.Image):
            image = image.convert("RGB")
        else:
            raise ValueError("image must be a PIL.Image, URL string, or file path")

        # Resize image to prevent Payload Too Large error (keeping previous fix)
        max_dim = 1024
        width, height = image.size
        if max(width, height) > max_dim:
            if width > height:
                new_width = max_dim
                new_height = int(height * (max_dim / width))
            else:
                new_height = max_dim
                new_width = int(width * (max_dim / height))
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Convert PIL Image -> base64 data URI (required format for non-URL images)
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        image_url = f"data:image/png;base64,{img_b64}"

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_url}},
                {"type": "text", "text": prompt}
            ]
        }
    ]

    response = client.chat_completion(
        messages=messages,
        max_tokens=max_new_tokens,
    )

    return response.choices[0].message.content







