import concurrent.futures
import streamlit as st
import requests
import streamlit.components.v1 as components
import base64
from http.cookies import SimpleCookie
from uuid import uuid4
import concurrent

FASTAPI_URL = "http://fastapi-app:8082/generate"

st.set_page_config(page_title="Dimensa", layout="centered")
st.title("DIMENSA | AI-Powered 3D Imagination")

def get_or_create_session_id():
    if "session_id" not in st.session_state:
        cookie = st.query_params.get("cookie", "")
        session_id = None

        if cookie:
            parsed_cookie = SimpleCookie()
            parsed_cookie.load(cookie)
            session_cookie = parsed_cookie.get("session_id")

            if session_cookie:
                session_id = session_cookie.value

        if not session_id:
            session_id = str(uuid4())
        
        st.session_state.session_id = session_id
    return st.session_state.session_id

session_id = get_or_create_session_id()

st.markdown(
    f"""
    <script>
        document.cookie = "session_id={session_id}; SameSite=Lax; path=/";
    </script>
    """,
    unsafe_allow_html=True,
)

user_prompt = st.text_input("Enter you imagination...")

if st.button("Generate 3D model"):
    if not user_prompt:
        st.error("Please enter a prompt.")
    else:
        payload = {
            "session_id": session_id,
            "user_prompt": user_prompt
        }

        with st.spinner("Generating 3D model, please wait..."):
            try:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(requests.post, FASTAPI_URL, json=payload)
                    response = future.result(timeout=120)

                if response.status_code == 200:

                    model_data = response.content

                    st.markdown("Preview 3D model")
                    model_file = "3Dmodel.glb"
                    model_base64 = base64.b64encode(model_data).decode('utf-8')

                    components.html(
                        f"""
                        <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
                        <model-viewer src="data:application/octet-stream;base64,{model_base64}" 
                            alt="3D model" auto-rotate camera-controls 
                            style="width: 100%; height: 500px; border: 2px dotted black; border-radius: 5px; background-color: white;">
                        </model-viewer>
                        """, height=550
                                )
                    
                    st.download_button(
                        label="Download 3D model",
                        data=model_data,
                        file_name=model_file,
                        mime="application/octet-stream"
                    )
                else:
                    try:
                        error_data = response.json()
                        st.error(f"Error: {error_data.get('error', 'Unknown error')}")
                    except Exception:
                        st.error("Error creating the model (and couldn't parse error details).")
            except concurrent.futures.TimeoutError:
                st.error("Request timed out. The model generation took too long.")
            except Exception as e:
                st.error(f"Request failed: {e}")
