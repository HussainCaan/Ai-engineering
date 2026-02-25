import streamlit as st
import requests

# Backend URL
FASTAPI_URL = "http://localhost:8000/llm"

st.set_page_config(
    page_title="Research Paper Assistant",
    page_icon="📚",
    layout="centered"
)

st.title("📚 Research Paper Assistant")
st.markdown(
    """
    This assistant explains academic research papers in depth.
    It uses:
    - Wikipedia
    - Arxiv
    
    Enter a research paper title below.
    """
)

# Input box
query = st.text_input(
    "Enter Research Paper Title:",
    placeholder="Attention Is All You Need"
)


if st.button("Analyze Paper"):

    if not query.strip():
        st.warning("Please enter a paper title.")
    else:
        with st.spinner("🔍 Searching tools and analyzing paper..."):

            try:
                response = requests.post(
                    FASTAPI_URL,
                    json={"query": query},
                    timeout=120
                )

                if response.status_code == 200:
                    result = response.json()
                    st.success("Analysis Complete ✅")
                    st.markdown("### 📄 Explanation")
                    st.write(result["response"])

                else:
                    st.error(f"Backend Error: {response.status_code}")
                    st.write(response.text)

            except requests.exceptions.ConnectionError:
                st.error("❌ Could not connect to FastAPI backend.")
                st.info("Make sure your FastAPI server is running on port 8000.")
            
            except requests.exceptions.Timeout:
                st.error("⏳ Request timed out. Try again.")
            
            except Exception as e:
                st.error(f"Unexpected error: {e}")
                

