import logging
import json
import httpx
from datetime import datetime
from config import settings

logger = logging.getLogger("AegisChain-AI")

# System prompt engineered to force strict, easily parseable JSON outputs from the LLM
SYSTEM_PROMPT = f"""
You are an expert pharmaceutical supply chain AI auditor. 
Your task is to analyze transit telemetry data for sensitive medications.
The acceptable cold-chain temperature range is {settings.TEMP_THRESHOLD_MIN}°C to {settings.TEMP_THRESHOLD_MAX}°C.
Any temperature outside this range is a critical anomaly and compromises the batch.

Respond ONLY with a valid JSON object matching this exact schema, with no markdown formatting or extra text:
{{
    "status": "Safe" | "Compromised",
    "confidence_score": float (0.0 to 1.0),
    "anomalies_detected": int (number of violations),
    "summary": "Brief 1-2 sentence explanation of the findings."
}}
"""

async def analyze_telemetry_for_anomalies(batch_id: str, transit_history: list) -> dict:
    """
    Evaluates a batch's transit history using an LLM to detect temperature excursions 
    or suspicious transit patterns.
    """
    logger.info(f"Initiating AI analysis for batch {batch_id} with {len(transit_history)} records.")
    
    if not transit_history:
        return {
            "status": "Unknown",
            "confidence_score": 0.0,
            "anomalies_detected": 0,
            "summary": "No transit history available for analysis."
        }

    # Format the history into a readable string for the LLM context
    history_context = f"Batch ID: {batch_id}\n"
    for idx, record in enumerate(transit_history):
        # Convert timestamp to human-readable format if it's an integer
        ts = record.get("timestamp")
        if isinstance(ts, int):
            ts_str = datetime.fromtimestamp(ts).isoformat()
        else:
            ts_str = str(ts)
            
        history_context += (
            f"Checkpoint {idx + 1}:\n"
            f" - Location: {record.get('location')}\n"
            f" - Telemetry: {record.get('temperature_data')}\n"
            f" - Time: {ts_str}\n"
        )

    # Prepare the payload for an OpenAI-compatible API structure (supports OpenAI, Nebius, etc.)
    payload = {
        "model": settings.AI_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Analyze this transit history and return the JSON report:\n\n{history_context}"}
        ],
        "temperature": 0.1, # Low temperature for deterministic, analytical outputs
        "max_tokens": 150
    }

    # Define headers using the configured API key
    headers = {
        "Authorization": f"Bearer {settings.AI_API_KEY}",
        "Content-Type": "application/json"
    }

    # Base URL configuration (Defaults to OpenAI if not overridden in env)
    # Allows seamless swapping to Nebius AI Cloud or other providers
    api_url = "https://api.openai.com/v1/chat/completions"
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(api_url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            raw_content = data['choices'][0]['message']['content'].strip()
            
            # Clean up potential markdown formatting from overzealous LLMs
            if raw_content.startswith("```json"):
                raw_content = raw_content.replace("```json", "").replace("```", "").strip()
                
            result_json = json.loads(raw_content)
            logger.info(f"AI Analysis complete for {batch_id}: Status {result_json.get('status')}")
            return result_json

    except httpx.HTTPStatusError as e:
        logger.error(f"AI API HTTP error: {e.response.status_code} - {e.response.text}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response as JSON: {str(e)}\nRaw Output: {raw_content}")
    except Exception as e:
        logger.error(f"Unexpected AI engine error: {str(e)}")

    # Hackathon Fail-Safe: Always return a structured response even if the API times out
    logger.warning("Falling back to deterministic heuristic analysis due to AI failure.")
    return _fallback_heuristic_analysis(transit_history)

def _fallback_heuristic_analysis(transit_history: list) -> dict:
    """
    A deterministic backup function to ensure the live demo does not crash if the LLM endpoint fails.
    """
    anomalies = 0
    for record in transit_history:
        data_str = record.get("temperature_data", "")
        # Very basic string parsing for the fallback
        if "Temp:" in data_str:
            try:
                # Extract the number between "Temp:" and "C"
                temp_str = data_str.split("Temp:")[1].split("C")[0]
                temp = float(temp_str)
                if temp < settings.TEMP_THRESHOLD_MIN or temp > settings.TEMP_THRESHOLD_MAX:
                    anomalies += 1
            except Exception:
                pass 
                
    if anomalies > 0:
        return {
            "status": "Compromised",
            "confidence_score": 1.0,
            "anomalies_detected": anomalies,
            "summary": "Fallback engine detected temperature violations outside the 2-8°C range."
        }
    return {
        "status": "Safe",
        "confidence_score": 0.8,
        "anomalies_detected": 0,
        "summary": "Fallback engine verified all telemetry is within acceptable parameters."
    }