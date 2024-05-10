import streamlit as st
import requests

st.title('Add Two Numbers')

x = st.number_input('Enter first number:', value=0)
y = st.number_input('Enter second number:', value=0)

if st.button('Add'):
    response = requests.post('http://localhost:8000/add/', json={'x': x, 'y': y})
    if response.status_code == 200:
        result = response.json()['result']
        st.success(f'The result is: {result}')
    else:
        st.error('Failed to get response from the API')
