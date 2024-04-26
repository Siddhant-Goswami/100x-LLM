import os
from dotenv import load_dotenv
from notion_client import Client
load_dotenv()

notion = Client(auth=os.getenv("NOTION_API_KEY"))

page_id = '67dd09be5b3b44d694996a75c07ecc26'

response = notion.pages.retrieve(page_id=page_id)

response_body = notion.blocks.children.list(
    block_id=page_id
)

print(response_body)

import streamlit as st


st.title(response['properties']['title']['title'][0]['plain_text'])

st.write(response_body['results'][1]['paragraph']['rich_text'][0]['plain_text'])





