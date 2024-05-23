import streamlit as st
import ollama
import sqlite3
import json

CHAT_HISTORY_DB = 'chat_history.db'

# Database setup
def create_connection():
    return sqlite3.connect(CHAT_HISTORY_DB)

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_data TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_chat(chat_id, chat_data):
    conn = create_connection()
    cursor = conn.cursor()
    if chat_id is None:
        cursor.execute('INSERT INTO chat_history (chat_data) VALUES (?)', (json.dumps(chat_data),))
        chat_id = cursor.lastrowid
    else:
        cursor.execute('UPDATE chat_history SET chat_data = ? WHERE id = ?', (json.dumps(chat_data), chat_id))
    conn.commit()
    conn.close()
    return chat_id

def load_chats():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM chat_history')
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_chat(chat_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM chat_history WHERE id = ?', (chat_id,))
    conn.commit()
    conn.close()

def send_ollama_request(model, messages):
    response = ollama.chat(model=model, messages=messages)
    return response

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

    # Load chat history from the database
    if 'chat_id' not in st.session_state:
        st.session_state.chat_id = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'all_chats' not in st.session_state:
        st.session_state.all_chats = load_chats()

    # Sidebar for creating a new chat and viewing old chats
    with st.sidebar:
        st.header("Options")
        if st.button("Start New Chat"):
            if st.session_state.chat_history:
                st.session_state.chat_id = save_chat(st.session_state.chat_id, st.session_state.chat_history)
            st.session_state.chat_history = []
            st.session_state.chat_id = None
            st.session_state.all_chats = load_chats()
            st.experimental_rerun()

        if st.session_state.all_chats:
            st.subheader("Previous Chats")
            for chat in st.session_state.all_chats:
                chat_id, chat_data = chat
                chat_button_label = f"Chat {chat_id}"
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(chat_button_label, key=f"view_{chat_id}"):
                        st.session_state.chat_id = chat_id
                        st.session_state.chat_history = json.loads(chat_data)
                        st.experimental_rerun()
                with col2:
                    if st.button("❌", key=f"delete_{chat_id}"):
                        delete_chat(chat_id)
                        st.session_state.all_chats = load_chats()
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
            st.session_state.chat_id = save_chat(st.session_state.chat_id, st.session_state.chat_history)
            st.session_state.all_chats = load_chats()

if __name__ == "__main__":
    create_table()
    main()
