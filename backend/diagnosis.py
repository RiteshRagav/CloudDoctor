import os
import json
import logging
import uuid
from typing import Optional, Dict, Any
from models import DiagnosisResult

logger = logging.getLogger(__name__)


async def run_diagnosis(logs_text: str, scenario: str, incident_id: str) -> DiagnosisResult:
    """Run AI diagnosis on the given logs using Emergent LLM key + OpenAI GPT-4o."""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage

        api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            logger.error("EMERGENT_LLM_KEY not configured")
            return DiagnosisResult(
                root_cause="LLM not configured - missing EMERGENT_LLM_KEY",
                severity="unknown",
                confidence=0,
                recommended_fixes=["Configure EMERGENT_LLM_KEY in backend .env"],
                estimated_mttr="unknown",
            )

        chat = LlmChat(
            api_key=api_key,
            session_id=f"diagnosis-{incident_id[:8]}-{uuid.uuid4().hex[:6]}",
            system_message="""You are CloudDoctor, an expert AI cloud infrastructure diagnostics system.
You analyze application logs from cloud infrastructure to diagnose issues.

When given logs, respond with ONLY a valid JSON object (no markdown, no code blocks, no extra text):
{
  "root_cause": "Clear, concise description of the root cause",
  "severity": "critical|high|medium|low",
  "confidence": <integer 0-100>,
  "recommended_fixes": ["Actionable fix 1", "Actionable fix 2", "Actionable fix 3"],
  "estimated_mttr": "X minutes/hours"
}

Be specific about the root cause based on the log patterns. Provide actionable fixes."""
        )
        chat.with_model("openai", "gpt-4o")

        user_msg = UserMessage(
            text=f"Diagnose this cloud infrastructure incident.\nScenario type: {scenario}\n\nLogs:\n{logs_text}"
        )

        response = await chat.send_message(user_msg)
        logger.info(f"LLM response for incident {incident_id}: {response[:100]}...")

        # Parse response
        clean = response.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1] if "\n" in clean else clean[3:]
            clean = clean.rsplit("```", 1)[0]
        clean = clean.strip()

        data = json.loads(clean)
        return DiagnosisResult(
            root_cause=data.get("root_cause", "Unable to determine"),
            severity=data.get("severity", "unknown"),
            confidence=int(data.get("confidence", 0)),
            recommended_fixes=data.get("recommended_fixes", []),
            estimated_mttr=data.get("estimated_mttr", "unknown"),
        )

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        return DiagnosisResult(
            root_cause=f"AI analysis completed but response format error: {str(e)}",
            severity="medium",
            confidence=60,
            recommended_fixes=["Retry diagnosis", "Check LLM configuration"],
            estimated_mttr="unknown",
        )
    except Exception as e:
        logger.error(f"Diagnosis failed: {e}")
        return DiagnosisResult(
            root_cause=f"Diagnosis error: {str(e)}",
            severity="unknown",
            confidence=0,
            recommended_fixes=["Check LLM API key", "Verify network connectivity"],
            estimated_mttr="unknown",
        )


async def check_llm_health() -> Dict[str, Any]:
    """Check if LLM service is accessible."""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage

        api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            return {"status": "error", "message": "EMERGENT_LLM_KEY not configured"}

        chat = LlmChat(
            api_key=api_key,
            session_id=f"health-check-{uuid.uuid4().hex[:8]}",
            system_message="Respond with OK"
        )
        chat.with_model("openai", "gpt-4o")

        response = await chat.send_message(UserMessage(text="ping"))
        if response:
            return {"status": "connected", "message": "GPT-4o via Emergent key operational"}
        return {"status": "error", "message": "Empty response from LLM"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
