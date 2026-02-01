# EduBot - Fast Educational AI

A free 24/7 educational AI chatbot that guides learning instead of giving direct answers.

## Features

- ✅ **Educational approach** - Guides learning, never gives direct answers
- ✅ **Free 24/7 hosting** - Runs on cloud with no local dependencies
- ✅ **Fast responses** - Uses Hugging Face Inference API with optimized model
- ✅ **Clean UI** - Simple, professional interface
- ✅ **No cheating** - Prevents direct answers to homework/tests

## How it works

Instead of giving direct answers, EduBot:
- Uses real-world analogies
- Asks guiding questions  
- Provides hints without conclusions
- Encourages discovery learning

Perfect for schools - prevents cheating while promoting actual learning.

## Quick Start (Local Development)

1. **Create a Hugging Face account** and get your API token from [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

2. **Set up environment variables:**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env file and add your Hugging Face token
   ```

3. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Start backend:**
   ```bash
   python main.py
   ```

5. **Open frontend:**
   Open `frontend/index.html` in your browser

## Deployment (Free 24/7 Hosting)

### Option 1: Render.com (Recommended)

1. **Create a GitHub repository** with your code (make sure to exclude the large .gguf file using .gitignore)

2. **Sign up for Render.com** (free account)

3. **Deploy backend:**
   - Go to Render.com and create a new "Web Service"
   - Connect your GitHub repository
   - Configure:
     - Build Command: `python -m pip install -r backend/requirements.txt`
     - Start Command: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app`
     - Environment Variables:
       - `HUGGINGFACE_TOKEN`: Your Hugging Face API token
       - `MODEL_NAME`: `Qwen/Qwen2.5-1.5B-Instruct`

4. **Deploy frontend:**
   - Create a new "Static Site" on Render
   - Connect your GitHub repository
   - Configure:
     - Build Command: `echo "Static site ready"`
     - Publish Directory: `frontend`

5. **Update API endpoint:**
   - In `frontend/script.js`, update the deployed API URL to your Render backend URL

### Option 2: Vercel + Render

- Frontend on Vercel (free)
- Backend on Render (free)

### Option 3: Railway (Alternative to Render)

1. **Create a GitHub repository** with your code (make sure to exclude the large .gguf file using .gitignore)

2. **Sign up for Railway** (free account)

3. **Deploy backend:**
   - Go to Railway.app and create a new "Project"
   - Connect your GitHub repository
   - Configure:
     - Build Command: `python -m pip install -r backend/requirements.txt`
     - Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
     - Environment Variables:
       - `HUGGINGFACE_TOKEN`: Your Hugging Face API token
       - `MODEL_NAME`: `Qwen/Qwen2.5-1.5B-Instruct`

4. **Deploy frontend:**
   - You can deploy frontend to Railway as a static site or use Netlify/Vercel
   - For Railway static site:
     - Create a new "Static Site" service
     - Connect your GitHub repository
     - Configure:
       - Build Command: `echo "Static site ready"`
       - Publish Directory: `frontend`

5. **Update API endpoint:**
   - In `frontend/script.js`, update the deployed API URL to your Railway backend URL

### Option 4: Netlify + Railway

- Frontend on Netlify (free)
- Backend on Railway (free)

## Technology Stack

- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **Backend**: FastAPI (Python)
- **AI Model**: Qwen/Qwen2.5-1.5B-Instruct (via Hugging Face Inference API)
- **Hosting**: Render.com (free tier)

## Cost Information

- **Hugging Face Inference API**: Free tier includes 100K tokens/month
- **Render.com**: Free tier includes:
  - 1 web service instance
  - 1 static site
  - 750 hours of runtime/month
  - 100 GB bandwidth/month

## Environment Variables

### Backend

```
HUGGINGFACE_TOKEN=your_huggingface_api_token
MODEL_NAME=Qwen/Qwen2.5-1.5B-Instruct
```

### Frontend

Update `API_BASE_URL` in `frontend/script.js` with your deployed backend URL.

## Performance Optimization

- Uses smaller Qwen2.5-1.5B-Instruct model for faster responses
- Limits conversation history to 3 messages
- Optimized for cost efficiency
- CORS enabled for all origins (for deployment)

## Educational Behavior Enforcement

The system prompt enforces educational behavior:
- Never gives direct answers
- Uses analogies and real-world examples
- Asks guiding questions
- Provides hints without conclusions
- Encourages discovery learning

## Contributing

Feel free to submit issues and pull requests to improve EduBot.