import streamlit as st
import requests
import os
import base64

# Function to make the API request and save the image
def generate_and_save_image(api_key, text_prompt):
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
    body = {
      "steps": 20,
      "width": 1024,
      "height": 1024,
      "seed": 0,
      "cfg_scale": 5,
      "samples": 1,
      "text_prompts": [
        {
          "text": text_prompt,
          "weight": 1
        },
        {
          "text": "blurry, bad",
          "weight": -1
        }
      ],
    }
    headers = {
      "Accept": "application/json",
      "Content-Type": "application/json",
      "Authorization": f"Bearer {api_key}",
    }
    response = requests.post(url, headers=headers, json=body)
    
    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))
    
    data = response.json()

    # Ensure the output directory exists
    out_dir = "./out"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    images = []
    for i, image in enumerate(data["artifacts"]):
        image_path = os.path.join(out_dir, f'txt2img_{image["seed"]}.png')
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(image["base64"]))
        images.append(image_path)
    return images

# Streamlit UI
st.title("Stability AI Image Generator")

api_key = st.text_input("Enter your Stability API Key", type="password")
text_prompt = st.text_input("Enter a text prompt", value="A painting of a cat")

if st.button("Generate Image"):
    try:
        images = generate_and_save_image(api_key, text_prompt)
        for image_path in images:
            st.image(image_path, caption="Generated Image")
    except Exception as e:
        st.error(f"Failed to generate image: {str(e)}")