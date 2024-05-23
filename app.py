import streamlit as st
import torch
from langchain_community.llms import CTransformers

def generate_response(input_text, num_words, device):
    # Initialize the CTransformers language model on the specified device
    llm = CTransformers(
        model="llama-2-7b-chat.ggmlv3.q8_0.bin",
        model_type="llama",
        config={"max_new_tokens": num_words, "temperature": 0.01},
        device=device  # Pass the device to use (e.g., 'cuda' for GPU)
    )
    
    # Generate response based on the input text and number of words
    response = llm.invoke(input_text, max_length=num_words)
    
    return response

st.set_page_config(
    page_title="Cherry Bot",
    page_icon="🔮",
    layout='centered',
    initial_sidebar_state="collapsed"
)

st.title("Cherry Bot")

# Check if GPU is available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
if device.type == 'cuda':
    st.write(f"Using GPU: {torch.cuda.get_device_name(0)}")
else:
    st.warning("GPU not available, running on CPU.")

# User input section
input_text = st.text_area("Enter some text to start with:")
num_words = st.number_input("Type Something....", min_value=1, value=50)

# Button to generate response
if st.button("Generate"):
    if input_text:
        # Generate response using GPU if available
        response = generate_response(input_text, num_words, device)
        # Display the generated response
        st.write(response)
    else:
        st.warning("Please enter some text to generate a response.")
