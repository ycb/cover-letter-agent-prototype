#!/usr/bin/env python3
"""
LLM-based Job Description Parser

Uses the PM levels framework to extract structured job information and match requirements
to competencies for better cover letter generation and job targeting.
"""

import json
import os
from typing import Dict, List, Optional, Any
from agents.pm_inference import PMLevelsFramework, call_openai


class JobParserLLM:
    """LLM-based job description parser with PM levels framework integration."""
    
    def __init__(self, framework_path: str = "data/pm_levels.yaml"):
        self.framework = PMLevelsFramework(framework_path)
    
    def parse_job_description(self, job_description: str) -> Dict[str, Any]:
        """
        Parse job description using LLM and PM levels framework.
        
        Returns structured data including:
        - company_name: Extracted company name
        - job_title: Extracted job title
        - inferred_level: PM level (L2-L5)
        - inferred_role_type: PM role type
        - key_requirements: Force-ranked list of key requirements
        - required_competencies: Mapped to PM framework competencies
        - company_info: Additional company context
        - job_context: Additional job context
        """
        
        prompt = self._build_job_parsing_prompt(job_description)
        
        try:
            response = call_openai(prompt, model="gpt-4", temperature=0.1)
            result = json.loads(response.strip())
            
            # Validate and enhance the result
            validated_result = self._validate_and_enhance_result(result, job_description)
            
            return validated_result
            
        except Exception as e:
            print(f"LLM job parsing failed: {e}. Using fallback parsing.")
            return self._fallback_parsing(job_description)
    
    def _build_job_parsing_prompt(self, job_description: str) -> str:
        """Build LLM prompt for job parsing with PM levels framework."""
        
        # Get framework context for levels and competencies
        levels_info = []
        for level in self.framework.get_all_levels():
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
        
        prompt = f"""
You are an expert job description analyzer specializing in product management roles. Analyze the provided job description and extract structured information using the PM levels framework.

PM Levels Framework:
{levels_text}

Job Description:
\"\"\"
{job_description}
\"\"\"

Extract and structure the following information:

1. Company Name: Extract the hiring company name
2. Job Title: Extract the exact job title
3. Inferred PM Level: Based on scope, requirements, and seniority indicators, determine if this is L2, L3, L4, or L5
4. Inferred Role Type: Determine the most likely PM role type (growth, platform, ai_ml, generalist, etc.)
5. Key Requirements: Extract the top 5-8 most important requirements/skills
6. Required Competencies: Map requirements to PM framework competencies
7. Company Context: Extract company size, stage, industry, business model
8. Job Context: Extract team size, reporting structure, key stakeholders

Disregard any information that is irrelevant such as:
- Content copied from source pages
- Content overlaid by third-party job application tools
- Generic boilerplate text
- Unrelated job postings or ads

Respond in JSON format:
{{
    "company_name": "Example Corp",
    "job_title": "Senior Product Manager",
    "inferred_level": "L3",
    "inferred_role_type": "growth",
    "key_requirements": [
        "5+ years product management experience",
        "Experience with A/B testing and data analysis",
        "Cross-functional leadership skills",
        "Experience with growth metrics and KPIs"
    ],
    "required_competencies": {{
        "product_strategy": "required",
        "data_driven_thinking": "required",
        "xfn_leadership": "required",
        "execution_at_scale": "preferred"
    }},
    "company_info": {{
        "size": "500-1000 employees",
        "stage": "Series C",
        "industry": "SaaS",
        "business_model": "B2B"
    }},
    "job_context": {{
        "team_size": "8-12 people",
        "reporting_to": "Director of Product",
        "key_stakeholders": ["Engineering", "Design", "Marketing"]
    }},
    "confidence": 0.85,
    "notes": "Strong signals for L3 growth PM role with emphasis on data-driven decision making"
}}
"""
        return prompt
    
    def _validate_and_enhance_result(self, result: Dict[str, Any], original_jd: str) -> Dict[str, Any]:
        """Validate and enhance the LLM parsing result."""
        
        # Ensure required fields exist
        required_fields = ['company_name', 'job_title', 'inferred_level', 'inferred_role_type']
        for field in required_fields:
            if field not in result:
                result[field] = 'Unknown'
        
        # Validate inferred level
        valid_levels = ['L2', 'L3', 'L4', 'L5']
        if result.get('inferred_level') not in valid_levels:
            result['inferred_level'] = 'L3'  # Default to L3
        
        # Get prioritized skills for this level/role
        level = result.get('inferred_level', 'L3')
        role_type = result.get('inferred_role_type', 'generalist')
        
        prioritized_skills = self.framework.get_competencies_for_level(level)
        result['prioritized_skills'] = [comp['name'] for comp in prioritized_skills]
        
        # Add framework context
        level_data = self.framework.get_level(level)
        if level_data:
            result['level_summary'] = level_data.get('summary', '')
            result['level_competencies'] = [comp['name'] for comp in level_data.get('competencies', [])]
        
        return result
    
    def _fallback_parsing(self, job_description: str) -> Dict[str, Any]:
        """Fallback parsing when LLM fails."""
        
        # Simple regex-based extraction (basic fallback)
        import re
        
        # Extract company name (look for common patterns)
        company_patterns = [
            r'at\s+([A-Z][a-zA-Z\s&]+?)(?:\s+in|\s+is|\s+seeks|\s+looking)',
            r'([A-Z][a-zA-Z\s&]+?)\s+is\s+seeking',
            r'([A-Z][a-zA-Z\s&]+?)\s+looking\s+for'
        ]
        
        company_name = 'Unknown'
        for pattern in company_patterns:
            match = re.search(pattern, job_description, re.IGNORECASE)
            if match:
                company_name = match.group(1).strip()
                break
        
        # Extract job title
        title_patterns = [
            r'(Senior\s+)?Product\s+Manager',
            r'(Senior\s+)?Product\s+Director',
            r'Head\s+of\s+Product'
        ]
        
        job_title = 'Product Manager'
        for pattern in title_patterns:
            match = re.search(pattern, job_description, re.IGNORECASE)
            if match:
                job_title = match.group(0)
                break
        
        return {
            'company_name': company_name,
            'job_title': job_title,
            'inferred_level': 'L3',
            'inferred_role_type': 'generalist',
            'key_requirements': ['Product management experience', 'Cross-functional collaboration'],
            'required_competencies': {'execution': 'required', 'collaboration': 'required'},
            'company_info': {'size': 'Unknown', 'stage': 'Unknown', 'industry': 'Unknown'},
            'job_context': {'team_size': 'Unknown', 'reporting_to': 'Unknown'},
            'prioritized_skills': ['product_strategy', 'xfn_leadership', 'execution_at_scale'],
            'confidence': 0.3,
            'notes': 'Fallback parsing used due to LLM failure'
        }
    
    def match_requirements_to_competencies(self, requirements: List[str], target_level: str) -> Dict[str, str]:
        """Match job requirements to PM framework competencies."""
        
        # Get competencies for the target level
        level_competencies = self.framework.get_competencies_for_level(target_level)
        competency_names = [comp['name'] for comp in level_competencies]
        
        # Simple keyword matching (could be enhanced with LLM)
        matches = {}
        
        for req in requirements:
            req_lower = req.lower()
            
            # Map requirements to competencies
            if any(word in req_lower for word in ['strategy', 'roadmap', 'vision']):
                matches['product_strategy'] = 'required'
            elif any(word in req_lower for word in ['leadership', 'team', 'cross-functional']):
                matches['xfn_leadership'] = 'required'
            elif any(word in req_lower for word in ['data', 'analytics', 'metrics', 'kpi']):
                matches['data_driven_thinking'] = 'required'
            elif any(word in req_lower for word in ['execution', 'delivery', 'launch']):
                matches['execution_at_scale'] = 'required'
            elif any(word in req_lower for word in ['communication', 'presentation', 'stakeholder']):
                matches['communication_influence'] = 'required'
        
        return matches


def parse_job_with_llm(job_description: str) -> Dict[str, Any]:
    """Convenience function to parse job description with LLM."""
    parser = JobParserLLM()
    return parser.parse_job_description(job_description)


if __name__ == "__main__":
    # Test the job parser
    test_jd = """
    Duke Energy is seeking a Senior Product Manager to join our growing team.
    
    We are looking for someone with:
    - 5+ years of product management experience
    - Experience leading cross-functional teams
    - Strong data analysis and A/B testing skills
    - Experience with growth metrics and KPIs
    - Excellent communication and stakeholder management skills
    
    The ideal candidate will:
    - Define product strategy and roadmap
    - Lead engineering and design teams
    - Conduct market research and competitive analysis
    - Drive product launches and measure success
    """
    
    result = parse_job_with_llm(test_jd)
    print("Job Parsing Result:")
    print(json.dumps(result, indent=2)) 