
# 🚀 DIMENSA | AI-POWERED 3D IMAGINATION

Created an intelligent, end-to-end pipeline for 3D model generation powered by Openfabric and AI21 api for expanding the prompt creatively.

## 🛠 The Pipeline

User Prompt
↓
Local LLM (DeepSeek or LLaMA)
↓
Text-to-Image App (Openfabric)
↓
Image Output
↓
Image-to-3D App (Openfabric)
↓
3D Model Output

Simple. Elegant. Powerful.

---

Prompt:
> “Design a cyberpunk city skyline at night.”
```bash

→ LLM expands into vivid, textured visual descriptions  
→ Text-to-Image App renders a cityscape  
→ Image-to-3D app converts it into depth-aware 3D  
→ The system remembers the request for remixing later
```

## 🚀 Points

- 🎨 Visual GUI with Streamlit
- 🔍 ChromaDB for memory similarity

## Folder Structure
```bash
dimensa/
├── fastapi-app/
│   ├── main
│   ├── memory/              
│   │   ├── long_term_memory.py              
│   │   └── short_term_memory.py
│   ├── .env
│   ├── Dockerfile
│   └── requirements.txt
│
├── flask-app/
│   ├── config/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── remote.py
│   │   └── stub.py
│   ├── datastore/
│   ├── ontology_dc8f06af066e4a7880a5938933236037/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── input.py 
│   │   └── output.py
│   ├── main.py
│   ├── ignite.py
│   ├── start.sh
│   ├── poetry.lock
│   ├── Dockerfile
│   └── pyproject.toml      
│
├── streamlit-app/
│   ├── streamlit_app.py                    
│   ├── Dockerfile         
│   └── requirements.txt       
│
├── .gitignore               
├── docker-compose.yml             
└── README.md                      
```

# Steps To Run
Clone the repository:
```bash
git clone https://github.com/midhun-craj/dimensa.git
```
Navigate to the project folder:
```bash
cd dimensa
```

##🔗 API Integration
1. Go to the site below sign up and generate a free api key
```bash
https://docs.ai21.com/
``` 

2. Map to the fastapi app and create a .env file inside the fastapi-app folder and paste the ai21 api key.
```bash
cd fastapi-app
touch .env
```
Inside the .env file paste the api key 
```bash
AI21_API_KEY=your_api_key
```

### Commands to run the project using docker compose
```bash 
COMPOSE_BAKE=TRUE docker compose up -d --build
```
To stop the docker compose
```bash
docker compose down
```
To verify the containers are running:
run this command and see the running containers
```bash
docker ps
```

### Commands to run the project using docker 
Run each service app using this command
```bash 
docker build -t image_name .
docker run -d -p port:port --name container_name image_name
```

After running the project the entry point can be viewed at \|/
```bash 
http://localhost:8081
```