import logging
from typing import Dict
import os
from uuid import uuid4
import http.server
import socketserver
from threading import Thread
import base64
import sqlite3

from ontology_dc8f06af066e4a7880a5938933236037.config import ConfigClass
from ontology_dc8f06af066e4a7880a5938933236037.input import InputClass
from ontology_dc8f06af066e4a7880a5938933236037.output import OutputClass
from openfabric_pysdk.context import AppModel, State
from core.stub import Stub

from transformers import AutoTokenizer, AutoModelForCausalLM

# Configurations for the app
configurations: Dict[str, ConfigClass] = dict()

# IMAGE_DIR = 'saved images'
MODEL_DIR = '/savedmodels'

if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)


############################################################
                    # Session Memory
############################################################
class SessionMemory:
    def __init__(self):
        self.memory = []

    def add_to_memory(self, message):
        self.memory.append(message)

    def get_memory(self):
        return " ".join(self.memory)
    

############################################################
                    # Long-Term Memory
############################################################
class LongTermMemory:
    def __init__(self, db_name="memory.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY, content TEXT)")
    
    def add_memory(self, content):
        self.cursor.execute("INSERT INTO memories (content) VALUES (?)", (content,))
        self.conn.commit()

    def recall_memory(self, description):
        self.cursor.execute("SELECT content FROM memories WHERE content LIKE ?", ('%' + description + '%',))
        return self.cursor.fetchall()
    

session_memory = SessionMemory()
long_term_memory = LongTermMemory()


############################################################
                # Config callback function
############################################################
def config(configuration: Dict[str, ConfigClass], state: State) -> None:
    """
    Stores user-specific configuration data.

    Args:
        configuration (Dict[str, ConfigClass]): A mapping of user IDs to configuration objects.
        state (State): The current state of the application (not used in this implementation).
    """
    for uid, conf in configuration.items():
        logging.info(f"Saving new config for user with id:'{uid}'")
        configurations[uid] = conf


############################################################
                # Execution callback function
############################################################
def execute(model: AppModel) -> None:
    """
    Main execution entry point for handling a model pass.

    Args:
        model (AppModel): The model object containing request and response structures.
    """

    # Retrieve input
    request: InputClass = model.request
    user_prompt = request.prompt
    logging.info(f"User prompt: {user_prompt}" )

    # Retrieve user config
    user_config: ConfigClass = configurations.get('super-user', None)
    logging.info(f"{configurations}")

    # Initialize the Stub with app IDs
    app_ids = user_config.app_ids if user_config else []
    stub = Stub(app_ids)
    logging.info(f"Stub: {stub}")

############################################################
                        #  PIPELINE 
############################################################

    ############################################################
                        #  GPT2-medium 
    ############################################################
    logging.info("Model downloading...")
    model_name = "gpt2-medium"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    llm_model = AutoModelForCausalLM.from_pretrained(model_name)
    logging.info("Model downloaded...")

    def expand_prompt_with_gpt4(user_prompt: str) -> str:

        description_for_llm = """
You are a creative assistant tasked with transforming short scene ideas into richly detailed, \
    visually immersive descriptions that are perfect for image generation. Focus on capturing:
"""
        
        final_prompt = description_for_llm.strip() + f'\nIdea: "{user_prompt}"Scene:'

        inputs = tokenizer(final_prompt, return_tensors="pt")
        input_length = inputs.input_ids.shape[1]

        outputs = llm_model.generate(
            inputs['input_ids'], 
            max_new_tokens=150, 
            num_return_sequences=1,
            temperature=0.85,
            top_p=0.95,
            no_repeat_ngram_size=3,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )

        generated_tokens = outputs[0][input_length:]

        expanded_prompt = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

        return expanded_prompt
    

    # STEP - 1 LLM Call
    logging.info(f"User prompt: {user_prompt}")
    logging.info("Expanding the prompt...")

    expanded_prompt = expand_prompt_with_gpt4(user_prompt)
    logging.info(f"Expanded prompt: {expanded_prompt}")

    session_memory.add_to_memory(expanded_prompt)

    if "like the one i created last" in user_prompt:
        memory_recall = long_term_memory.recall_memory(user_prompt)

        if memory_recall:
            logging.info(f"Recalling from long-term memory: {memory_recall}")
        else:
            logging.info("No relevant long-term memory found.")
            long_term_memory.add_memory(user_prompt)   


    # STEP - 2 Prompt to image app
    object1 = stub.call(request.attachments[0], {'prompt': expanded_prompt}, 'super-user')
    if object1 is None:
        logging.error("Error: object1 is empty, cannot process further")
        return
    # logging.info(f"object1: {object1}")
    
    generated_blob_image = object1.get('result', None)
    if generated_blob_image is None:
        logging.error("Error: no image found in object1")
        return
    logging.info("image generated")
    
    base64_encoded_image = base64.b64encode(generated_blob_image).decode('utf-8')
    logging.info("image is base64 encoded to a string")


    # STEP - 3 Image to 3D model app
    object2 = stub.call(request.attachments[1], {'input_image': base64_encoded_image}, 'super-user')
    
    if object2 is None:
        logging.error("Error: object2 is empty, cannot process further")
        return
    # logging.error(f"object2: {object2}")

    model_image = object2.get('generated_object', None)
    if model_image is None:
        logging.error("Error: no model found in object2")
        return
    logging.info("3D model generated.")

    generated_model_path = os.path.join(MODEL_DIR, f"{uuid4()}.glb")
    with open(generated_model_path, 'wb') as f:
        f.write(model_image)
    logging.info(f"3D model saved as {generated_model_path}")

    model_url = f"http://localhost:8888/{os.path.basename(generated_model_path)}"
    logging.info(f"3D model is available at {model_url}")

    # Prepare response
    response: OutputClass = model.response
    response.message = f"3D model url: {model_url}"


############################################################
                        #  IMAGE URL 
############################################################

def start_http_server():
    PORT = 8888
    os.chdir(MODEL_DIR)
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        logging.info(F"serving at port {PORT}")
        httpd.serve_forever()

if __name__ == '__main__':
    server_thread = Thread(start_http_server)
    server_thread.daemon = True
    server_thread.start()

    logging.info("HTTP server running...")

    # [
    #     "c25dcd829d134ea98f5ae4dd311d13bc.node3.openfabric.network","f0b5f319156c4819b9827000b17e511a.node3.openfabric.network"
    # ]

    # docker build -t dimensa-app .

    #     docker run -it -d \
    #   -v /Users/midhuncraj/PersonalProjects/Dimensa/app/models_3d:/savedmodels \
    #   -v /Users/midhuncraj/PersonalProjects/Dimensa/app/huggingface:/root/.cache/huggingface \
    #   -p 8888:8888 dimensa-app