import streamlit as st
import requests
from groq import Groq
import re

# NASA API Key (Not required for this endpoint)
GROQ_API_KEY = "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"

# Function to extract main topic dynamically
def extract_main_topic(question):
    # Remove unnecessary words and return the main subject
    cleaned_question = re.sub(r"\b(what|who|when|where|why|how|tell me about|give me information on|show me|explain|was|is|the|of|in|about|a|an|this|can be got)\b", "", question, flags=re.IGNORECASE)
    cleaned_question = re.sub(r"[^\w\s]", "", cleaned_question).strip()  # Remove punctuation

    return cleaned_question if cleaned_question else question  # Return cleaned topic or original question

# Function to fetch NASA images only
def fetch_nasa_media(query):
    url = f"https://images-api.nasa.gov/search?q={query}&media_type=image"  # Filter for images only
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to fetch NASA data."}

# Function to interact with Groq AI
def ask_groq_ai(question):
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": question}]
    )

    if hasattr(response, "choices") and response.choices:
        return response.choices[0].message.content.strip()
    else:
        return "No response from Groq AI."

# Streamlit UI
st.title("AI-Powered Space Tutor 🚀")
st.write("Ask me anything about space!")

# User Input with Unique Key
user_question = st.text_input("Enter your space-related question:", key="space_question")

if user_question:
    st.subheader("AI Explanation:")
    
    # Get AI response
    ai_response = ask_groq_ai(user_question)
    st.write(ai_response)

    # Step 1: Extract main topic
    main_topic = extract_main_topic(user_question)

    # Step 2: Fetch and display NASA images only
    st.subheader("Related NASA Media:")
    nasa_media = fetch_nasa_media(main_topic)  # Use cleaned, simplified query

    if "collection" in nasa_media and "items" in nasa_media["collection"]:
        items = nasa_media["collection"]["items"]

        if items:
            for item in items[:3]:  # Show top 3 results
                data = item.get("data", [{}])[0]
                links = item.get("links", [{}])

                title = data.get("title", "No Title Available")
                media_type = data.get("media_type", "")

                if links and "href" in links[0]:
                    media_url = links[0]["href"]
                    
                    if media_type == "image":
                        st.image(media_url, caption=title)
                    else:
                        st.write(f"Skipping non-image media: {media_url}")
                else:
                    st.write("No media available for this item.")
        else:
            st.write("No related media found.")
    else:
        st.write("No related media found.")
