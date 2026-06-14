# STEP 1: IMPORTS 

import streamlit as st

from groq import Groq

from tavily import TavilyClient

import os

from dotenv import load_dotenv

load_dotenv()

# STEP 2: SETTINGS 

GROQ_API_KEY   = os.environ.get("GROQ_API_KEY")

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

BOT_NAME       = "Zara"

#  Multiple AI models (from Session 2!)

MODELS = {

    " LLaMA 3.3 70B  (Best)":    "llama-3.3-70b-versatile",

    " LLaMA 3.1 8B   (Fastest)":  "llama-3.1-8b-instant",

    " Gemma 2 9B     (Google)":   "gemma2-9b-it",

}

# ── STEP 1: IMPORTS ───────────────────────────────────────────────

import streamlit as st

from groq import Groq

from tavily import TavilyClient

import os

from dotenv import load_dotenv

load_dotenv()

# ── STEP 2: SETTINGS ──────────────────────────────────────────────

GROQ_API_KEY   = os.environ.get("GROQ_API_KEY")

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

BOT_NAME       = "Zara"

#  Multiple AI models (from Session 2!)

MODELS = {

    " LLaMA 3.3 70B  (Best)":    "llama-3.3-70b-versatile",

    " LLaMA 3.1 8B   (Fastest)":  "llama-3.1-8b-instant",

    " Gemma 2 9B     (Google)":   "gemma2-9b-it",

}

# ── STEP 3: ZARA'S PERSONALITY ────────────────────────────────────

BASE_SYSTEM_PROMPT = """

You are Zara, a friendly AI coding buddy for young learners! 

- Fun, kind, and always encouraging

- Keep answers short and simple (2-4 sentences)

- Use emojis to keep things lively!

- You REMEMBER the whole conversation — use it to give smarter answers!

- When you search the web, share what you found in a fun way 

"""

# ── STEP 4: PAGE SETUP ────────────────────────────────────────────

st.set_page_config(page_title=f"{BOT_NAME} — Final Bot ", page_icon="", layout="centered")

# ── STEP 5: MEMORY SETUP (from Session 4!) ────────────────────────

if "messages" not in st.session_state:

    st.session_state["messages"] = []

if "file_text" not in st.session_state:

    st.session_state["file_text"] = ""

# ── STEP 6: WEB SEARCH TOOL (from Session 3!) ─────────────────────

def search_web(query):

    """Search the internet using Tavily and return results."""

    try:

        client  = TavilyClient(api_key=TAVILY_API_KEY)

        results = client.search(query, max_results=5, include_answer=True)

        if not results or not results.get("results"):

            return "No results found.", []

        sources          = []

        content_for_groq = ""

        for r in results["results"]:

            sources.append({"title": r.get("title", ""), "url": r.get("url", "")})

            content_for_groq += f"- {r.get('title', '')}\n  {r.get('content', '')[:300]}\n\n"

        if results.get("answer"):

            content_for_groq = f"Quick summary: {results['answer']}\n\n" + content_for_groq

        return content_for_groq.strip(), sources

    except Exception as e:

        return f"Search failed: {e}", []

        # ── STEP 7: AGENT BRAIN (from Session 3!) ─────────────────────────

#

#  This is the full agent loop:

#  Step A — Ask Groq: "Should I search?" → YES or NO

#  Step B — If YES: search with Tavily → give Groq the results

#  Step C — If NO:  Groq answers from memory + conversation history

def run_agent(question, model, system_prompt):

    """The full agent loop — Think → Act → Answer."""

    client = Groq(api_key=GROQ_API_KEY)

    # ── A: Should Zara search? ─────────────────────────────────────

    decision = client.chat.completions.create(

        model       = model,

        temperature = 0.0,

        max_tokens  = 5,

        messages    = [{

            "role": "user",

            "content": (

                f'Student asked: "{question}"\n'

                "Reply YES to search for: news, events, scores, latest/current info, real-world topics.\n"

                "Reply NO for: coding questions, math, greetings, jokes.\n"

                "ONE word only: YES or NO"

            )

        }]

    )

    should_search = "YES" in decision.choices[0].message.content.upper()

    # ── B: Search + Answer ─────────────────────────────────────────

    #To Do 2

    if should_search:

        # Ask Groq to make a clean search query

        query_resp = client.chat.completions.create(

            model       = model,

            temperature = 0.0,

            max_tokens  = 20,

            messages    = [{

                "role": "user",

                "content": f'Convert to a 5-word web search query: "{question}"\nReply with ONLY the query.'

            }]

        )

        search_query            = query_resp.choices[0].message.content.strip().strip('"')

        search_results, sources = search_web(search_query)

        # Answer using real results + conversation memory

        final = client.chat.completions.create(

            model       = model,

            temperature = 0.7,

            max_tokens  = 600,

            messages    = [

                {"role": "system", "content": system_prompt},

                *st.session_state["messages"],          #  Full memory!

                {"role": "user", "content": (

                    f'Student asked: "{question}"\n'

                    f'Web search results for "{search_query}":\n{search_results}\n\n'

                    f'Answer using the search results. Keep Zara personality!'

                )}

            ]

        )

        return final.choices[0].message.content, True, search_query, search_results, sources

    # ── C: Answer directly from memory ────────────────────────────

    #To Do 3

    else:

        direct = client.chat.completions.create(

            model       = model,

            temperature = 0.7,

            max_tokens  = 500,

            messages    = [

                {"role": "system", "content": system_prompt},

                *st.session_state["messages"],          #  Full memory!

                {"role": "user", "content": question}

            ]

        )

        return direct.choices[0].message.content, False, "", "", []

