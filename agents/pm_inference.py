"""
PM Role + Level Inference System

Analyzes user data (resume, LinkedIn, work samples, etc.) to infer PM role type, level, archetype, competencies, and leverage ratio.
Uses the meta-synthesis PM levels framework for evidence-based assessment.
"""
import yaml
import os
import json
from typing import Dict, List, Optional, Any
from core.types import PMInferenceResult, WorkSample


def call_openai(prompt: str, model: str = "gpt-4", temperature: float = 0.1) -> str:
    """Call OpenAI API with the given prompt."""
    import openai
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment")
    
    client = openai.OpenAI(api_key=api_key)
    
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": "You are an expert PM leveling specialist."},
            {"role": "user", "content": prompt}
        ]
    )
    
    content = response.choices[0].message.content
    if content is None:
        raise ValueError("Empty response from OpenAI API")
    
    return content.strip()


class PMLevelsFramework:
    """Loads and manages the PM levels framework for inference."""
    
    def __init__(self, framework_path: str = "data/pm_levels.yaml"):
        self.framework_path = framework_path
        self.framework = self._load_framework()
    
    def _load_framework(self) -> Dict[str, Any]:
        """Load the PM levels framework from YAML."""
        try:
            with open(self.framework_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"PM levels framework not found at {self.framework_path}")
    
    def get_level(self, level_code: str) -> Optional[Dict[str, Any]]:
        """Get a specific level by code (e.g., 'L3')."""
        for level in self.framework.get('levels', []):
            if level.get('level') == level_code:
                return level
        return None
    
    def get_competencies_for_level(self, level_code: str) -> List[Dict[str, Any]]:
        """Get force-ranked competencies for a specific level."""
        level = self.get_level(level_code)
        if level:
            return level.get('competencies', [])
        return []
    
    def get_all_levels(self) -> List[Dict[str, Any]]:
        """Get all levels in the framework."""
        return self.framework.get('levels', [])
    
    def get_role_types_for_level(self, level_code: str) -> List[str]:
        """Get role types available for a specific level."""
        level = self.get_level(level_code)
        if level:
            return level.get('role_types', [])
        return []


class PMUserSignals:
    def __init__(self,
                 resume_text: str,
                 linkedIn_text: Optional[str] = None,
                 story_docs: Optional[List[str]] = None,
                 work_samples: Optional[List[WorkSample]] = None,
                 years_experience: Optional[int] = None,
                 titles: Optional[List[str]] = None,
                 org_size: Optional[str] = None,
                 team_leadership: Optional[bool] = None,
                 data_fluency_signal: Optional[bool] = None,
                 ml_experience_signal: Optional[bool] = None):
        self.resume_text = resume_text
        self.linkedIn_text = linkedIn_text
        self.story_docs = story_docs or []
        self.work_samples = work_samples or []
        self.years_experience = years_experience
        self.titles = titles or []
        self.org_size = org_size
        self.team_leadership = team_leadership
        self.data_fluency_signal = data_fluency_signal
        self.ml_experience_signal = ml_experience_signal


def _build_inference_prompt(signals: PMUserSignals, framework: PMLevelsFramework) -> str:
    """Build LLM prompt for PM inference using the framework."""
    
    # Get framework context
    levels_info = []
    for level in framework.get_all_levels():
        level_code = level['level']
        title = level['title']
        summary = level['summary']
        competencies = [comp['name'] for comp in level['competencies']]
        role_types = level['role_types']
        
        levels_info.append(f"""
Level {level_code} ({title}):
- Summary: {summary}
- Key Competencies: {', '.join(competencies)}
- Role Types: {', '.join(role_types)}
""")
    
    levels_text = '\n'.join(levels_info)
    
    # Build user signals summary
    signals_summary = f"""
User Profile:
- Years Experience: {signals.years_experience or 'Unknown'}
- Titles: {', '.join(signals.titles) if signals.titles else 'None provided'}
- Org Size: {signals.org_size or 'Unknown'}
- Team Leadership: {signals.team_leadership or 'Unknown'}
- Data Fluency: {signals.data_fluency_signal or 'Unknown'}
- ML Experience: {signals.ml_experience_signal or 'Unknown'}
- Work Samples: {len(signals.work_samples)} provided
- Story Documents: {len(signals.story_docs)} provided
"""

    prompt = f"""
You are an expert PM leveling specialist. Analyze the provided user data and PM levels framework to infer the user's most likely PM level, role type, and key competencies.

PM Levels Framework:
{levels_text}

User Data:
{signals_summary}

Resume Text (first 1000 chars):
{signals.resume_text[:1000]}

Work Samples:
{chr(10).join([f"- {sample.get('title', 'Unknown')}: {sample.get('description', 'No description')}" for sample in signals.work_samples[:3]])}

Story Documents:
{chr(10).join([f"- {doc[:200]}..." for doc in signals.story_docs[:2]])}

Based on this evidence, determine:
1. Most likely PM level (L2, L3, L4, or L5)
2. Most appropriate role type for this level
3. Top 3-5 competencies where the user shows strength
4. Any competency gaps that might indicate under-leveling

Respond in JSON format:
{{
    "level": "L3",
    "role_type": "growth",
    "archetype": "Settler (Growth)",
    "competencies": {{
        "product_strategy": "strong",
        "execution": "strong", 
        "data_driven_thinking": "moderate",
        "xfn_leadership": "moderate"
    }},
    "leverage_ratio": "high",
    "confidence": 0.85,
    "notes": "Strong signals from growth stories and cross-functional delivery. Some gaps in org-wide strategy suggest L3 rather than L4.",
    "gaps": ["org_wide_strategy", "systems_thinking"]
}}
"""
    return prompt


