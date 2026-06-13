
import streamlit as st

from groq import Groq

import os

from dotenv import load_dotenv

load_dotenv()

# STEP 2: SETTINGS

API_KEY  = os.environ.get("GROQ_API_KEY")

BOT_NAME = "Zara"

#To Do 1 - Mention the model

MODEL    = "llama-3.3-70b-versatile"

#STEP 3: ZARA'S PERSONALITY

#To do 2 - Mention the System Prompt

SYSTEM_PROMPT = """

"You are Zara, a friendly AI buddy for young learners! 

- Fun, kind, and always encouraging

- Keep answers short and simple (2-4 sentences)

- Accuracy matters most! Make sure all responses are accurate and relavent!

- When you search the web, share what you found in a fun way """

#  STEP 4: PAGE SETUP 

st.set_page_config(page_title=f"{BOT_NAME} — AI Chatbot", page_icon="", layout="centered")

# STEP 5: MEMORY SETUP

#

#   HOW MEMORY WORKS:

#  We store all messages in st.session_state["messages"]

#  Every time the student sends a message, we send the FULL list to Groq

#  Groq sees the whole conversation → smarter, connected replies!

if "messages" not in st.session_state:

    st.session_state["messages"] = []   # Empty memory on first load

if "file_text" not in st.session_state:

    st.session_state["file_text"] = ""  # No file uploaded yet

    # STEP 6: SIDEBAR 

with st.sidebar:

    st.title(" Settings")

    st.markdown("---")

    #  File Upload

    st.markdown("** Upload a .txt File**")

    st.caption("Zara will read it and answer questions about it!")

    uploaded_file = st.file_uploader("Choose a .txt file", type=["txt"])

    if uploaded_file is not None:

        st.session_state["file_text"] = uploaded_file.read().decode("utf-8")

        # To do 3 

        st.success(f" Loaded: {uploaded_file.name}")

    st.markdown("---")

    #  Memory info + Clear button

    st.markdown("** Memory**")

    msg_count = len(st.session_state["messages"])

    st.caption(f" {msg_count} message(s) saved" if msg_count > 0 else "Memory is empty")

    if st.button(" Clear Memory", use_container_width=True):

        st.session_state["messages"] = []

        st.session_state["file_text"] = ""

        st.rerun()

    st.markdown("---")

    st.markdown("**Codeyoung Workshop** • Session 4")

    st.markdown("Powered by [Groq](https://groq.com) + LLaMA 3 ")
    
    # STEP 7: MAIN PAGE 

st.title(f" {BOT_NAME}")

st.caption("Session 4: Memory + File Upload ")

st.info(

    " Hi! I'm **Zara** — and I just got a big upgrade! \n\n"

    " I now **remember our whole conversation!**\n"

    " Upload a **.txt file** and I'll answer questions about it!\n\n"

    "Try: *'My name is Alex'* → then ask *'What's my name?'*"

)

#  STEP 8: SHOW CHAT HISTORY 

# Loop through saved messages and display them on screen

for message in st.session_state["messages"]:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

#  STEP 9: HANDLE NEW MESSAGE 

user_input = st.chat_input(f"Message {BOT_NAME}...")

if user_input:

    #  Save user message to memory

    # To do 4

    st.session_state["messages"].append({"role": "user", "content": user_input})

    #  Show user message

    with st.chat_message("user"):

        st.markdown(user_input)

    #  Build system prompt — attach file content if uploaded

    system_prompt = SYSTEM_PROMPT

    if st.session_state["file_text"]:

        system_prompt += f"\n\nThe student uploaded a file. Here is its content:\n{st.session_state['file_text'][:3000]}"

    #  Get AI reply — send FULL memory to Groq!

    with st.chat_message("assistant"):

        with st.spinner(" Zara is thinking..."):

            try:

                client = Groq(api_key=API_KEY)

                response = client.chat.completions.create(

                    model      = MODEL,

                    max_tokens = 500,

                    messages   = [

                        {"role": "system", "content": system_prompt},

                        #To do 5

                        *st.session_state["messages"],  #  Full memory sent here!

                    ],

                )

                reply = response.choices[0].message.content

                st.markdown(reply)

                st.caption(f" {len(st.session_state['messages'])} message(s) in memory  •  LLaMA 3.3")

            except Exception as error:

                st.error(f" Error: {error}")

                reply = "Oops! Something went wrong."

    #  Save Zara's reply to memory too!

    st.session_state["messages"].append({"role": "assistant", "content": reply})



