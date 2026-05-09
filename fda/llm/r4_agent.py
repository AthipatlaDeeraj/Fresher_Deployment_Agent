import json
import os
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from fda.core.logger import logger
from dotenv import load_dotenv

load_dotenv()

class TrainingTheme(BaseModel):
    training_required: bool = Field(description="Whether specific training is required based on the skill gap")
    primary_theme: str = Field(description="The main training topic suggested")
    secondary_topics: List[str] = Field(description="List of supplementary topics")
    reasoning: str = Field(description="Why this training is suggested")

def generate_training_suggestions(sanitized_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    R4 LLM Agent: Generates training themes based on skill gaps.
    Uses strict JSON schema enforcement via Pydantic structured output.
    """
    if not os.environ.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY") == "your_api_key_here":
        logger.warning("GROQ_API_KEY not set. Using fallback R4 logic.")
        return fallback_r4_logic(sanitized_data)

    try:
        # Use a model that supports structured outputs well
        llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2)
        structured_llm = llm.with_structured_output(TrainingTheme)
        
        prompt = PromptTemplate.from_template(
            """
            You are a technical training coordinator. Based on the project data, suggest a training theme for a new junior employee.
            
            Project Data:
            {data}
            
            If "demanded_skills" is empty, suggest "General Fresher Onboarding".
            Otherwise, create a curriculum based on "demanded_skills" and "current_team_skills".
            """
        )
        
        chain = prompt | structured_llm
        
        # Log Audit input
        logger.info(f"AUDIT LOG - R4 LLM Input for {sanitized_data.get('project_name')}: {json.dumps(sanitized_data)}")
        
        result: TrainingTheme = chain.invoke({"data": json.dumps(sanitized_data, indent=2)})
        output_dict = result.model_dump()
        
        logger.info(f"AUDIT LOG - R4 LLM Output: {json.dumps(output_dict)}")
        return output_dict
        
    except Exception as e:
        logger.error(f"R4 LLM failed for {sanitized_data.get('project_name')}: {e}")
        return fallback_r4_logic(sanitized_data)

def fallback_r4_logic(data: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback rule-based logic if LLM fails or is unavailable."""
    all_skills = set(data["current_team_skills"]).union(set(data["demanded_skills"]))
    if all_skills:
        theme = f"Foundational training on: {', '.join(all_skills)}"
    else:
        theme = "General Fresher Onboarding & Project Orientation"
        
    return {
        "training_required": True,
        "primary_theme": theme,
        "secondary_topics": [],
        "reasoning": "Fallback deterministic logic used."
    }
