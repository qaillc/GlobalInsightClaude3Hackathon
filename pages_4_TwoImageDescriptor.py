import streamlit as st
import base64
from anthropic import Anthropic  # Assuming anthropic is a package for interacting with Claude

def image_to_base64(image):
    """Convert the uploaded image to base64."""
    return base64.b64encode(image.getvalue()).decode("utf-8")

def get_media_type(image_name):
    """Get the media type of the uploaded image based on its file extension."""
    if image_name.lower().endswith(".jpg") or image_name.lower().endswith(".jpeg"):
        return "image/jpeg"
    elif image_name.lower().endswith(".png"):
        return "image/png"
    else:
        return None  # Extend this function based on the image formats you expect to handle

def describe_image(image, api_key):
    """Send the image to Claude for description."""
    image_base64 = image_to_base64(image)
    media_type = get_media_type(image.name)

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
                        "text": "Describe this image."
                    }
                ],
            }
        ],
    )
    return message.content

def main():
    st.title("Image Description with Claude 3 Opus")
    
    api_key = st.text_input("Enter your Claude API Key:", type="password")

    st.header("Upload Images")
    col1, col2 = st.columns(2)
    
    with col1:
        view_image = st.file_uploader("Upload View Image", type=["jpg", "jpeg", "png"], key="view")
    with col2:
        buffer_image = st.file_uploader("Upload Buffer Image", type=["jpg", "jpeg", "png"], key="buffer")
    
    if st.button("Describe Images"):
        if not api_key:
            st.error("Please enter a valid API key.")
            return
        
        if view_image is not None:
            view_description = describe_image(view_image, api_key)
            st.text("View Image Description from Claude:")
            st.write(view_description)
        else:
            st.error("Please upload a View image.")

        if buffer_image is not None:
            buffer_description = describe_image(buffer_image, api_key)
            st.text("Buffer Image Description from Claude:")
            st.write(buffer_description)
        else:
            st.error("Please upload a Buffer image.")

if __name__ == "__main__":
    main()
