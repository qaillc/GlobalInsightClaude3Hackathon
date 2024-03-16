import streamlit as st
import requests
import os
import base64
import random

# Function to automatically generate scene text prompts from a movie topic
def generate_scene_prompts(movie_topic):
    actions = [
        "begins their journey in",
        "encounters a mysterious character in",
        "discovers a hidden secret within",
        "faces a daunting challenge in",
        "finds a crucial clue leading to the next adventure in",
        "unravels a complex puzzle in",
        "is forced to make a critical decision at",
        "unearths an ancient artifact in",
        "befriends an unlikely ally within",
        "witnesses a breathtaking phenomenon in"
    ]
    action1 = random.choice(actions)
    action2 = random.choice(list(set(actions) - {action1}))
    scene1 = f"{movie_topic} - Scene 1: Our hero {action1} the setting, marking the start of their adventure."
    scene2 = f"{movie_topic} - Scene 2: As the story progresses, the hero {action2}, moving closer to their goal."
    return [scene1, scene2]

# Function to make the API request and save the image
def generate_and_save_image(api_key, text_prompts):
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
    images = []
    
    for text_prompt in text_prompts:
        body = {
          "steps": 20,
          "width": 1024,
          "height": 1024,
          "seed": random.randint(0, 2**32),
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

        out_dir = "./out"
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        for i, image in enumerate(data["artifacts"]):
            image_path = os.path.join(out_dir, f'txt2img_{text_prompt[:10]}_{image["seed"]}.png')
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(image["base64"]))
            images.append(image_path)
            
    return images

# Streamlit UI
st.title("Stability AI Movie Scene Generator")

api_key = st.text_input("Enter your Stability API Key", type="password")
movie_topic = st.text_input("Enter a movie topic", value="A mysterious forest adventure")

if st.button("Generate Images"):
    text_prompts = generate_scene_prompts(movie_topic)
    
    try:
        images = generate_and_save_image(api_key, text_prompts)
        if images:
            cols = st.columns(2)
            with cols[0]:
                st.image(images[0], caption="View (Scene 1)")
            with cols[1]:
                st.image(images[1], caption="Buffer (Scene 2)")
    except Exception as e:
        st.error(f"Failed to generate images: {str(e)}")