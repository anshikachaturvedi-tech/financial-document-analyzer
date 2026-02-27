import streamlit as st
import requests
import pandas as pd

UPLOAD_URL = "http://127.0.0.1:8000/upload"
QUERY_URL = "http://127.0.0.1:8000/query"
LOGS_URL = "http://127.0.0.1:8000/logs"

st.set_page_config(
    page_title="Financial Document Q&A System",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Financial Document Q&A System")
st.markdown("Upload a financial PDF and ask any question about it.")

# -------------------------
# Session State
# -------------------------
if "uploaded" not in st.session_state:
    st.session_state.uploaded = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# -------------------------
# Upload Section
# -------------------------
st.subheader("📂 Upload Financial Document")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if st.button("Upload Document"):

    if uploaded_file is None:
        st.warning("Please upload a PDF first.")
    else:
        files = {
            "file": (uploaded_file.name, uploaded_file, "application/pdf")
        }

        with st.spinner("Uploading document..."):
            response = requests.post(UPLOAD_URL, files=files)

        if response.status_code == 200:
            st.success("Document uploaded successfully!")
            st.session_state.uploaded = True
            st.session_state.chat_history = []
        else:
            st.error(response.text)


# -------------------------
# Query Section
# -------------------------
if st.session_state.uploaded:

    st.subheader("💬 Ask Questions About Uploaded PDF")

    query = st.text_input("Enter your question")

    if st.button("Ask Question"):

        if not query:
            st.warning("Please enter a question.")
        else:
            with st.spinner("Generating answer..."):

                response = requests.post(
                    QUERY_URL,
                    data={"query": query}
                )

                if response.status_code == 200:
                    answer = response.json()["answer"]

                    # Store in chat history
                    st.session_state.chat_history.append(
                        {"question": query, "answer": answer}
                    )

                else:
                    st.error(response.text)

    # -------------------------
    # Display Chat History
    # -------------------------
    if st.session_state.chat_history:
        st.subheader("📖 Current Session Conversation")

        for chat in reversed(st.session_state.chat_history):
            st.markdown(f"**🧑 Question:** {chat['question']}")
            st.markdown(f"**🤖 Answer:** {chat['answer']}")
            st.markdown("---")


# -------------------------
# Database History Section
# -------------------------
st.markdown("## 🗂️ Database History")

if st.button("🔄 Refresh Database History"):

    try:
        response = requests.get(LOGS_URL)

        if response.status_code == 200:
            logs = response.json()["logs"]

            if logs:

                df = pd.DataFrame(logs)

                # Rename columns for clean display
                df = df.rename(columns={
                    "id": "ID",
                    "file_name": "File Name",
                    "query": "Query",
                    "answer": "Answer",
                    "created_at": "Timestamp"
                })

                # Convert timestamp to readable format
                df["Timestamp"] = pd.to_datetime(df["Timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")

                # Show latest first
                df = df.sort_values(by="ID", ascending=False)

                st.dataframe(
                    df,
                    use_container_width=True,
                    height=400
                )

            else:
                st.info("No records found in database.")

        else:
            st.error("Failed to fetch logs from backend.")

    except Exception as e:
        st.error("Backend not reachable.")
        st.write(str(e))


st.markdown("---")
st.caption("Built with FastAPI + CrewAI + Groq + Streamlit")