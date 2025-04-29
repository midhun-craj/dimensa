import os
import requests
from ai21 import AI21Client
from ai21.models.chat import ChatMessage
import base64
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import logging
import json
from io import BytesIO

app = FastAPI()

FLASK_API_URL = "http://flask-app:8888/execution"
client = AI21Client(api_key=os.getenv('AI21_API_KEY'))

class GenerateRequest(BaseModel):
    user_prompt: str

class FlaskResponse(BaseModel):
    generated_model: str
    message: str

@app.post("/generate")
async def generate_model(request: GenerateRequest):

    user_prompt = request.user_prompt

    system_prompt = (
    """
You are a world-class creative assistant specializing in transforming short user ideas into vivid, \
    detailed visual scenes. Your goal is to generate imaginative and coherent descriptions that could \
        be used to produce high-quality AI-generated images, which will later be turned into 3D models.

Each scene should be:
- Rich in visual details (colors, materials, lighting, textures)
- Grounded in physics or stylized with intention (e.g., fantasy, sci-fi, cyberpunk, bio-organic)
- Focused on objects, characters, or environments that are clearly and uniquely defined
- Composed in a way that guides visual rendering systems to generate striking and structured imagery

Avoid generic phrases. Use descriptive language to stimulate image generation that results in high-fidelity, sculptable 3D shapes.

"""
)
    
    if user_prompt:
        ai21_response = client.chat.completions.create(
            model='jamba-large',
            messages=[
                ChatMessage(role='system', content=system_prompt),
                ChatMessage(
                    role='user', 
                    content=f"{user_prompt}\n\nPlease elaborate in 150–200 words, describing visual style, \
                        color, mood, background elements, and fine details suitable for rendering an image or 3D model."
                    )
            ]
        )

        expanded_prompt = ai21_response.choices[0].message.content.strip()

        flask_response = requests.post(
            FLASK_API_URL,
            json={
                "attachments": [
                    "c25dcd829d134ea98f5ae4dd311d13bc.node3.openfabric.network",
                    "f0b5f319156c4819b9827000b17e511a.node3.openfabric.network"
                ],
                "prompt": expanded_prompt
            }
        )
        logging.info(f"Raw response from flask: {flask_response.text}")

        flask_json = flask_response.text.replace("'", '"')
        try:
            flask_data = FlaskResponse.parse_obj(json.loads(flask_json))
        except json.JSONDecodeError as e:
            logging.error(f"JSON Decode Error: {e}")
            return {"error": "Failed to decode JSON response from Flask."}
        
        model_data = base64.b64decode(flask_data.generated_model)

        model_stream = BytesIO(model_data)
        model_stream.seek(0)

        return StreamingResponse(
            model_stream,
            media_type="application/octet-stream",
            headers={"Content-Disposition": "attachment; filename=model.glb"}
        )
    else:
        return {"error": "No prompt provided."}