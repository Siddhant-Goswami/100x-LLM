import os
from notion_client import Client
import streamlit as st

# 5. Authenticate and Connect to Notion (use notion integration key)
notion = Client(auth=os.environ.get("NOTION_API_KEY"))

page_id = '232b178364ed4fa4b15764dbc0d1e9dd'

response = notion.pages.retrieve(page_id=page_id)

response_body = notion.blocks.children.list(
    block_id=page_id
)

st.title(response['properties']['title']['title'][0]['plain_text'])

for block in response_body['results']:
    if block['type'] == 'paragraph':
        for text in block['paragraph']['rich_text']:
            st.write(text['plain_text'])

