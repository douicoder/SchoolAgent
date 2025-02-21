import streamlit as st
from chatbot_class import Chatbot

st.title("School Agent")

# Initialize chatbot
chatbot = Chatbot()

# Check for and update database on startup
if "db_update_message" not in st.session_state:
    with st.spinner("Updating database..."):
        st.session_state.db_update_message = chatbot.update_vector_db()
    st.info(st.session_state.db_update_message)

# Start chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# user input
if user_input := st.chat_input("Enter question..."):
    # add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # print user message in chat
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Fetching answer..."):
        response, query_time = chatbot.get_response(user_input)

        # print assistant response in chat
        with st.chat_message("assistant"):
            st.markdown(response)
            if query_time:
                st.write(f"⏱️ **Query Time:** {query_time:.2f} seconds")

        # add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

else:
    st.info("Enter a question to get started.")
