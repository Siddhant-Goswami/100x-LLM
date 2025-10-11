from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

load_dotenv(); client = OpenAI()

vs_id = "vs_684c062dbc5c8191b027bc6a2f23374b"

def ask(q):
    r = client.responses.create(
        input=q, model="gpt-4o-mini",
        tools=[{"type": "file_search", "vector_store_ids":[vs_id]}]
    )
    content = r.output[-1].content[0]
    text = content.text
    annotations = getattr(content, 'annotations', [])
    # Prepare citation markers and bibliography
    citations = []
    text_with_citations = text
    if annotations:
        # Sort by index descending so insertion doesn't mess up positions
        file_citations = [a for a in annotations if getattr(a, 'type', None) == 'file_citation']
        file_citations = sorted(file_citations, key=lambda a: a.index, reverse=True)
        for i, ann in enumerate(file_citations):
            marker = f"[{i+1}]"
            idx = ann.index
            text_with_citations = text_with_citations[:idx] + marker + text_with_citations[idx:]
            citations.append((marker, ann.filename))
    return text_with_citations, citations[::-1]  # reverse to match inline order

# Streamlit UI
st.title("File Search RAG Q&A")
question = st.text_input("Ask a question:")
if st.button("Submit"):
    if question:
        with st.spinner("Getting answer..."):
            answer, citations = ask(question)
        st.markdown(f"**Answer:** {answer}")
        if citations:
            st.markdown("\n**Citations:**")
            for marker, filename in citations:
                st.markdown(f"{marker} {filename}")
    else:
        st.warning("Please enter a question.")
