"""
Educational AI Chatbot Backend
Uses Hugging Face Inference API for free 24/7 hosting
Enforces educational behavior and prevents cheating
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import logging
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Get Hugging Face token from environment variables
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-1.5B-Instruct")  # Smaller, faster model for free usage
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "512"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.5"))
TOP_P = float(os.getenv("TOP_P", "0.8"))
TOP_K = int(os.getenv("TOP_K", "30"))

# ============================================================================
# SYSTEM PROMPT - CORE EDUCATIONAL BEHAVIOR ENFORCEMENT
# ============================================================================

SYSTEM_PROMPT = """You are an educational tutor. NEVER give direct answers to homework/tests. Instead:

1. Use analogies and real-world examples
2. Ask guiding questions
3. Give hints without conclusions
4. Encourage discovery

If asked for direct answers, say: "I can't give you the answer, but let me help you understand..."

Be concise, encouraging, and focus on learning concepts."""

# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

app = FastAPI(
    title="Educational AI Chatbot",
    description="Educational chatbot using Hugging Face Inference API",
    version="1.0.0"
)

# CORS Configuration - Allow all origins for deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# HUGGING FACE INFERENCE CLIENT
# ============================================================================

if not HUGGINGFACE_TOKEN:
    logger.error("HUGGINGFACE_TOKEN environment variable not set")
    raise Exception("HUGGINGFACE_TOKEN environment variable is required")

try:
    client = InferenceClient(
        model=MODEL_NAME,
        token=HUGGINGFACE_TOKEN
    )
    logger.info(f"✓ Connected to Hugging Face Inference API with model: {MODEL_NAME}")
except Exception as e:
    logger.error(f"Error connecting to Hugging Face Inference API: {e}")
    raise

# ============================================================================
# DATA MODELS
# ============================================================================

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    temperature: Optional[float] = TEMPERATURE
    max_tokens: Optional[int] = MAX_TOKENS

class ChatResponse(BaseModel):
    response: str
    tokens_used: int
    model: str = MODEL_NAME

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_messages_for_huggingface(messages: List[Message]) -> List[dict]:
    """
    Format conversation history for Hugging Face chat completions
    """
    formatted = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in messages:
        formatted.append({"role": msg.role, "content": msg.content})
    return formatted

def detect_cheating_attempt(user_message: str) -> bool:
    """Quick cheating detection"""
    keywords = ["solve this", "answer this", "do my homework", "just tell me", "what's the answer"]
    return any(k in user_message.lower() for k in keywords)

def add_educational_context(user_message: str) -> str:
    """Add educational context if needed"""
    if detect_cheating_attempt(user_message):
        return f"[GUIDE LEARNING] Student asking for direct answer: {user_message}"
    return user_message

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": MODEL_NAME,
        "mode": "educational"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint
    Processes user message and returns educational response
    """
    try:
        if not request.messages:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        # Get the last user message
        last_message = request.messages[-1]
        if last_message.role != "user":
            raise HTTPException(status_code=400, detail="Last message must be from user")
        
        # Add educational context
        enhanced_message = add_educational_context(last_message.content)
        
        # Keep only last 3 messages for speed and cost efficiency
        recent_messages = request.messages[-3:] if len(request.messages) > 3 else request.messages
        
        # Replace last message with enhanced version
        modified_messages = recent_messages.copy()
        modified_messages[-1] = {"role": "user", "content": enhanced_message}
        
        logger.info(f"Processing message: {last_message.content[:100]}...")
        
        # Generate response using Hugging Face Inference API
        response = client.chat_completion(
            messages=format_messages_for_huggingface(modified_messages),
            max_tokens=request.max_tokens or MAX_TOKENS,
            temperature=request.temperature or TEMPERATURE,
            top_p=TOP_P,
            top_k=TOP_K,
        )
        
        # Extract response text
        response_text = response.choices[0].message.content.strip()
        tokens_used = response.usage.completion_tokens
        
        logger.info(f"Generated response ({tokens_used} tokens)")
        
        return ChatResponse(
            response=response_text,
            tokens_used=tokens_used,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/analyze-question")
async def analyze_question(request: ChatRequest):
    """
    Analyze if a question is asking for direct answers
    Returns educational guidance
    """
    try:
        if not request.messages:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        last_message = request.messages[-1].content
        is_cheating = detect_cheating_attempt(last_message)
        
        return {
            "is_direct_answer_request": is_cheating,
            "recommendation": "Reframe as learning opportunity" if is_cheating else "Safe to answer educationally"
        }
    except Exception as e:
        logger.error(f"Error in analyze-question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model-info")
async def model_info():
    """Get information about the loaded model"""
    return {
        "model_name": MODEL_NAME,
        "mode": "Educational (Anti-Cheating)",
        "system_prompt_active": True,
    }

# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("Educational AI Chatbot Backend Started")
    logger.info("=" * 60)
    logger.info(f"Model: {MODEL_NAME}")
    logger.info(f"Mode: Educational (Anti-Cheating)")
    logger.info(f"API running on: http://localhost:8001")
    logger.info(f"Docs available at: http://localhost:8001/docs")
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Backend shutting down...")

# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
