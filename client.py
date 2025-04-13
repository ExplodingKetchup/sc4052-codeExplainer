import requests
import streamlit as st

server_address = 'http://127.0.0.1:5000'

if __name__ == '__main__':
    st.title('AI Code Explainer')

    # Input fields
    code_input = st.text_area('Enter your code:', height=200)
    additional_info_input = st.text_area('Additional information (optional):', height=100)

    # Button to generate explanation
    if st.button('Generate Explanation'):
        try:
            response = requests.post(f'{server_address}/explain-code', json={'code': code_input, 'additional_info': additional_info_input})
            response.raise_for_status()
            explanation = response.text
        except requests.exceptions.HTTPError as err:
            explanation = f'An error occurred! {err}'

        # Display the explanation
        st.subheader('Generated Explanation:')
        st.markdown(explanation)