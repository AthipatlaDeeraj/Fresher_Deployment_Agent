import json
import os
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from fda.core.logger import logger
from dotenv import load_dotenv

load_dotenv()

from pydantic import BaseModel, Field

class DeploymentSuitability(BaseModel):
    suitable_for_fresher: bool = Field(description="Whether the project is suitable for a fresher")
    skill_overlap_score: float = Field(description="Score between 0.0 and 1.0 for skill overlap")
    role_match_score: float = Field(description="Score between 0.0 and 1.0 for role match")
    reasoning: str = Field(description="Brief explanation of the evaluation")

def analyze_deployment_opportunity(sanitized_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    R3 LLM Agent: Evaluates role/skill suitability for fresher deployment.
    Uses Groq to analyze skill compatibility and determine an overlap score.
    """
    # Fallback if no API key
    if not os.environ.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY") == "your_api_key_here":
        logger.warning("GROQ_API_KEY not set. Using fallback R3 logic.")
        return fallback_r3_logic(sanitized_data)

    try:
        llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2)
        structured_llm = llm.with_structured_output(DeploymentSuitability)
        
        prompt = PromptTemplate.from_template(
            """
            You are an expert IT resource management AI. Evaluate the following project for entry-level (fresher) deployment suitability.
            
            Project Data:
            {data}
            
            Analyze the overlap between "current_team_skills" (what the team currently has) and "demanded_skills" (what is needed).
            Determine if the demanded skills are suitable for an entry-level employee to learn.
            Also evaluate the role match suitability based on the skills context.
            """
        )
        
        chain = prompt | structured_llm
        
        # Log Audit input
        logger.info(f"AUDIT LOG - R3 LLM Input for {sanitized_data.get('project_name')}: {json.dumps(sanitized_data)}")
        
        result = chain.invoke({"data": json.dumps(sanitized_data, indent=2)})
        output_dict = result.model_dump()
        
        logger.info(f"AUDIT LOG - R3 LLM Output: {json.dumps(output_dict)}")
        return output_dict
        
    except Exception as e:
        logger.error(f"R3 LLM failed for {sanitized_data.get('project_name')}: {e}")
        return fallback_r3_logic(sanitized_data)

def fallback_r3_logic(data: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback rule-based logic if LLM fails or is unavailable."""
    overlap = len(set(data["current_team_skills"]).intersection(set(data["demanded_skills"])))
    score = min(1.0, overlap * 0.2)
    return {
        "suitable_for_fresher": data["junior_gap_percentage"] > 0,
        "skill_overlap_score": score,
        "role_match_score": 0.5,
        "reasoning": "Fallback deterministic logic used due to missing API key or LLM error."
    }
