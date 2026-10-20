import streamlit as st
import requests
import base64

st.set_page_config(
    page_title="AI Intelligence Engine",
    page_icon="🤖"
)

st.title("🤖 Agentic Multi-Modal Intelligence Engine")
st.write("Your AI assistant for text and image understanding!")

api_key = st.text_input(
    "Enter your Gemini API Key",
    type="password"
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

uploaded_image = st.file_uploader(
    "Upload an image (optional)",
    type=["png", "jpg", "jpeg"]
)

prompt = st.chat_input("Ask me anything...")

if prompt:
    if not api_key:
        st.warning("Please enter your Gemini API key.")
        st.stop()

    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    parts = [{"text": prompt}]

    if uploaded_image:
        image_bytes = uploaded_image.getvalue()
        image_base64 = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        parts.append({
            "inline_data": {
                "mime_type": uploaded_image.type,
                "data": image_base64
            }
        })

    history = []

    for message in st.session_state.messages[:-1]:
        history.append({
            "role": (
                "user"
                if message["role"] == "user"
                else "model"
            ),
            "parts": [{"text": message["content"]}]
        })

    history.append({
        "role": "user",
        "parts": parts
    })

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-2.5-flash:generateContent"
    )

    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json"
    }

    payload = {"contents": history}

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=60
                )

                if response.ok:
                    data = response.json()
                    answer = data["candidates"][0][
                        "content"
                    ]["parts"][0]["text"]

                    st.markdown(answer)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })
                else:
                    st.error(
                        f"API error: {response.status_code}. "
                        "Please check your API key and try again."
                    )

            except Exception as error:
                st.error(f"Something went wrong: {error}")

if st.button("Clear Conversation"):
    st.session_state.messages = []
    st.rerun()
