
# 🌐 DIMENSA | AI-POWERED 3D IMAGINATION 🚀

Imagine → Generate → Explore
Create stunning 3D models from simple prompts using a powerful pipeline driven by Openfabric, AI21 API!

## 🛠 The Pipeline

📝 Your Prompt  
↓  
🧠 LLM (AI21)  
↓  
🖼️ Text-to-Image App (Openfabric)  
↓  
🧾 Image Output  
↓  
🧊 Image-to-3D App (Openfabric)  
↓  
🎉 3D Model Output  

Simple. Elegant. Powerful.  

Example Prompt:
> “Design a cyberpunk city skyline at night.”
```bash

→ LLM expands into vivid, textured visual descriptions  
→ Text-to-Image App renders a cityscape  
→ Image-to-3D app converts it into depth-aware 3D  
→ The system remembers the request for remixing later
```

## 🌟 Features

- 🎨 Visual GUI with Streamlit
- 🔍 ChromaDB for memory similarity
- ⚡ End-to-end Dockerized microservices
- 📦 Modular structure for extensibility

## 🗂️ Folder Structure
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

## 🧭 Getting Started
### Clone the repo
```bash
git clone https://github.com/midhun-craj/dimensa.git
cd dimensa
```


### 🔗 Set up API Key for AI21 Studio
Go to the site below sign up and generate a free api key:
```bash
https://docs.ai21.com/
``` 
Then:
```bash
cd fastapi-app
touch .env
```
Inside .env, paste:
```bash
AI21_API_KEY=your_api_key
```

## 🐳 Run with Docker Compose (Recommended)
### ✅ Start all services
```bash 
COMPOSE_BAKE=TRUE docker compose up -d --build
```
### 🛑 Stop everything
```bash
docker compose down
```
### 📊 Check if everything's running
```bash
docker ps
```

## 🛠️ Run Each Service Manually (Alternative) 
```bash 
docker build -t image_name .
docker run -d -p port:port --name container_name image_name
```

## 🖥 Access the App
Launch your browser and visit:
```bash 
http://localhost:8081
```
🎨 Enter a prompt → Watch AI create 3D art from your imagination!