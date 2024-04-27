import streamlit as st
from huggingface_hub import InferenceClient
import requests
from dotenv import load_dotenv
load_dotenv()

# Define a function to check if the given URL is valid and reachable
def is_valid_url(url):
    try:
        response = requests.get(url)
        # Check if the response status code is 200 (OK)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        # Return False if the URL is not reachable or any other exception occurs
        return False

# Streamlit app
def main():
    st.title("Image Classifier")
    st.write("Enter the URL of an image to classify it using Hugging Face's Inference API.")

    # Input for image URL
    image_url = st.text_input("Image URL")

    # Display the image if the URL is valid
    if image_url:
        if is_valid_url(image_url):
            st.image(image_url, caption='Uploaded Image', use_column_width=True)
        else:
            st.error("The URL is not valid or the image is not accessible. Please check the URL.")

    # Button to classify the image
    if st.button("Classify Image"):
        if not image_url:
            st.error("Please enter a URL.")
        elif not is_valid_url(image_url):
            st.error("Please enter a valid URL of an accessible image.")
        else:
            # If the URL is valid, initialize the InferenceClient with the model ID
            # Replace "your-model-id" with the actual model ID you want to use
            client = InferenceClient()
            try:
                # Perform the classification using the client
                response = client.image_classification(image_url)
                # Extract the label from the first prediction
                label = response[0]['label']  # Adjust according to the actual output structure
                st.success(f"The image was classified as: {label}")
            except Exception as e:
                st.error(f"Failed to classify the image: {str(e)}")

# Run the Streamlit app
if __name__ == "__main__":
    main()


# from huggingface_hub import InferenceClient
# from dotenv import load_dotenv
# load_dotenv()

# client = InferenceClient()

# response = client.image_classification("https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Callie_the_golden_retriever_puppy.jpg/800px-Callie_the_golden_retriever_puppy.jpg")

# print(response[0].label)

