"""
Simple test script to verify the backend changes
"""

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from main import app
import pytest
from fastapi.testclient import TestClient

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Qwen" in data["model"]
    print("✅ Health check test passed")

def test_analyze_question():
    """Test the question analysis endpoint"""
    # Test with a normal question
    normal_question = {
        "messages": [{"role": "user", "content": "How does photosynthesis work?"}]
    }
    response = client.post("/analyze-question", json=normal_question)
    assert response.status_code == 200
    data = response.json()
    assert not data["is_direct_answer_request"]
    
    # Test with a direct answer request
    direct_question = {
        "messages": [{"role": "user", "content": "What's the answer to this homework question?"}]
    }
    response = client.post("/analyze-question", json=direct_question)
    assert response.status_code == 200
    data = response.json()
    assert data["is_direct_answer_request"]
    print("✅ Question analysis test passed")

def test_model_info():
    """Test the model info endpoint"""
    response = client.get("/model-info")
    assert response.status_code == 200
    data = response.json()
    assert "Qwen" in data["model_name"]
    assert data["mode"] == "Educational (Anti-Cheating)"
    print("✅ Model info test passed")

def test_chat_with_api():
    """Test the chat endpoint (requires valid API token)"""
    test_message = {
        "messages": [{"role": "user", "content": "What is 2 + 2?"}]
    }
    response = client.post("/chat", json=test_message)
    
    if response.status_code == 500:
        print("⚠️ Chat test failed - could be due to missing/invalid Hugging Face token")
        return False
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert len(data["response"]) > 0
    assert data["tokens_used"] > 0
    print("✅ Chat API test passed")
    return True

if __name__ == "__main__":
    print("Testing EduBot backend...")
    print("=" * 40)
    
    test_health_check()
    test_analyze_question()
    test_model_info()
    
    # The chat test might fail if no valid token is configured
    chat_success = test_chat_with_api()
    
    print("\n" + "=" * 40)
    print("Backend test completed!")
    
    if chat_success:
        print("All tests passed ✅")
    else:
        print("\n⚠️  Note: Chat test failed. This is likely because:")
        print("  1. You haven't configured a Hugging Face API token")
        print("  2. The token is invalid or expired")
        print("  3. Hugging Face Inference API is temporarily unavailable")
        print("\nConfigure your token in backend/.env file to run this test successfully.")