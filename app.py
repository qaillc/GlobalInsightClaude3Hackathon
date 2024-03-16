import streamlit as st
import requests
import os
import base64
import random
import io



# Assuming anthropic is a package for interacting with AI models like Claude
# Placeholder for the actual package import and setup
from anthropic import Anthropic

def image_to_base64(image):
    """Convert the image file to base64."""
    return base64.b64encode(open(image, "rb").read()).decode("utf-8")

def get_media_type(image_name):
    """Get the media type of the uploaded image based on its file extension."""
    if image_name.lower().endswith(".jpg") or image_name.lower().endswith(".jpeg"):
        return "image/jpeg"
    elif image_name.lower().endswith(".png"):
        return "image/png"
    else:
        return None

def describe_image(image_path, api_key):
    """Send the image to Claude for description."""
    image_base64 = image_to_base64(image_path)
    media_type = get_media_type(image_path)
    client = Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_base64,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Describe this image. Provide a summary"
                    }
                ],
            }
        ],
    )
    return message.content

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

def generate_next_scene_prompt(description1, description2, api_key):
    client = Anthropic(api_key=api_key)
    combined_description = f"Based on these events: {description1} and then {description2}, imagine and describe what happens next in the story. RETURN A SUMMARIZED VERSION LESS THAN 1000 Characters"
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[{"role": "user", "content": combined_description}]
    )
    
    # Speculative: Assuming the Message object has a method or property to get content
    if hasattr(message, 'content'):
        continuation = message.content  # If .content is directly accessible
    elif hasattr(message, 'get_content'):
        continuation = message.get_content()  # If there's a method named get_content
    else:
        continuation = "Unable to generate continuation. Check the 'Message' object structure."
    
    return continuation


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

def main():
    st.title("Claude 3 Opus Generated Scenes")

    stability_api_key = st.text_input("Enter your Stability API Key:", type="password")
    claude_api_key = st.text_input("Enter your Claude API Key:", type="password")
    movie_topic = st.text_input("Enter a movie topic", value="A mysterious forest adventure")

    if st.button("Generate Scenes"):
        if not stability_api_key or not claude_api_key:
            st.error("Please enter valid API keys.")
            return

        text_prompts = generate_scene_prompts(movie_topic)
        images = generate_and_save_image(stability_api_key, text_prompts)

        cols = st.columns(2)
        with cols[0]:
            st.image(images[0], caption="Scene 1")
            description1 = describe_image(images[0], claude_api_key)
            st.write(description1)
        with cols[1]:
            st.image(images[1], caption="Scene 2")
            description2 = describe_image(images[1], claude_api_key)
            st.write(description2)



        next_scene_prompt = generate_next_scene_prompt(description1, description2, claude_api_key)
        st.write(next_scene_prompt)



    
        image_projected = generate_and_save_image(stability_api_key, str(next_scene_prompt))
        for image_path in image_projected:
            st.image(image_path, caption="Projected Image")
    
         
       

if __name__ == "__main__":
    main()