def infer_pm_profile(signals: PMUserSignals) -> PMInferenceResult:
    """
    Analyze user signals to infer PM role type, level, archetype, competencies, and leverage ratio.
    Uses the PM levels framework for evidence-based assessment.
    """
    # Load the PM levels framework
    framework = PMLevelsFramework()
    
    # Build and send LLM prompt
    prompt = _build_inference_prompt(signals, framework)
    
    try:
        response = call_openai(prompt, model="gpt-4", temperature=0.1)
        
        # Parse JSON response
        result = json.loads(response.strip())
        
        # Validate and structure the result
        return PMInferenceResult(
            role_type=result.get('role_type', 'generalist'),
            level=result.get('level', 'L3'),
            archetype=result.get('archetype', 'Generalist'),
            competencies=result.get('competencies', {}),
            leverage_ratio=result.get('leverage_ratio', 'medium'),
            notes=result.get('notes', ''),
            confidence=result.get('confidence', 0.5),
            gaps=result.get('gaps', [])
        )
        
    except Exception as e:
        # Fallback to basic inference based on years and titles
        print(f"LLM inference failed: {e}. Using fallback logic.")
        return _fallback_inference(signals)


def _fallback_inference(signals: PMUserSignals) -> PMInferenceResult:
    """Fallback inference logic when LLM fails."""
    
    # Simple heuristics based on years and titles
    years = signals.years_experience or 0
    titles = [t.lower() for t in (signals.titles or [])]
    
    if years >= 8 or any('director' in t or 'vp' in t or 'head' in t for t in titles):
        level = 'L5'
        role_type = 'platform'
    elif years >= 5 or any('senior' in t or 'staff' in t or 'principal' in t for t in titles):
        level = 'L4'
        role_type = 'growth'
    elif years >= 2 or any('product manager' in t for t in titles):
        level = 'L3'
        role_type = 'growth'
    else:
        level = 'L2'
        role_type = 'generalist'
    
    return PMInferenceResult(
        role_type=role_type,
        level=level,
        archetype=f"{role_type.title()} PM",
        competencies={
            'execution': 'strong',
            'collaboration': 'strong',
            'communication': 'moderate'
        },
        leverage_ratio='medium',
        notes=f'Fallback inference based on {years} years experience and titles: {titles}',
        confidence=0.3,
        gaps=[]
    )


def get_competency_gaps(user_level: str, target_level: str, framework: PMLevelsFramework) -> List[str]:
    """Identify competency gaps between user's current level and target level."""
    
    user_competencies = framework.get_competencies_for_level(user_level)
    target_competencies = framework.get_competencies_for_level(target_level)
    
    if not user_competencies or not target_competencies:
        return []
    
    user_comp_names = {comp['name'] for comp in user_competencies}
    target_comp_names = {comp['name'] for comp in target_competencies}
    
    # Find competencies in target level that aren't in user level
    gaps = target_comp_names - user_comp_names
    
    return list(gaps)


def get_prioritized_skills_for_job(level: str, role_type: str, framework: PMLevelsFramework) -> List[str]:
    """Get force-ranked skills for a specific level and role type."""
    
    level_data = framework.get_level(level)
    if not level_data:
        return []
    
    # Get competencies for this level, sorted by priority
    competencies = sorted(level_data.get('competencies', []), key=lambda x: x.get('priority', 999))
    
    # Filter by role type if specified
    if role_type and role_type in level_data.get('role_types', []):
        # Could add role-specific filtering logic here
        pass
    
    return [comp['name'] for comp in competencies] 