import os
import json
import httpx
import base64
import logging
from io import BytesIO
from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager
from fastapi.responses import StreamingResponse

from ai21 import AI21Client
from ai21.models.chat import ChatMessage

from memory import long_term_memory as ltm, short_term_memory as stm

app = FastAPI()

FLASK_API_URL = "http://flask-app:8888/execution"
client = AI21Client(api_key=os.getenv('AI21_API_KEY'))

@asynccontextmanager
async def lifespan():
    logging.info("Preloading memory resources...")
    _ = ltm.get_model()
    _ = ltm.get_collection()
    logging.info("Memory resources ready.")
    yield
    logging.info("Shutting down...")

class GenerateRequest(BaseModel):
    session_id: str
    user_prompt: str

class FlaskResponse(BaseModel):
    generated_model: str
    message: str

@app.post("/generate")
async def generate_model(request: GenerateRequest):

    session_id = request.session_id
    user_prompt = request.user_prompt

    if not user_prompt:
        return {"error": "No prompt provided"}
    
    memory_context = build_memory_context(session_id, user_prompt)
    final_prompt = create_final_prompt(user_prompt, memory_context)

    try:
        ai21_response = client.chat.completions.create(
            model='jamba-large',
            messages=[
                ChatMessage(role='system', content=SYSTEM_PROMPT),
                ChatMessage(role='user', content=final_prompt)
            ]
        )
        expanded_prompt = ai21_response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"AI21 API failed: {e}")
        return {"error": "AI21 generation failed."}
    
    try:
        timeout_config = httpx.Timeout(connect=10, read=80, write=30, pool=5)
        async with httpx.AsyncClient(timeout=timeout_config) as async_client:
            flask_response = await async_client.post(
                FLASK_API_URL,
                json={
                    "attachments": [
                        "c25dcd829d134ea98f5ae4dd311d13bc.node3.openfabric.network",
                        "f0b5f319156c4819b9827000b17e511a.node3.openfabric.network"
                    ],
                    "prompt": expanded_prompt
                }
            )
        flask_json = flask_response.text.replace("'", '"')
        flask_data = FlaskResponse.model_validate(json.loads(flask_json))

    except httpx.TimeoutException as te:
        logging.error(f"Timeout when calling Flask API: {te}")
        return {"error": "The model generation process timeout. Please try again."}
    
    except httpx.RequestError as re:
        logging.error(f"HTTPX Request error calling flask API: {re}")
        return {"error": "A network occurred when contacting the model generation service."}
    
    except Exception as e:
        logging.error(f"Unexpected Flask API error: {e}")
        return {"error": "Failed to get valid response from Flask service."}
    
    stm.add_to_short_term_memory(session_id, user_prompt, expanded_prompt)
    ltm.save_to_long_term_memory(session_id, user_prompt, expanded_prompt)
        
    model_data = base64.b64decode(flask_data.generated_model)
    model_stream = BytesIO(model_data)
    model_stream.seek(0)

    return StreamingResponse(
        model_stream,
        media_type="application/octet-stream",
        headers={"Content-Disposition": "attachment; filename=model.glb"}
        )
    
@app.get("/health")
def health_check():
    return {"status": "ok"}



def build_memory_context(session_id: str, user_prompt: str) -> str:
    context = ""

    if any(phrase in user_prompt for phrase in ["like the one", "like that one", "as before", "similar to"]):
        short_term = stm.get_short_term_memory(session_id)
        if short_term:
            context += f"\nPrevious prompt: {short_term['user_prompt']}\nPrevious response: {short_term['assistant_response']}"

        long_term = ltm.get_long_term_memory(session_id, user_prompt)
        for i, mem in enumerate(long_term):
            context += f"\nPast memory {i+1} - Prompt: {mem['user_prompt']}\nResponse: {mem['assistant_response']}\n"

    return context

def create_final_prompt(user_prompt: str, memory_context: str) -> str:
    return (
        f"{memory_context}\n\nCurrent prompt: {user_prompt}\n\n"
        "Please elaborate in 150–200 words, describing visual style, color, mood, background elements, "
        "and fine details suitable for rendering an image or 3D model."
    )

SYSTEM_PROMPT = """
You are a world-class creative assistant specializing in transforming short user ideas into vivid, detailed visual scenes.
Your goal is to generate imaginative and coherent descriptions that could be used to produce high-quality AI-generated images, 
which will later be turned into 3D models.

Each scene should be:
- Rich in visual details (colors, materials, lighting, textures)
- Grounded in physics or stylized with intention (e.g., fantasy, sci-fi, cyberpunk, bio-organic)
- Focused on objects, characters, or environments that are clearly and uniquely defined
- Composed in a way that guides visual rendering systems to generate striking and structured imagery

Avoid generic phrases. Use descriptive language to stimulate image generation that results in high-fidelity, sculptable 3D shapes.
"""