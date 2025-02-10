import streamlit as st
import json
from prompt_chaining import generate_marketing_content

def main():
    st.set_page_config(
        page_title="Marketing Copy Generator",
        page_icon="✍️",
        layout="wide"
    )
    
    st.title("✍️ Marketing Copy Generator")
    st.write("""
    Generate, review, and translate marketing copy using AI. 
    The system will automatically validate the content and provide feedback.
    """)
    
    # Create two columns for input
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Product Information")
        product = st.text_input("Product Name", placeholder="e.g., Smart Fitness Watch")
        target_audience = st.text_input("Target Audience", placeholder="e.g., Health-conscious young professionals")
        
        st.subheader("Requirements")
        requirements = st.text_area(
            "Enter requirements (one per line)",
            placeholder="""- Emphasize key features
- Include specific benefits
- Focus on target audience needs
- Keep it under 100 words""",
            height=150
        )
        
        target_language = st.selectbox(
            "Translation Language",
            ["Spanish", "French", "German", "Italian", "Portuguese", "Chinese", "Japanese"]
        )
        
        max_attempts = st.slider(
            "Maximum Generation Attempts",
            min_value=1,
            max_value=5,
            value=3,
            help="Maximum number of attempts to generate acceptable copy"
        )
    
    with col2:
        st.subheader("Process Status")
        if 'generation_state' not in st.session_state:
            st.session_state.generation_state = None
            
        generate_button = st.button("Generate Marketing Copy", type="primary")
        
        if generate_button:
            if not product or not target_audience or not requirements:
                st.error("Please fill in all required fields!")
            else:
                with st.spinner("Generating marketing copy..."):
                    result = generate_marketing_content(
                        product=product,
                        target_audience=target_audience,
                        requirements=requirements,
                        target_language=target_language,
                        max_attempts=max_attempts
                    )
                    st.session_state.generation_state = result
        
        if st.session_state.generation_state:
            result = st.session_state.generation_state
            
            # Status indicator
            if result["status"] == "success":
                st.success(f"✅ Success (Attempts: {result['attempts']})")
            else:
                st.error(f"❌ Failed after {result['attempts']} attempts")
            
            # Original Copy
            st.subheader("Original Copy")
            st.text_area("", value=result["original_copy"], height=100, disabled=True)
            
            # Feedback
            st.subheader("Feedback")
            st.info(result["feedback"])
            
            if result["status"] == "success":
                # Final Copy
                st.subheader("Final Approved Copy")
                st.text_area("", value=result["final_copy"], height=100, disabled=True)
                
                # Translated Copy
                st.subheader(f"Translated Copy ({target_language})")
                st.text_area("", value=result["translated_copy"], height=100, disabled=True)
                
                # Download buttons
                st.subheader("Export Results")
                
                # Create JSON with all results
                export_data = {
                    "product": product,
                    "target_audience": target_audience,
                    "requirements": requirements.split("\n"),
                    "target_language": target_language,
                    "results": result
                }
                
                # JSON download
                st.download_button(
                    label="Download JSON",
                    data=json.dumps(export_data, indent=2),
                    file_name="marketing_copy_results.json",
                    mime="application/json"
                )
                
                # Text download
                text_content = f"""Marketing Copy Generation Results

Product: {product}
Target Audience: {target_audience}

Requirements:
{requirements}

Original Copy:
{result['original_copy']}

Feedback:
{result['feedback']}

Final Approved Copy:
{result['final_copy']}

{target_language} Translation:
{result['translated_copy']}
"""
                st.download_button(
                    label="Download Text",
                    data=text_content,
                    file_name="marketing_copy_results.txt",
                    mime="text/plain"
                )

if __name__ == "__main__":
    main() 