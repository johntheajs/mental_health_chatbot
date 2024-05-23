import streamlit as st
import ollama
import pickle
import os

CHAT_HISTORY_FILE = "chat_history.pkl"

# Function to send request to OLLAMA model
def send_ollama_request(model, messages):
    response = ollama.chat(model=model, messages=messages)
    return response

# Function to save chat history to a file
def save_chat_history():
    with open(CHAT_HISTORY_FILE, 'wb') as file:
        pickle.dump(st.session_state.all_chats, file)

# Function to load chat history from a file
def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, 'rb') as file:
            return pickle.load(file)
    return []

def main():
    st.set_page_config(
        page_title="Cherry Bot",
        page_icon="🔮",
        layout='wide'
    )

    st.markdown(
        """
        <style>
        .chat-history {
            padding: 10px;
            margin-bottom: 20px;
            border-radius: 5px;
            border: 1px solid #ddd;
            max-height: 400px;
            overflow-y: auto;
        }
        .message-user {
            color: blue;
            margin-bottom: 10px;
        }
        .message-bot {
            color: green;
            margin-bottom: 10px;
        }
        .user-input {
            margin-top: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("Cherry Bot")

    # Load chat history from the file
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'all_chats' not in st.session_state:
        st.session_state.all_chats = load_chat_history()

    # Sidebar for creating a new chat and viewing old chats
    with st.sidebar:
        st.header("Options")
        if st.button("Start New Chat"):
            if st.session_state.chat_history:
                st.session_state.all_chats.append(st.session_state.chat_history)
                save_chat_history()
            st.session_state.chat_history = []

        if st.session_state.all_chats:
            st.subheader("Previous Chats")
            for i, chat in enumerate(st.session_state.all_chats):
                chat_button_label = f"Chat {i + 1}"
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(chat_button_label, key=f"view_{i}"):
                        st.session_state.chat_history = chat
                with col2:
                    if st.button("❌", key=f"delete_{i}"):
                        st.session_state.all_chats.pop(i)
                        save_chat_history()
                        st.experimental_rerun()

    # Display the conversation history
    chat_history_container = st.container()
    with chat_history_container:
        if st.session_state.chat_history:
            st.write("### Chat History")
            chat_history_str = ""
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    chat_history_str += f"<div class='message-user'><b>User:</b> {message['content']}</div>"
                else:
                    chat_history_str += f"<div class='message-bot'><b>Cherry Bot:</b> {message['content']}</div>"
            st.markdown(f"<div class='chat-history'>{chat_history_str}</div>", unsafe_allow_html=True)

    # User input form at the bottom
    with st.form(key='user_input_form', clear_on_submit=True):
        input_text = st.text_area("Enter a message to chat with Cherry Bot:", key="input_text", height=100)
        submit_button = st.form_submit_button(label='Send')

    # Button to generate response
    if submit_button:
        if input_text.strip() == "":
            st.warning("Please enter some text to chat.")
        else:
            # Prepare message for the OLLAMA model
            user_message = {
                'role': 'user',
                'content': input_text,
            }
            st.session_state.chat_history.append(user_message)

            # Update the conversation history immediately
            with chat_history_container:
                st.write("### Chat History")
                chat_history_str = ""
                for message in st.session_state.chat_history:
                    if message['role'] == 'user':
                        chat_history_str += f"<div class='message-user'><b>User:</b> {message['content']}</div>"
                    else:
                        chat_history_str += f"<div class='message-bot'><b>Cherry Bot:</b> {message['content']}</div>"
                st.markdown(f"<div class='chat-history'>{chat_history_str}</div>", unsafe_allow_html=True)

            model = 'llama3'

            # Get response from OLLAMA
            response = send_ollama_request(model, st.session_state.chat_history)
            bot_message = {
                'role': 'assistant',
                'content': response['message']['content']
            }
            st.session_state.chat_history.append(bot_message)

            # Update the conversation history again after receiving the response
            with chat_history_container:
                st.write("### Chat History")
                chat_history_str = ""
                for message in st.session_state.chat_history:
                    if message['role'] == 'user':
                        chat_history_str += f"<div class='message-user'><b>User:</b> {message['content']}</div>"
                    else:
                        chat_history_str += f"<div class='message-bot'><b>Cherry Bot:</b> {message['content']}</div>"
                st.markdown(f"<div class='chat-history'>{chat_history_str}</div>", unsafe_allow_html=True)

            # Save the updated chat history
            save_chat_history()

if __name__ == "__main__":
    main()
