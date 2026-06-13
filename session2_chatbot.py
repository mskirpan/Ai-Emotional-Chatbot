# ── STEP 1: IMPORTS ───────────────────────────────────────────────

import streamlit as st

from groq import Groq

import os

from dotenv import load_dotenv

# Load API key from .env file

load_dotenv()

# ── STEP 2: YOUR SETTINGS ─────────────────────────────────────────

API_KEY  = os.environ.get("GROQ_API_KEY")   # Loaded from .env file

BOT_NAME = "Zara"                            # Your bot's name

#  NEW! Multiple AI models to choose from

# To Do 1 

MODELS = {

    " Model 1":  "llama-3.1-8b-instant",

    "Model 2 ":  "llama-3.3-70b-versatile",

    " Model 3":  "openai/gpt-oss-120b",

    

}

# ── STEP 3:  SYSTEM PROMPT — Zara's Personality ─────────────────

# This is the BIG upgrade from Session 1!

# The AI reads this BEFORE every conversation.

# Change anything here to redesign Zara's personality!

# To Do 2

SYSTEM_PROMPT = """

You are Zara, a friendly AI coding buddy built for young learners! 

- Your name is Zara. You are enthusiastic, encouraging, and super fun!

- You LOVE coding and think Python is the coolest thing ever!

- You speak with energy and use emojis to keep things lively 

- You are patient — you NEVER make students feel bad for not knowing something




YOUR GOAL:

- Help students learn Python, AI, and coding concepts

- Make learning feel like playing a game, not studying!

- Break hard topics into tiny, easy steps

YOUR TONE:

- Friendly and enthusiastic — like a cool older sibling who codes

- Use simple words — no jargon unless you explain it!

- Short answers — 2 to 4 sentences max unless asked for more

- End responses with a question or emoji to keep the conversation going

YOUR RULES:

- Always start with a friendly greeting if this is the first message

- NEVER say coding is hard — say it's "a fun puzzle to solve!"

- If asked something off-topic, gently redirect: "Great question! But as your coding buddy, let's talk about..."

- NEVER give harmful, rude, or inappropriate content

STYLE:

- Use emojis often (but not in every single word — keep it natural)

- Use  for Python topics,  for AI topics,  for encouragement

- Celebrate every small win: "You got it!  That's huge!"
"""

# ── STEP 4: PAGE SETUP ────────────────────────────────────────────

st.set_page_config(

    page_title = f"{BOT_NAME} — AI Chatbot",

    page_icon  = "",

    layout     = "centered",

)

# ── STEP 5: SIDEBAR ───────────────────────────────────────────────

with st.sidebar:

    st.title(" Settings")

    st.markdown("---")

    #  NEW! Model selector — students pick the AI brain

    model_label = st.selectbox(

        "Choose AI Brain ",

        options = list(MODELS.keys()),

        index   = 0,

        help    = "Try different models and see how they respond!"

    )

    selected_model = MODELS[model_label]

    st.markdown("---")

    #  NEW! Temperature slider — controls creativity

    temperature = st.slider(

        "Creativity ",

        min_value = 0.0, 

        max_value = 1.5,

        value     = 0.7,

        step      = 0.1,

        help      = "0.0 = Factual & precise  |  1.5 = Wild & creative!"

    )

    # Show temperature label

    if temperature <= 0.3:

        st.caption(" Very factual mode")

    elif temperature <= 0.7:

        pass

        st.caption("Reasonable Mode")

    elif temperature <= 1.0:

        pass

        st.caption("Semi Unreasonable Mode")

    else:

        st.caption(" Wild & unpredictable mode!")

    st.markdown("---")

    st.markdown(f"**Bot:** {BOT_NAME}")

    st.markdown(f"**Model:** `{selected_model}`")

    st.markdown("---")

    st.markdown("**CodeYoung Workshop** • Session 2")

    st.markdown("Powered by [Groq](https://groq.com) + LLaMA 3 ")

# ── STEP 6: CHAT DISPLAY ──────────────────────────────────────────

st.title(f" {BOT_NAME}")

st.caption("Powered by Groq + LLaMA 3 • CodeYoung Workshop ")

# Show welcome message

st.info(

    f" Hi! I'm **{BOT_NAME}**, your AI coding buddy! "

    f"I now have a real personality — try asking me anything! \n\n"

    f" Try switching AI models in the sidebar and see how answers change!"

)

# ── STEP 7: INPUT + AI RESPONSE ───────────────────────────────────

#  UPGRADE: now sends SYSTEM PROMPT + user message

# The system prompt gives Zara her personality on every single call!

user_input = st.chat_input(f"Message {BOT_NAME}...")

if user_input:

    # Show user message

    with st.chat_message("user"):

        st.markdown(user_input)

    # Get AI response

    with st.chat_message("assistant"):

        with st.spinner("Thinking... "):

            try:

                # Connect to Groq

                client = Groq(api_key=API_KEY)

                #  NEW! Send SYSTEM PROMPT first, then user message

                # This is the key upgrade from Session 1!

                response = client.chat.completions.create(

                    model       = selected_model,

                    temperature = temperature,

                    max_tokens  = 500,

                    messages    = [

                        {

                            "role":    "system",        #  System prompt!

                            "content": SYSTEM_PROMPT
                        },

                        {

                            "role":    "user",

                            "content": user_input

                        }

                    ],

                )

                # Show the reply

                reply = response.choices[0].message.content

                st.markdown(reply)

                #  Show which model replied (fun for students to see!)

                st.caption(f" Replied by: {model_label.split('(')[0].strip()} • Temp: {temperature}")

            except Exception as error:

                st.error(f" Error: {error}")