from auth0_component import login_button
import streamlit as st

clientId = "j2r7dzEYqNXg8EHizc5zUO28h72nAUrD"
domain = "dev-gy6cyikcqvogc1xp.us.auth0.com"

redirectUri = "http://localhost:8501/component/auth0_component.login_button/index.html"

user_info = login_button(clientId, domain=domain, redirectUri=redirectUri)

st.write(user_info)