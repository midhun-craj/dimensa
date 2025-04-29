import os
import streamlit as st
import requests
import streamlit.components.v1 as components
from io import BytesIO
import base64

FASTAPI_URL = "http://fastapi-app:8000/generate"

st.title("DIMENSA")

user_prompt = st.text_input("Enter you imagination...")

if st.button("Generate 3D model"):
    if user_prompt:
        response = requests.post(FASTAPI_URL, json={"user_prompt": user_prompt})

        if response.status_code == 200:

            model_data = response.content

            st.markdown("Preview 3D model")
            model_file = "3Dmodel.glb"
            model_base64 = base64.b64encode(model_data).decode('utf-8')

            components.html(f"""
        <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
        <model-viewer src="data:application/octet-stream;base64,{model_base64}" 
                    alt="3D model" auto-rotate camera-controls 
                    style="width: 100%; height: 500px; border: 2px dotted black; border-radius: 5px; background-color: white;">
        </model-viewer>
                        """, height=550)
            
            st.download_button(
                label="Download 3D model",
                data=model_data,
                file_name=model_file,
                mime="application/octet-stream"
            )
        else:
            st.error("Error generating the model.")
    else:
        st.error("Please enter a prompt.")
        