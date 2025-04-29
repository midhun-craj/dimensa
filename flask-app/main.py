import logging
from typing import Dict
import base64

from ontology_dc8f06af066e4a7880a5938933236037.config import ConfigClass
from ontology_dc8f06af066e4a7880a5938933236037.input import InputClass
from ontology_dc8f06af066e4a7880a5938933236037.output import OutputClass, OutputClassSchema
from openfabric_pysdk.context import AppModel, State
from core.stub import Stub

# Configurations for the app
configurations: Dict[str, ConfigClass] = dict()


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

    # STEP - 1 Prompt to image app
    object1 = stub.call(request.attachments[0], {'prompt': user_prompt}, 'super-user')
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


    # STEP - 2 Image to 3D model app
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

    model_image_string = base64.b64encode(model_image).decode('utf-8')

    # Prepare response
    response: OutputClass = model.response
    response.message = "3D model generated successfully"
    response.generated_model = model_image_string

    # response_dict = OutputClassSchema().dump(response)
    # logging.info(f"Serialized JSON Response: {response_dict}")