import json
import os
import pandas as pd
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from fda.core.logger import logger
from dotenv import load_dotenv

load_dotenv()

# ── Sanitization ────────────────────────────────────────────────────────────

def sanitize_project_data(project_row: pd.Series, ris_skills: set, so_skills: set) -> Dict[str, Any]:
    """
    Strict data sanitization before LLM calls.
    Ensures no PII or raw DataFrames are passed to the LLM.
    Returns only high-level aggregates and text features.
    """
    return {
        "project_name": str(project_row.get("project_name", "UNKNOWN")),
        "junior_gap_percentage": round(float(project_row.get("junior_gap", 0)), 2),
        "current_junior_percentage": round(float(project_row.get("junior_pct", 0)), 2),
        "team_size": int(project_row.get("total_headcount", 0)),
        "current_team_skills": list(ris_skills),
        "demanded_skills": list(so_skills)
    }


# ── R3 Agent ─────────────────────────────────────────────────────────────────

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


# ── R4 Agent ─────────────────────────────────────────────────────────────────

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
