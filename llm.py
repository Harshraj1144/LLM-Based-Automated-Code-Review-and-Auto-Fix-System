import json
import logging
import httpx
from backend.app.config import settings

logger = logging.getLogger("app.llm")
logging.basicConfig(level=logging.INFO)

SYSTEM_INSTRUCTION = """You are an expert automated code reviewer and security auditor.
Analyze the provided source code for:
1. Bugs, syntax errors, and logical errors.
2. Security vulnerabilities (e.g., SQL injection, cross-site scripting (XSS), resource leaks, hardcoded credentials, buffer overflows).
3. Performance bottlenecks, memory leaks, and inefficiencies.
4. Coding standard and style violations (e.g., PEP 8 in Python, naming conventions, missing error handling).

You MUST respond ONLY with a raw JSON object matching the following structure. Do not wrap the JSON output in markdown blocks (like ```json ... ```) or include any other text before/after the JSON.

JSON Schema:
{
  "score": <0-100 integer representing overall code quality. 100 means perfect code, lower scores indicate more/worse issues.>,
  "summary": "<A 2-3 sentence overview summarizing findings.>",
  "corrected_code": "<The complete corrected source code. Do not truncate. Keep original structure but fix all detected issues.>",
  "issues": [
    {
      "id": "issue-1",
      "category": "bug" | "security" | "performance" | "style",
      "severity": "critical" | "warning" | "info",
      "line": <line number in the original code, 1-indexed.>,
      "title": "<Short title of the issue>",
      "description": "<Detailed explanation of the issue, what causes it, and why it should be fixed.>",
      "suggestion": "<Detailed instructions on how to fix this issue.>"
    }
  ]
}
"""

def get_demo_response(original_code: str, language: str) -> dict:
    """Returns a mock code review to demonstrate all frontend features when no API key is set."""
    lines = original_code.splitlines()
    code_length = len(lines)
    
    # Simple mockup issues based on code length
    issues = [
      {
        "id": "demo-issue-1",
        "category": "security",
        "severity": "critical",
        "line": min(3, code_length),
        "title": "API Key Missing Warning",
        "description": "The system is running in demo mode because GEMINI_API_KEY is not configured in the backend .env file.",
        "suggestion": "Please create a .env file in the project root and add: GEMINI_API_KEY=your_key"
      },
      {
        "id": "demo-issue-2",
        "category": "performance",
        "severity": "warning",
        "line": min(5, code_length) if code_length >= 5 else 1,
        "title": "Optimizing API Performance",
        "description": "Once an API key is provided, the backend will perform real-time code analysis utilizing the Gemini 2.5 Flash model.",
        "suggestion": "Configure the environment variable to enable live analysis."
      }
    ]

    # Simple text additions for corrected code
    comment_char = "#" if language.lower() in ["python", "ruby", "perl"] else "//"
    corrected = f"{comment_char} --- LIVE ANALYSIS ENABLED ONCE GEMINI_API_KEY IS SET ---\n" + original_code

    return {
        "score": 65,
        "summary": "This is a DEMO review. To enable real code analysis, please set your GEMINI_API_KEY in the .env file.",
        "corrected_code": corrected,
        "issues": issues
    }

def clean_json_response(text: str) -> dict:
    """Cleans code blocks and other formatting wrapper text around JSON responses."""
    text = text.strip()
    # Strip markdown wrappers if present
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    return json.loads(text)

async def analyze_code_gemini(code: str, language: str, api_key: str) -> dict:
    """Calls Gemini API using httpx to guarantee compatibility and avoid library conflicts."""
    models = ["gemini-3.5-flash", "gemini-flash-latest", "gemini-2.5-flash"]
    headers = {"Content-Type": "application/json"}
    prompt = f"Please review this {language} code:\n\n{code}"
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        },
        "systemInstruction": {
            "parts": [{"text": SYSTEM_INSTRUCTION}]
        }
    }
    
    last_error = None
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        logger.info(f"Attempting code analysis using {model}...")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code != 200:
                    logger.warning(f"Gemini API {model} Error: {response.status_code} - {response.text}")
                    last_error = f"Gemini API error ({model}): {response.text}"
                    continue
                    
                data = response.json()
                try:
                    raw_text = data['candidates'][0]['content']['parts'][0]['text']
                    return clean_json_response(raw_text)
                except (KeyError, IndexError, json.JSONDecodeError) as e:
                    logger.warning(f"Failed to parse Gemini response for {model}: {e}. Raw response: {data}")
                    last_error = f"Failed to parse response from {model}."
                    continue
        except Exception as e:
            logger.warning(f"Exception during request to {model}: {e}")
            last_error = str(e)
            continue
            
    raise Exception(f"All Gemini models failed. Last error: {last_error}")

async def analyze_code_openai(code: str, language: str, api_key: str) -> dict:
    """Calls OpenAI chat completion API."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    prompt = f"Please review this {language} code:\n\n{code}"
    
    payload = {
        "model": "gpt-4-turbo-preview",
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": prompt}
        ]
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            logger.error(f"OpenAI API Error: {response.status_code} - {response.text}")
            raise Exception(f"OpenAI API error: {response.text}")
            
        data = response.json()
        try:
            raw_text = data['choices'][0]['message']['content']
            return clean_json_response(raw_text)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            logger.error(f"Failed to parse OpenAI response: {e}. Raw response: {data}")
            raise Exception("Failed to parse code review response from OpenAI API.")

async def analyze_code(code: str, language: str) -> dict:
    """Main LLM analysis entry point. Directs call to selected provider or falls back to demo mode."""
    if settings.gemini_api_key:
        logger.info("Analyzing code using Gemini API...")
        try:
            return await analyze_code_gemini(code, language, settings.gemini_api_key)
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}. Falling back to demo mode...")
            return get_demo_response(code, language)
            
    elif settings.openai_api_key:
        logger.info("Analyzing code using OpenAI API...")
        try:
            return await analyze_code_openai(code, language, settings.openai_api_key)
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}. Falling back to demo mode...")
            return get_demo_response(code, language)
            
    else:
        logger.info("No API keys found. Returning demo review response...")
        return get_demo_response(code, language)
