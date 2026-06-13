import streamlit as st

from groq import Groq

from tavily import TavilyClient

import os

from dotenv import load_dotenv

load_dotenv()

# ── SETTINGS ──────────────────────────────────────────────────────

GROQ_API_KEY   = os.environ.get("GROQ_API_KEY")

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

BOT_NAME       = "Zara"

MODEL          = "llama-3.3-70b-versatile"

# ── ZARA'S PERSONALITY ────────────────────────────────────────────

#To do 1

SYSTEM_PROMPT = """

"You are Zara, a friendly AI buddy for young learners! 

- Fun, kind, and always encouraging

- Keep answers short and simple (2-4 sentences)

- Use emojis to keep things lively!

- When you search the web, share what you found in a fun way """
def search_web(query):


    try:


        client  = TavilyClient(api_key=TAVILY_API_KEY),

        results = client.search(

            query,

            max_results      = 5,

            search_depth     = "advanced",   # deeper, better results

            include_answer   = True,         # Tavily's own AI summary

        )

        if not results or not results.get("results"):

            return "No results found for: " + query, []

       

        sources = []

        content_for_groq = ""

        for r in results["results"]:

            title   = r.get("title",   "")

            url     = r.get("url",     "")

            content = r.get("content", "")[:300]

            sources.append({"title": title, "url": url})

            content_for_groq += f"- {title}\n  {content}\n\n"

        # Also include Tavily's own answer if available

        tavily_answer = results.get("answer", "")

        if tavily_answer:

            content_for_groq = f"Quick summary: {tavily_answer}\n\n" + content_for_groq

        return content_for_groq.strip(), sources

    except Exception as e:

        return "Search failed: " + str(e), []
       
def run_agent(question):

    

    

    client = Groq(api_key=GROQ_API_KEY)

    # ── STEP 1: Should Zara search? ───────────────────────────────

    decision = client.chat.completions.create(

        model       = MODEL,

        temperature = 0.0,

        max_tokens  = 5,

        messages    = [{

            "role": "user",

            "content": (

                f'A student asked: "{question}"\n\n'

                "Should you search the web? Be STRICT.\n\n"

                "Reply YES for:\n"

                "- News, events, scores, rankings\n"

                "- Anything with: latest, newest, current, today, 2024, 2025\n"

                "- People, places, movies, shows, games, products\n"

                "- Weather, prices, results, updates\n"

                "- ANY real-world topic that changes over time\n\n"

                "Reply NO ONLY for:\n"

                "- Pure coding/Python questions (what is a loop, write a function)\n"

                "- Simple math (2+2, what is pi)\n"

                "- Casual greetings (hi, how are you, tell a joke)\n\n"

                "When in doubt → reply YES\n\n"

                "Reply ONE word only: YES or NO"

            )

        }]

    )

    should_search = "YES" in decision.choices[0].message.content.upper()
    # ── STEP 2A: Search + Answer ───────────────────────────────────

    if should_search:

        # Ask Groq to make a good search query

        query_response = client.chat.completions.create(

            model       = MODEL,

            temperature = 0.0,

            max_tokens  = 20,

            messages    = [{

                "role": "user",

                "content": (

                    f'Convert this into a short web search query (5 words max):\n'

                    f'"{question}"\n'

                    f'Reply with ONLY the search query, nothing else.'

                )

            }]

        )

        search_query            = query_response.choices[0].message.content.strip().strip('"')

        #To do 4

        search_results, sources = search_web(search_query)

        # Ask Groq to answer using real search results

        final_response = client.chat.completions.create(

            model       = MODEL,

            temperature = 0.7,

            max_tokens  = 600,

            messages    = [

                {"role": "system", "content": SYSTEM_PROMPT},

                {"role": "user",   "content": (

                    f'A student asked: "{question}"\n\n'

                    f'I searched the web for: "{search_query}"\n'

                    f'Here are the real results:\n{search_results}\n\n'

                    f'Give a clear, helpful answer using these results.\n'

                    f'Structure your answer with:\n'

                    f'- A short fun intro (1 sentence)\n'

                    f'- 3-4 bullet points with the key facts found\n'

                    f'- A fun closing line\n'

                    f'Keep the Zara personality throughout!'

                )}

            ]

        )

        return (

            final_response.choices[0].message.content,

            True,

            search_query,

            search_results,

            sources,

        )

    # ── STEP 2B: Answer directly ───────────────────────────────────

    else:

        direct = client.chat.completions.create(

            model       = MODEL,

            temperature = 0.7,

            max_tokens  = 400,

            messages    = [

                {"role": "system", "content": SYSTEM_PROMPT}, 

                {"role": "user",   "content": question},

            ]

        )

        return direct.choices[0].message.content, False, "", "", []