# ── STEP 8: SIDEBAR ───────────────────────────────────────────────

with st.sidebar:

    st.title(" Settings")

    st.markdown("---")

    # Model selector (Session 2!)

    st.markdown("** Choose AI Brain**")

    model_label    = st.selectbox("", options=list(MODELS.keys()), index=0, label_visibility="collapsed")

    selected_model = MODELS[model_label]

    st.markdown("---")

    # File upload (Session 4!)

    st.markdown("** Upload a .txt File**")

    st.caption("Zara will read it and answer questions about it!")

    uploaded_file = st.file_uploader("Choose a .txt file", type=["txt"])

    if uploaded_file is not None:

        st.session_state["file_text"] = uploaded_file.read().decode("utf-8")

        st.success(f" Loaded: {uploaded_file.name}")

    st.markdown("---")

    # Web search toggle (Session 3!)

    st.markdown("** Web Search**")

    web_search_on  = st.toggle("Enable web search", value=True)

    show_thinking  = st.toggle("Show Zara's thinking", value=True)

    st.markdown("---")

    # Memory info + clear (Session 4!)

    st.markdown("** Memory**")

    msg_count = len(st.session_state["messages"])

    st.caption(f" {msg_count} message(s) saved" if msg_count > 0 else "Memory is empty")

    if st.button(" Clear Memory", use_container_width=True):

        st.session_state["messages"] = []

        st.session_state["file_text"] = ""

        st.rerun()

    st.markdown("---")

    st.markdown("**Codeyoung Workshop** • Session 5 ")

    st.markdown("Powered by [Groq](https://groq.com) + Tavily ")

# ── STEP 9: MAIN PAGE ─────────────────────────────────────────────

st.title(f" {BOT_NAME} — Final Bot!")

st.caption("Session 5: All Features Combined ")

st.info(

    " Hi! I'm **Zara** — the FINAL version! \n\n"

    " I have a real **personality**\n"

    " I can **search the web** for current info\n"

    " I **remember** our whole conversation\n"

    " I can **read files** you upload\n\n"

    "Try anything — I'm ready! "

)

# ── STEP 10: SHOW CHAT HISTORY ────────────────────────────────────

for message in st.session_state["messages"]:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# ── STEP 11: HANDLE NEW MESSAGE ───────────────────────────────────

user_input = st.chat_input(f"Message {BOT_NAME}...")

if user_input:

    #  Save user message to memory

    #To Do 3

    st.session_state["messages"].append({"role": "user", "content": user_input})

    #  Show user message

    with st.chat_message("user"):

        st.markdown(user_input)

    #  Build system prompt — add file content if uploaded

    system_prompt = BASE_SYSTEM_PROMPT

    if st.session_state["file_text"]:

        system_prompt += f"\n\nThe student uploaded a file. Here is its content:\n{st.session_state['file_text'][:3000]}"

    #  Run the agent (or skip search if toggled off)

    with st.chat_message("assistant"):

        with st.spinner(" Zara is thinking..."):

            try:

                if web_search_on and TAVILY_API_KEY:

                    # Full agent — memory + web search

                    #To Do 4

                    reply, did_search, search_query, search_results, sources = run_agent(

                        user_input,selected_model,system_prompt

                    )

                else:

                    # No web search — just memory + personality

                    client   = Groq(api_key=GROQ_API_KEY)

                    response = client.chat.completions.create(

                        model      = selected_model,

                        max_tokens = 500,

                        messages   = [

                            {"role": "system", "content": system_prompt},

                            *st.session_state["messages"],

                        ],

                    )

                    reply, did_search, search_query, search_results, sources = (

                        response.choices[0].message.content, False, "", "", []

                    )

                st.markdown(reply)

                #  Show thinking expander (Session 3!)

                if show_thinking:

                    if did_search:

                        with st.expander(" Zara searched the web — see how!"):

                            #To Do 5

                            st.markdown(f"**Searched for:** `{search_query}`")

                            st.code(search_results[:500], language=None)

                            if sources:

                                st.markdown("**Sources:**")

                                for src in sources:

                                    st.markdown(f"- [{src['title']}]({src['url']})")

                    elif web_search_on:

                        with st.expander(" No search needed"):

                            st.markdown("Groq decided this question didn't need a web search!")

                # Status line

                search_tag = " Searched" if did_search else " From knowledge"

                file_tag   = " File loaded" if st.session_state["file_text"] else ""

                mem_tag    = f" {len(st.session_state['messages'])} msgs"

                st.caption(f"{search_tag}  •  {mem_tag}  •  {file_tag}  •  {model_label.split('(')[0].strip()}")

            except Exception as error:

                st.error(f" Error: {error}")

                reply = "Oops! Something went wrong."

    #  Save Zara's reply to memory too!

    st.session_state["messages"].append({"role": "assistant", "content": reply})