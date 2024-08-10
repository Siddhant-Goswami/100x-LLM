import os
import streamlit as st
from notion_client import Client

# Create Streamlit input fields for API key and page ID
st.title('Notion Page Viewer')
api_key = st.text_input('Enter your Notion API Key:', type='password')
page_id = st.text_input('Enter the Notion Page ID:')

if st.button('Retrieve Page Content'):
    if api_key and page_id:
        # Use the provided API key for authentication
        notion = Client(auth=api_key)

        # Retrieve page information
        try:
            response = notion.pages.retrieve(page_id=page_id)
            response_body = notion.blocks.children.list(block_id=page_id)

            # Display the title and some contents of the page
            page_title = response['properties']['title']['title'][0]['plain_text']
            st.header(page_title)

            # Check if there's paragraph text to display
            if response_body['results'] and 'paragraph' in response_body['results'][1]:
                paragraph_text = response_body['results'][1]['paragraph']['rich_text'][0]['plain_text']
                st.write(paragraph_text)
            else:
                st.write("No paragraph text available in this block.")
        except Exception as e:
            st.error(f"Failed to retrieve or parse page content: {str(e)}")
    else:
        st.error("Please provide both the API key and Page ID.")