st.set_page_config(page_title="Zara — AI Agent", page_icon="", layout="centered")

# ── Sidebar ───────────────────────────────────────────────────────

with st.sidebar:

    st.title(" Settings")

    st.markdown("---")

    show_thinking = st.toggle(" Show Zara's Thinking", value=True)

    st.markdown("---")

    st.markdown("**Zara's Tool:**")

    st.markdown(" **Tavily Web Search**")

    st.markdown("Built for AI agents — always works!")

    st.markdown("---")

    st.markdown("**Codeyoung Workshop** • Session 3")

    st.markdown("Powered by [Groq](https://groq.com) ")

# ── Main Page ─────────────────────────────────────────────────────

st.title(" Zara — AI Agent")

st.caption("Session 3: Agentic AI with Tavily Web Search ")

# Show warning if Tavily key is missing

if not TAVILY_API_KEY:

    st.warning(

        " **Tavily API key not found!**\n\n"

        "1. Go to [app.tavily.com](https://app.tavily.com) and sign up free\n"

        "2. Copy your API key\n"

        "3. Add to your `.env` file:\n"

        "```\nTAVILY_API_KEY=your_key_here\n```\n"

        "4. Restart the app"

    )

st.info(

    " Hi! I'm **Zara** and I just became an **AI Agent!** \n\n"

    " I can now **search the real internet** using Tavily!\n"

    " I decide on my own whether I need to search or just answer.\n\n"

    "Try: *'What is the latest news about AI?'*\n"

    "Or: *'What is a Python for loop?'* ← no search needed!"

)

# ── Chat ──────────────────────────────────────────────────────────

user_input = st.chat_input("Ask Zara anything...")

if user_input:

    with st.chat_message("user"):

        st.markdown(user_input)

    with st.chat_message("assistant"):

        with st.spinner(" Zara is thinking..."):

            try:

                reply, did_search, search_query, search_results, sources = run_agent(user_input)

                st.markdown(reply)

                if show_thinking:

                    if did_search:

                        with st.expander(" Zara searched the web — see how!"):

                            st.markdown("####  How the Agent worked:")

                            st.markdown("**Step 1** — Groq read your question")

                            st.markdown("**Step 2** — Groq decided: *'I need to search!'*")

                            st.markdown(f"**Step 3** — Searched Tavily for: `{search_query}`")

                            st.markdown("**Step 4** — Real results came back:")

                            st.code(search_results[:600], language=None)

                            st.markdown("**Step 5** — Groq wrote the friendly answer above ")

                            # Show sources

                            if sources:

                                st.markdown("####  Sources:")

                                for src in sources:

                                    title = src.get("title", "Source")

                                    url   = src.get("url",   "#")

                                    st.markdown(f"- [{title}]({url})")

                            st.caption("This is real Agentic AI — Think → Search → Answer! ")

                    else:

                        with st.expander(" No search needed — see how!"):

                            st.markdown("####  How the Agent worked:")

                            st.markdown("**Step 1** — Groq read your question")

                            st.markdown("**Step 2** — Groq decided: *'I already know this!'*")

                            st.markdown("**Step 3** — Groq answered directly ")

                            st.caption("Agents only search when they actually need to!")

                tool_label = " Searched web" if did_search else " From knowledge"

                st.caption(f"{tool_label}  •  LLaMA 3.3  •  Groq + Tavily")

            except Exception as error:

                st.error(" Error: " + str(error))

                st.info(" Check your GROQ_API_KEY and TAVILY_API_KEY in .env file!")