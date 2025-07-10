#!/usr/bin/env python3
"""
Cover Letter Agent
=================

An intelligent agent that generates customized cover letters using structured
blurb modules and logic-based scoring systems.
"""

import yaml
import re
import csv
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import logging
import os
# Add language_tool_python for grammar/spell check
try:
    import language_tool_python
    TOOL_AVAILABLE = True
except ImportError:
    TOOL_AVAILABLE = False
import sys
import collections

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class JobTargeting:
    """Represents job targeting criteria and evaluation results."""
    title_match: bool = False
    title_category: str = ""  # leadership or IC
    comp_match: bool = False
    location_match: bool = False
    location_type: str = ""  # preferred or open_to
    role_type_matches: List[str] = field(default_factory=list)
    company_stage_match: bool = False
    business_model_match: bool = False
    targeting_score: float = 0.0
    targeting_go_no_go: bool = False


@dataclass
class JobDescription:
    """Represents a parsed job description with extracted information."""
    raw_text: str
    company_name: str
    job_title: str
    keywords: List[str]
    job_type: str
    score: float
    go_no_go: bool
    extracted_info: Dict[str, Any]
    targeting: Optional[JobTargeting] = None


@dataclass
class BlurbMatch:
    """Represents a blurb with its match score and metadata."""
    blurb_id: str
    blurb_type: str
    text: str
    tags: List[str]
    score: float
    selected: bool = False


@dataclass
class EnhancementSuggestion:
    """Represents an enhancement suggestion for the cover letter."""
    timestamp: str
    job_id: str
    enhancement_type: str
    category: str
    description: str
    status: str  # open, accepted, rejected
    priority: str  # high, medium, low
    notes: str = ""


class CoverLetterAgent:
    """Main agent class for generating customized cover letters."""
    
    def __init__(self, user_id: str = None, data_dir: str = "data"):
        """Initialize the agent with user context or data directory."""
        if user_id:
            # Multi-user mode
            from core.user_context import UserContext
            self.user_context = UserContext(user_id)
            self.data_dir = self.user_context.user_dir
            self.blurbs = self.user_context.blurbs
            self.logic = self.user_context.logic
            self.enhancement_log = self.user_context.load_enhancement_log()
            self.targeting = self.user_context.targeting
            self.config = self.user_context.config
            self.google_drive = self._initialize_google_drive()
            self.context_analyzer = self._initialize_context_analyzer()
            self.resume = self._load_resume()
        else:
            # Legacy mode
            self.data_dir = Path(data_dir)
            self.blurbs = self._load_blurbs()
            self.logic = self._load_logic()
            self.enhancement_log = self._load_enhancement_log()
            self.targeting = self._load_targeting()
            self.config = self._load_config()
            self.google_drive = self._initialize_google_drive()
            self.context_analyzer = self._initialize_context_analyzer()
            self.resume = self._load_resume()
    
    def _load_blurbs(self) -> Dict[str, List[Dict]]:
        """Load blurbs from YAML file."""
        blurbs_path = self.data_dir / "blurbs.yaml"
        with open(blurbs_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _load_logic(self) -> Dict[str, Any]:
        """Load blurb logic from YAML file."""
        logic_path = self.data_dir / "blurb_logic.yaml"
        with open(logic_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _load_enhancement_log(self) -> List[Dict]:
        """Load enhancement log from CSV file."""
        log_path = self.data_dir / "enhancement_log.csv"
        if not log_path.exists():
            return []
        
        with open(log_path, 'r') as f:
            reader = csv.DictReader(f)
            return list(reader)
    
    def _save_enhancement_log(self):
        """Save enhancement log to CSV file."""
        if hasattr(self, 'user_context'):
            # Multi-user mode
            self.user_context.save_enhancement_log(self.enhancement_log)
        else:
            # Legacy mode
            log_path = self.data_dir / "enhancement_log.csv"
            if not self.enhancement_log:
                return
            
            fieldnames = self.enhancement_log[0].keys()
            with open(log_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.enhancement_log)
    
    def _load_targeting(self) -> Dict[str, Any]:
        """Load job targeting config from YAML file."""
        targeting_path = self.data_dir / "job_targeting.yaml"
        if targeting_path.exists():
            with open(targeting_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def _load_config(self) -> Dict[str, Any]:
        """Load agent configuration from YAML file."""
        config_path = self.data_dir / "agent_config.yaml"
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def _initialize_google_drive(self):
        """Initialize Google Drive integration if enabled."""
        if not self.config.get('google_drive', {}).get('enabled', False):
            return None
        
        try:
            from google_drive_integration import GoogleDriveIntegration
            
            gd_config = self.config['google_drive']
            credentials_file = gd_config.get('credentials_file', 'credentials.json')
            folder_id = gd_config.get('folder_id', '')
            
            return GoogleDriveIntegration(credentials_file, folder_id)
            
        except ImportError:
            logger.warning("Google Drive integration not available. Install required packages.")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize Google Drive: {e}")
            return None
    
    def _initialize_context_analyzer(self):
        """Initialize the context analyzer."""
        try:
            from context_analyzer import ContextAnalyzer
            return ContextAnalyzer()
        except ImportError:
            logger.warning("Context analyzer not available")
            return None
    
    def _initialize_resume_parser(self):
        """Initialize the resume parser."""
        try:
            from resume_parser import ResumeParser
            return ResumeParser()
        except ImportError:
            logger.warning("Resume parser not available")
            return None
    
    def _load_resume(self):
        """Load and parse the resume."""
        if not self.config.get('profile', {}).get('resume_file'):
            return None
        
        resume_parser = self._initialize_resume_parser()
        if not resume_parser:
            return None
        
        resume_file = self.config['profile']['resume_file']
        resume_path = Path(resume_file)
        
        if not resume_path.exists():
            logger.warning(f"Resume file not found: {resume_file}")
            return None
        
        try:
            parsed_resume = resume_parser.parse_resume(str(resume_path))
            logger.info(f"Resume parsed successfully: {parsed_resume.name}")
            return parsed_resume
        except Exception as e:
            logger.error(f"Error parsing resume: {e}")
            return None
    
    def analyze_contextual_data(self, job_description: str) -> Dict[str, Any]:
        """Analyze contextual data to inform cover letter strategy."""
        if not self.context_analyzer:
            return {}
        
        analysis = {
            'achievements': [],
            'past_cover_letters': [],
            'strategic_insights': [],
            'recommended_achievements': [],
            'tone_recommendation': None,
            'resume_data': {}
        }
        
        # Extract achievements from case studies
        case_studies = self.get_case_studies(job_description.split())
        for case_study in case_studies:
            if case_study['type'] == 'file' and case_study.get('file_path'):
                try:
                    with open(case_study['file_path'], 'r') as f:
                        content = f.read()
                        achievements = self.context_analyzer.extract_achievements_from_text(
                            content, case_study.get('company', ''), case_study.get('role', ''), case_study.get('year', '')
                        )
                        analysis['achievements'].extend(achievements)
                except Exception as e:
                    logger.warning(f"Could not read case study file {case_study['file_path']}: {e}")
        
        # Analyze resume data if available
        if self.resume:
            resume_parser = self._initialize_resume_parser()
            if resume_parser:
                job_keywords = job_description.split()
                relevant_experience = resume_parser.get_relevant_experience(self.resume, job_keywords)
                relevant_skills = resume_parser.get_relevant_skills(self.resume, job_keywords)
                resume_summary = resume_parser.get_resume_summary(self.resume)
                
                analysis['resume_data'] = {
                    'name': self.resume.name,
                    'email': self.resume.email,
                    'location': self.resume.location,
                    'summary': self.resume.summary,
                    'relevant_experience': relevant_experience,
                    'relevant_skills': relevant_skills,
                    'resume_summary': resume_summary,
                    'all_experience': self.resume.experience,
                    'all_skills': self.resume.skills,
                    'achievements': self.resume.achievements
                }
        
        # Analyze past cover letters if available
        past_cover_letters = self._load_past_cover_letters()
        analysis['past_cover_letters'] = past_cover_letters
        
        # Generate strategic insights
        if self.context_analyzer:
            analysis['strategic_insights'] = self.context_analyzer.generate_strategic_insights(
                job_description, analysis['achievements'], past_cover_letters
            )
            
            # Find recommended achievements
            job_keywords = self.context_analyzer._extract_job_keywords(job_description)
            analysis['recommended_achievements'] = self.context_analyzer._find_relevant_achievements(
                analysis['achievements'], job_keywords
            )
            
            # Get tone recommendation
            tone_insight = next((insight for insight in analysis['strategic_insights'] 
                               if insight.insight_type == 'tone'), None)
            if tone_insight:
                analysis['tone_recommendation'] = tone_insight.recommended_action
        
        return analysis
    
    def _load_past_cover_letters(self) -> List:
        """Load and analyze past cover letters."""
        past_letters = []
        
        # Load from Google Drive if available
        if self.google_drive and self.google_drive.available:
            gd_materials = self.google_drive.get_supporting_materials(
                self.config.get('google_drive', {}).get('materials', {})
            )
            
            cover_letters = gd_materials.get('cover_letters', [])
            for letter in cover_letters:
                # Download and analyze the cover letter
                local_path = f"materials/cover_letters/{letter['name']}"
                if self.google_drive.download_file(letter['id'], local_path):
                    try:
                        with open(local_path, 'r') as f:
                            content = f.read()
                            # Extract metadata from filename or content
                            company, position, date = self._extract_letter_metadata(letter['name'])
                            analyzed_letter = self.context_analyzer.analyze_past_cover_letter(
                                content, company, position, date
                            )
                            past_letters.append(analyzed_letter)
                    except Exception as e:
                        logger.warning(f"Could not analyze cover letter {letter['name']}: {e}")
        
        return past_letters
    
    def _extract_letter_metadata(self, filename: str) -> Tuple[str, str, str]:
        """Extract company, position, and date from filename."""
        # Expected format: company_position_date.txt
        parts = filename.replace('.txt', '').split('_')
        if len(parts) >= 3:
            company = parts[0]
            position = parts[1]
            date = parts[2]
        else:
            company = "Unknown"
            position = "Unknown"
            date = "Unknown"
        
        return company, position, date
    
    def generate_enhanced_cover_letter(self, job: JobDescription, selected_blurbs: Dict[str, BlurbMatch], contextual_analysis: Dict[str, Any], missing_requirements: List[str] = None) -> str:
        """Generate an enhanced cover letter using contextual insights and fill gaps with role_specific_alignment blurbs."""
        if missing_requirements is None:
            missing_requirements = []
        # Start with base cover letter
        cover_letter = self.generate_cover_letter(job, selected_blurbs, missing_requirements)
        
        # Apply strategic insights
        if contextual_analysis.get('strategic_insights'):
            cover_letter = self._apply_strategic_insights(cover_letter, contextual_analysis['strategic_insights'])
        
        # Include resume-based achievements and experience
        if contextual_analysis.get('resume_data'):
            cover_letter = self._include_resume_data(cover_letter, contextual_analysis['resume_data'])
        
        # Include recommended achievements
        if contextual_analysis.get('recommended_achievements'):
            cover_letter = self._include_recommended_achievements(cover_letter, contextual_analysis['recommended_achievements'])
        
        # Adjust tone based on recommendation
        if contextual_analysis.get('tone_recommendation'):
            cover_letter = self._adjust_tone(cover_letter, contextual_analysis['tone_recommendation'])
        
        return cover_letter
    
    def _apply_strategic_insights(self, cover_letter: str, insights: List) -> str:
        """Apply strategic insights to the cover letter."""
        # For now, just log the insights
        for insight in insights:
            logger.info(f"Strategic insight: {insight.description}")
            logger.info(f"Recommended action: {insight.recommended_action}")
        
        return cover_letter
    
    def _include_recommended_achievements(self, cover_letter: str, achievements: List) -> str:
        """Include recommended achievements in the cover letter."""
        if not achievements:
            return cover_letter
        
        # Find a good place to insert achievements (after the main paragraph)
        lines = cover_letter.split('\n')
        insert_index = -1
        
        for i, line in enumerate(lines):
            if 'At Meta' in line or 'At Aurora' in line:
                insert_index = i + 1
                break
        
        if insert_index == -1:
            # Insert before the closing paragraph
            for i, line in enumerate(lines):
                if 'I\'m excited about' in line:
                    insert_index = i
                    break
        
        if insert_index > 0:
            # Add achievement paragraph
            achievement_text = "\n"
            for achievement in achievements[:2]:  # Limit to 2 achievements
                achievement_text += f"At {achievement.company}, {achievement.description}\n"
            achievement_text += "\n"
            
            lines.insert(insert_index, achievement_text)
        
        return '\n'.join(lines)
    
    def _include_resume_data(self, cover_letter: str, resume_data: Dict[str, Any]) -> str:
        """Include resume-based data in the cover letter."""
        lines = cover_letter.split('\n')
        
        # Add relevant experience highlights
        if resume_data.get('relevant_experience'):
            experience_text = "\n".join([
                f"• {exp.title} at {exp.company} ({exp.duration})" 
                for exp in resume_data['relevant_experience'][:2]
            ])
            
            # Find a good place to insert (after main paragraph)
            insert_index = -1
            for i, line in enumerate(lines):
                if 'At Meta' in line or 'At Aurora' in line or 'I have' in line:
                    insert_index = i + 1
                    break
            
            if insert_index > 0:
                lines.insert(insert_index, f"\nRelevant Experience:\n{experience_text}\n")
        
        # Add relevant skills
        if resume_data.get('relevant_skills'):
            skills_text = ", ".join([skill.name for skill in resume_data['relevant_skills'][:5]])
            
            # Find place to insert skills
            insert_index = -1
            for i, line in enumerate(lines):
                if 'skills' in line.lower() or 'technologies' in line.lower():
                    insert_index = i + 1
                    break
            
            if insert_index > 0:
                lines.insert(insert_index, f"Key Skills: {skills_text}\n")
        
        # Add resume achievements
        if resume_data.get('achievements'):
            achievements_text = "\n".join([f"• {achievement}" for achievement in resume_data['achievements'][:3]])
            
            # Find place to insert achievements
            insert_index = -1
            for i, line in enumerate(lines):
                if 'achievements' in line.lower() or 'accomplishments' in line.lower():
                    insert_index = i + 1
                    break
            
            if insert_index > 0:
                lines.insert(insert_index, f"\nKey Achievements:\n{achievements_text}\n")
        
        return '\n'.join(lines)
    
    def _adjust_tone(self, cover_letter: str, tone_recommendation: str) -> str:
        """Adjust the tone of the cover letter based on recommendation."""
        # Simple tone adjustments
        if 'conversational' in tone_recommendation.lower():
            # Make more conversational
            cover_letter = cover_letter.replace('I am', "I'm")
            cover_letter = cover_letter.replace('I would', "I'd")
        elif 'professional' in tone_recommendation.lower():
            # Make more professional
            cover_letter = cover_letter.replace("I'm", 'I am')
            cover_letter = cover_letter.replace("I'd", 'I would')
        
        return cover_letter
    
    def get_case_studies(self, job_keywords: List[str] = None, force_include: list = None) -> List[Dict]:
        """Dynamically select relevant case studies from blurbs.yaml based on job tags and blurb_logic.yaml rules. Strongly weight maturity, business model, and role type tags."""
        import collections
        if job_keywords is None:
            job_keywords = []
        if force_include is None:
            force_include = []
        # Tag categories for strong weighting
        maturity_tags = {'public', 'startup', 'scaleup', 'pilot', 'prototype'}
        business_model_tags = {'b2b', 'b2c', 'b2b2c', 'd2c', 'consumer', 'smb', 'enterprise'}
        role_type_tags = {'growth', 'leadership', 'founding_pm', 'platform', 'ux', 'ai_ml'}
        key_skill_tags = {'data', 'analytics', 'metrics', 'execution', 'strategy', 'discovery', 'customer discovery', 'user research'}
        industry_tags = ['technology', 'healthcare', 'finance', 'education', 'energy', 'retail']
        # Load case studies from blurbs.yaml (examples section)
        case_studies = self.blurbs.get('examples', [])
        # Load min_score and selection rules from blurb_logic.yaml
        logic = self.logic.get('examples', {})
        selection_rules = self.logic.get('case_study_selection', {}).get('rules', [])
        # Compute relevance score for each case study
        scored = []
        job_kw_set = set([kw.lower() for kw in job_keywords])
        for cs in case_studies:
            score = 0
            tag_matches = set()
            for tag in cs.get('tags', []):
                if tag.lower() in [kw.lower() for kw in job_keywords]:
                    # Strong weighting for certain tag categories
                    if tag.lower() in maturity_tags or tag.lower() in business_model_tags or tag.lower() in role_type_tags:
                        score += 3
                    elif tag.lower() in key_skill_tags or tag.lower() in industry_tags:
                        score += 1
                    tag_matches.add(tag.lower())
            # Penalty for B2B-only if B2C/consumer present in JD
            if 'b2b' in cs.get('tags', []) and ('b2c' in job_keywords or 'consumer' in job_keywords):
                score -= 2
            # Bonus for Enact if B2C/consumer + leadership + startup in JD
            if cs['id'] == 'enact' and all(t in job_keywords for t in ['b2c', 'consumer', 'leadership', 'startup']):
                score += 3
            scored.append((cs, score, cs.get('id', 'unknown')))
        # DEBUG: Print scores for all case studies
        print("[DEBUG] Case study scores:")
        for cs, score, csid in scored:
            print(f"  {csid}: {score}")
        # Get min_scores from logic
        logic = self.config.get('blurb_logic', {}).get('minimum_scores', {}).get('examples', {})
        # Filter by min_score (convert to float)
        eligible = []
        for cs, score, csid in scored:
            min_score = float(logic.get(csid, {}).get('min_score', 0))
            if score >= min_score or cs['id'] in force_include:
                eligible.append((cs, score, min_score))
        # Sort by score descending
        eligible.sort(key=lambda x: x[1], reverse=True)
        # Prioritize diversity: prefer different industries/skills (simple: unique tag sets)
        samsung_ids = {'samsung', 'samsung_chatbot'}
        selected = []
        used_tags = set()
        samsung_selected = False
        print("[DEBUG] Selection process:")
        for cs, score, min_score in eligible:
            print(f"  Considering {cs['id']} (score: {score}, min_score: {min_score})")
            # Samsung logic: only one allowed
            if cs['id'] in samsung_ids:
                if samsung_selected:
                    print(f"    Skipping {cs['id']} - Samsung already selected")
                    continue
                # Prefer chatbot for AI/ML, NLP, or customer success
                if cs['id'] == 'samsung_chatbot' and any(tag in job_keywords for tag in ['ai_ml', 'nlp', 'customer_success']):
                    print(f"    Selecting {cs['id']} - preferred for AI/ML/NLP")
                    selected.append(cs)
                    samsung_selected = True
                elif cs['id'] == 'samsung' and not any(tag in job_keywords for tag in ['ai_ml', 'nlp', 'customer_success']):
                    print(f"    Selecting {cs['id']} - preferred for non-AI/ML")
                    selected.append(cs)
                    samsung_selected = True
                else:
                    print(f"    Selecting {cs['id']} - first Samsung found")
                    selected.append(cs)
                    samsung_selected = True
            else:
                print(f"    Selecting {cs['id']} - non-Samsung")
                selected.append(cs)
            if len(selected) >= 3:
                print(f"    Reached 3 case studies, stopping")
                break
        print(f"[DEBUG] Final selection: {[cs['id'] for cs in selected]}")
        # If user forced specific examples, ensure they're included
        for fid in force_include:
            if not any(cs['id'] == fid for cs in selected):
                for cs, score, min_score in eligible:
                    if cs['id'] == fid:
                        selected.append(cs)
                        break
        # Add 'name', 'description', and 'type' fields for compatibility
        for cs in selected:
            if 'name' not in cs:
                cs['name'] = cs['id'].capitalize()
            if 'description' not in cs:
                cs['description'] = cs['text'].split('.')[0].strip()
            if 'type' not in cs:
                cs['type'] = 'blurb'
        return selected
    
    def download_case_study_materials(self, case_studies: List[Dict], local_dir: str = "materials") -> List[str]:
        """Download case study materials to local directory."""
        downloaded_files = []
        
        if not self.google_drive or not self.google_drive.available:
            return downloaded_files
        
        for case_study in case_studies:
            if case_study['type'] == 'google_drive':
                local_path = os.path.join(local_dir, case_study['material_type'], case_study['name'])
                
                if self.google_drive.download_file(case_study['file_id'], local_path):
                    downloaded_files.append(local_path)
        
        return downloaded_files
    
    def parse_job_description(self, job_text: str) -> JobDescription:
        """Parse and analyze a job description."""
        logger.info("Parsing job description...")
        
        # Extract basic information
        company_name = self._extract_company_name(job_text)
        job_title = self._extract_job_title(job_text)
        keywords = self._extract_keywords(job_text)
        job_type = self._classify_job_type(job_text)
        
        # Calculate score
        score = self._calculate_job_score(job_text, keywords)
        
        # Determine go/no-go
        go_no_go = self._evaluate_go_no_go(job_text, keywords, score)
        
        # Extract additional information
        extracted_info = {
            'requirements': self._extract_requirements(job_text),
            'responsibilities': self._extract_responsibilities(job_text),
            'company_info': self._extract_company_info(job_text),
        }
        
        # Evaluate job targeting
        targeting = self._evaluate_job_targeting(job_text, job_title, extracted_info)
        
        return JobDescription(
            raw_text=job_text,
            company_name=company_name,
            job_title=job_title,
            keywords=keywords,
            job_type=job_type,
            score=score,
            go_no_go=go_no_go,
            extracted_info=extracted_info,
            targeting=targeting
        )
    
    def _extract_company_name(self, text: str) -> str:
        """Robust, multi-pass extraction of company name from job description."""
        import re, collections
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        # 1. Ignore 'About the job', use 'About <Name>' if present
        for line in lines:
            if line.lower().startswith('about ') and line.lower() != 'about the job':
                company = line[6:].strip()
                print(f"[DEBUG] Extracted company name from 'About': {company}")
                return company
        # 2. First non-empty, single capitalized word line
        for line in lines:
            if line.isalpha() and line[0].isupper() and len(line.split()) == 1:
                print(f"[DEBUG] Extracted company name from first capitalized line: {line}")
                return line
        # 3. Most frequent capitalized word in the JD
        words = re.findall(r'\b[A-Z][a-zA-Z0-9&]+\b', text)
        if words:
            most_common = collections.Counter(words).most_common(1)[0][0]
            print(f"[DEBUG] Extracted company name from most frequent capitalized word: {most_common}")
            return most_common
        # 4. Possessive or 'the Name team'
        for line in lines:
            match = re.match(r"([A-Z][a-zA-Z0-9& ]+)'s ", line)
            if match:
                company = match.group(1).strip()
                print(f"[DEBUG] Extracted company name from possessive: {company}")
                return company
            match = re.match(r'the ([A-Z][a-zA-Z0-9& ]+) team', line, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                print(f"[DEBUG] Extracted company name from 'the Name team': {company}")
                return company
        # 5. Not found
        print("[DEBUG] Company name not found in JD.")
        return ""
    
    def _extract_job_title(self, text: str) -> str:
        """Extract job title from job description."""
        # Look for "As a [Title] at" or "As a [Title]," pattern first
        as_pattern = r'As\s+a[n]?\s+([A-Z][a-zA-Z\s]+?)(?:\s+at|,|\.|\n)'
        match = re.search(as_pattern, text, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            # Remove trailing generic words
            title = re.sub(r'\s+(at|for|with|in|on|of)\b.*$', '', title)
            # Normalize to common titles
            if 'product manager' in title.lower():
                return 'Product Manager'
            if 'pm' == title.lower().strip():
                return 'Product Manager'
            return title
        # Fallback to common job title patterns
        patterns = [
            r'(?:Senior\s+)?(?:Product\s+)?(?:Manager|Lead|Director|VP)',
            r'(?:Senior\s+)?(?:Software\s+)?(?:Engineer|Developer)',
            r'(?:Data\s+)?(?:Scientist|Analyst)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                found = match.group(0).strip()
                if 'product manager' in found.lower():
                    return 'Product Manager'
                return found
        return "Product Manager"  # Default fallback for this use case
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords and implied tags from job description, including synonyms for maturity, business model, and role type."""
        import re
        keywords = set()
        text_lower = text.lower()
        # Direct keyword extraction (existing logic)
        direct_keywords = re.findall(r'\b[a-zA-Z0-9_\-/]+\b', text_lower)
        keywords.update(direct_keywords)
        # Synonym and implied tag mapping
        synonym_map = {
            # Maturity
            'public company': 'public',
            'ipo': 'public',
            'fortune 500': 'public',
            'startup': 'startup',
            'scaleup': 'scaleup',
            'pilot': 'pilot',
            'prototype': 'prototype',
            # Business Model
            'consumer': 'consumer',
            'personal finance': 'consumer',
            'b2c': 'b2c',
            'b2b': 'b2b',
            'b2b2c': 'b2b2c',
            'd2c': 'd2c',
            'smb': 'smb',
            'small business': 'smb',
            'enterprise': 'b2b',
            # Role Type
            'growth': 'growth',
            'leadership': 'leadership',
            'team lead': 'leadership',
            'manager': 'leadership',
            'founding pm': 'founding_pm',
            'founder': 'founding_pm',
            'platform': 'platform',
            'ux': 'ux',
            'user experience': 'ux',
            'ai/ml': 'ai_ml',
            'ai': 'ai_ml',
            'ml': 'ai_ml',
            # Key Skills
            'data': 'data_driven',
            'analytics': 'data_driven',
            'metrics': 'data_driven',
            'execution': 'execution',
            'strategy': 'strategy',
            'discovery': 'discovery',
            'customer discovery': 'discovery',
            'user research': 'discovery',
        }
        for phrase, tag in synonym_map.items():
            if phrase in text_lower:
                keywords.add(tag)
        # Implied tags for Quicken/finance
        if 'quicken' in text_lower or 'personal finance' in text_lower:
            keywords.update(['public', 'consumer', 'b2c', 'smb', 'data_driven'])
        return list(set(keywords))
    
    def _classify_job_type(self, text: str) -> str:
        """Classify the job type based on keywords."""
        text_lower = text.lower()
        
        for job_type, config in self.logic['job_classification'].items():
            keyword_count = sum(1 for keyword in config['keywords'] 
                              if keyword.lower() in text_lower)
            if keyword_count >= config['min_keyword_count']:
                return job_type
        
        return "general"
    
    def _calculate_job_score(self, text: str, keywords: List[str]) -> float:
        """Calculate a score for the job based on keywords and content."""
        score = 0.0
        
        # Add scores for keywords
        keyword_weights = self.logic['scoring_rules']['keyword_weights']
        for keyword in keywords:
            if keyword in keyword_weights:
                score += keyword_weights[keyword]
        
        # Add scores for strong match keywords
        strong_match_keywords = self.logic['go_no_go']['strong_match_keywords']
        for keyword in keywords:
            if keyword in strong_match_keywords:
                score += 2.0
        
        # Subtract scores for poor match keywords
        poor_match_keywords = self.logic['go_no_go']['poor_match_keywords']
        for keyword in keywords:
            if keyword in poor_match_keywords:
                score -= 1.0
        
        return score
    
    def _evaluate_go_no_go(self, text: str, keywords: List[str], score: float) -> bool:
        """Evaluate whether to proceed with cover letter generation."""
        # Check minimum keywords
        if len(keywords) < self.logic['go_no_go']['minimum_keywords']:
            return False
        
        # Check minimum score
        if score < self.logic['go_no_go']['minimum_total_score']:
            return False
        
        return True
    
    def _extract_requirements(self, text: str) -> List[str]:
        """Extract job requirements from text."""
        # Simple extraction - look for requirement patterns
        requirements = []
        lines = text.split('\n')
        
        for line in lines:
            if re.search(r'(?:requirements?|qualifications?|must|should)', line, re.IGNORECASE):
                requirements.append(line.strip())
        
        return requirements
    
    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract job responsibilities from text."""
        # Simple extraction - look for responsibility patterns
        responsibilities = []
        lines = text.split('\n')
        
        for line in lines:
            if re.search(r'(?:responsibilities?|duties?|will|you\s+will)', line, re.IGNORECASE):
                responsibilities.append(line.strip())
        
        return responsibilities
    
    def _extract_company_info(self, text: str) -> Dict[str, str]:
        """Extract company information from text."""
        info = {}
        
        # Look for company size
        size_patterns = [
            r'(\d+)\s*-\s*(\d+)\s+employees',
            r'(\d+)\+?\s+employees',
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['company_size'] = match.group(0)
                break
        
        # Look for industry
        industries = ['technology', 'healthcare', 'finance', 'education', 'energy', 'retail']
        for industry in industries:
            if industry in text.lower():
                info['industry'] = industry
                break
        
        return info
    
    def _evaluate_job_targeting(self, job_text: str, job_title: str, extracted_info: Dict[str, Any]) -> JobTargeting:
        """Evaluate job against targeting criteria from job_targeting.yaml."""
        if not self.targeting:
            return JobTargeting()
        t = self.targeting
        weights = t.get('scoring_weights', {})
        min_scores = t.get('minimum_scores', {})
        keywords = t.get('keywords', {})
        score = 0.0
        
        # Title match - IMPROVED: More flexible matching
        title_match = False
        title_category = ""
        job_title_lower = job_title.lower()
        
        # Check for exact matches first
        for cat, titles in t.get('target_titles', {}).items():
            for title in titles:
                if title.lower() in job_title_lower:
                    title_match = True
                    title_category = cat
                    score += weights.get('title_match', 5.0)
                    break
        
        # If no exact match, check for partial matches (e.g., "Product Manager" matches "Senior Product Manager")
        if not title_match:
            for cat, titles in t.get('target_titles', {}).items():
                for title in titles:
                    title_words = title.lower().split()
                    job_words = job_title_lower.split()
                    # Check if any target title words are in job title
                    if any(word in job_words for word in title_words):
                        title_match = True
                        title_category = cat
                        score += weights.get('title_match', 3.0)  # Lower score for partial match
                        break
        
        # PATCH: Force leadership for 'Group Product Manager' or similar
        if 'group product manager' in job_title_lower:
            title_category = 'leadership'
        # PATCH: If responsibilities mention manage/mentor, force leadership
        responsibilities = extracted_info.get('responsibilities', [])
        if any('manage' in r.lower() or 'mentor' in r.lower() for r in responsibilities):
            title_category = 'leadership'
        
        # Compensation - IMPROVED: Extract actual salary ranges
        comp_match = False
        comp_target = t.get('comp_target', 0)
        
        # Look for salary ranges in text
        import re
        salary_patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:-\d{1,3}(?:,\d{3})*)?)',  # $100,000-$200,000
            r'(\d{1,3}(?:,\d{3})*(?:-\d{1,3}(?:,\d{3})*)?)\s*(?:USD|dollars?)',  # 100,000-200,000 USD
        ]
        
        max_salary = 0
        for pattern in salary_patterns:
            matches = re.findall(pattern, job_text)
            for match in matches:
                if '-' in match:
                    # Range like "100,000-200,000"
                    parts = match.split('-')
                    try:
                        high_end = int(parts[1].replace(',', ''))
                        max_salary = max(max_salary, high_end)
                    except:
                        pass
                else:
                    # Single number
                    try:
                        salary = int(match.replace(',', ''))
                        max_salary = max(max_salary, salary)
                    except:
                        pass
        
        # Check if compensation meets target
        if max_salary > 0:
            comp_match = max_salary >= comp_target
            if comp_match:
                score += weights.get('comp_target', 3.0)
                # Bonus for high compensation
                if max_salary >= 200000:
                    score += 2.0  # Extra bonus for high comp
        else:
            # Fallback to keyword matching
            comp_found = any(kw in job_text.lower() for kw in keywords.get('comp_indicators', []))
            comp_match = comp_found
            if comp_match:
                score += weights.get('comp_target', 1.0)  # Lower score for keyword-only match
        
        # Location
        location_match = False
        location_type = ""
        for loc in t.get('locations', {}).get('preferred', []):
            if loc.lower() in job_text.lower():
                location_match = True
                location_type = "preferred"
                score += weights.get('location_preferred', 2.0)
        if not location_match:
            for loc in t.get('locations', {}).get('open_to', []):
                if loc.lower() in job_text.lower():
                    location_match = True
                    location_type = "open_to"
                    score += weights.get('location_open', 1.0)
        
        # Role types
        role_type_matches = []
        for role_type in t.get('role_types', []):
            for kw in keywords.get('role_type_indicators', {}).get(role_type, []):
                if kw in job_text.lower():
                    role_type_matches.append(role_type)
                    score += weights.get('role_type_match', 2.0)
                    break
        
        # Company stage - IMPROVED: Better detection of well-funded companies
        company_stage_match = False
        text_lower = job_text.lower()
        
        # Check for well-funded indicators (these are GOOD)
        well_funded_indicators = [
            'backed by', 'funded by', 'series', 'unicorn', 'billion', 'valuation',
            'lightspeed', 'a16z', 'sequoia', 'andreessen', 'coatue', 'silver lake'
        ]
        
        # Check for early-stage indicators (these are RISKIER)
        early_stage_indicators = [
            'seed', 'pre-seed', 'angel', 'bootstrapped', 'first hire', 'founding team'
        ]
        
        # Well-funded companies get positive score
        if any(indicator in text_lower for indicator in well_funded_indicators):
            company_stage_match = True
            score += weights.get('company_stage_match', 2.0)  # Higher score for well-funded
        # Early-stage companies get lower score
        elif any(indicator in text_lower for indicator in early_stage_indicators):
            company_stage_match = True
            score += weights.get('company_stage_match', 0.5)  # Lower score for early-stage
        
        # Business model
        business_model_match = False
        for bm in t.get('business_models', []):
            for kw in keywords.get('business_model_indicators', {}).get(bm, []):
                if kw in job_text.lower():
                    business_model_match = True
                    score += weights.get('business_model_match', 1.0)
                    break
        
        # Go/No-Go - IMPROVED: More flexible logic
        # High compensation can override strict title requirements
        high_comp_override = max_salary >= 200000
        
        # Calculate total positive factors
        positive_factors = 0
        if title_match:
            positive_factors += 1
        if location_match:
            positive_factors += 1
        if role_type_matches:
            positive_factors += 1
        if company_stage_match:
            positive_factors += 1
        if business_model_match:
            positive_factors += 1
        if comp_match and high_comp_override:
            positive_factors += 2  # High comp counts double
        
        # More flexible go/no-go: require fewer factors if high comp
        required_factors = 2 if high_comp_override else 3
        targeting_go_no_go = positive_factors >= required_factors
        
        return JobTargeting(
            title_match=title_match,
            title_category=title_category,
            comp_match=comp_match,
            location_match=location_match,
            location_type=location_type,
            role_type_matches=role_type_matches,
            company_stage_match=company_stage_match,
            business_model_match=business_model_match,
            targeting_score=score,
            targeting_go_no_go=targeting_go_no_go
        )
    
    def select_blurbs(self, job: JobDescription, debug=False, explain=False):
        """Select appropriate blurbs for the job description. Optionally return debug info."""
        debug_steps = []
        selected_blurbs = {}
        max_scores = {}
        for blurb_type, blurb_list in self.blurbs.items():
            best_match = None
            best_score = -1
            scores = []
            for blurb in blurb_list:
                score = self._calculate_blurb_score(blurb, job)
                scores.append((blurb['id'], score))
                if score > best_score:
                    best_score = score
                    best_match = BlurbMatch(
                        blurb_id=blurb['id'],
                        blurb_type=blurb_type,
                        text=blurb['text'],
                        tags=blurb['tags'],
                        score=score,
                        selected=True
                    )
            max_scores[blurb_type] = best_score
            # Enforce 60% relevance threshold
            if best_match and best_score >= 0.6 * (best_score if best_score > 0 else 1):
                selected_blurbs[blurb_type] = best_match
            if debug or explain:
                debug_steps.append({
                    'blurb_type': blurb_type,
                    'scores': scores,
                    'selected': best_match.blurb_id if best_match else None,
                    'selected_score': best_score
                })
        selected_blurbs = self._remove_blurb_duplication(selected_blurbs)
        if debug or explain:
            return selected_blurbs, debug_steps
        return selected_blurbs
    
    def _calculate_blurb_score(self, blurb: Dict, job: JobDescription) -> float:
        """Calculate how well a blurb matches the job description."""
        score = 0.0
        
        # Score based on tag overlap with job keywords
        for tag in blurb['tags']:
            if tag in job.keywords:
                score += 1.0
            elif tag.lower() in [k.lower() for k in job.keywords]:
                score += 0.5
        
        # Bonus for job type alignment
        if job.job_type in blurb['tags']:
            score += 2.0
        
        # Bonus for 'all' tag (universal blurbs)
        if 'all' in blurb['tags']:
            score += 0.5
        
        # ENHANCED: Theme-based paragraph2 selection
        if blurb.get('id') in ['growth', 'ai_ml', 'cleantech', 'internal_tools']:
            score = self._calculate_paragraph2_theme_score(blurb, job)
        
        return score
    
    def _remove_blurb_duplication(self, selected_blurbs: Dict[str, BlurbMatch]) -> Dict[str, BlurbMatch]:
        """Remove duplication between selected blurbs."""
        # Check for duplicate content between blurbs
        blurb_texts = []
        for blurb_type, blurb in selected_blurbs.items():
            if blurb_type in ['paragraph2', 'examples']:
                blurb_texts.append(blurb.text.lower())
        
        # If we have both paragraph2 and examples, check for overlap
        if 'paragraph2' in selected_blurbs and 'examples' in selected_blurbs:
            para2_text = selected_blurbs['paragraph2'].text.lower()
            examples_text = selected_blurbs['examples'].text.lower()
            
            # Check for significant overlap (same company/role mentioned)
            companies_para2 = self._extract_companies_from_text(para2_text)
            companies_examples = self._extract_companies_from_text(examples_text)
            
            if companies_para2 and companies_examples:
                overlap = set(companies_para2) & set(companies_examples)
                if overlap:
                    # If same company mentioned in both, prefer the higher scoring one
                    if selected_blurbs['paragraph2'].score > selected_blurbs['examples'].score:
                        del selected_blurbs['examples']
                    else:
                        del selected_blurbs['paragraph2']
        
        return selected_blurbs
    
    def _extract_companies_from_text(self, text: str) -> List[str]:
        """Extract company names from text."""
        companies = []
        # Common company patterns
        company_patterns = [
            'At Meta', 'At Aurora', 'At Enact', 'At SpatialThink',
            'Meta', 'Aurora', 'Enact', 'SpatialThink'
        ]
        
        for pattern in company_patterns:
            if pattern.lower() in text:
                companies.append(pattern)
        
        return companies
    
    def _calculate_paragraph2_theme_score(self, blurb: Dict, job: JobDescription) -> float:
        """Calculate theme-specific score for paragraph2 blurbs."""
        job_text_lower = job.raw_text.lower()
        blurb_id = blurb.get('id', '')
        
        # Growth theme indicators
        growth_indicators = [
            'onboarding', 'activation', 'a/b testing', 'product-led growth', 'plg',
            'conversion', 'monetization', 'user acquisition', 'retention',
            'experiments', 'dashboard', 'metrics', 'analytics', 'growth'
        ]
        
        # AI/ML theme indicators  
        ai_ml_indicators = [
            'nlp', 'ml model', 'trust', 'explainability', 'explainable',
            'agent interfaces', 'artificial intelligence', 'machine learning',
            'neural networks', 'algorithms', 'model deployment', 'ai', 'ml'
        ]
        
        # Cleantech theme indicators
        cleantech_indicators = [
            'climate', 'energy', 'sustainability', 'renewable', 'solar',
            'clean energy', 'carbon', 'environmental'
        ]
        
        # Internal tools theme indicators
        internal_tools_indicators = [
            'internal tools', 'employee tools', 'hr tools', 'productivity',
            'efficiency', 'operations', 'workflow', 'process'
        ]
        
        # Calculate theme match scores
        growth_score = sum(2.0 for indicator in growth_indicators if indicator in job_text_lower)
        ai_ml_score = sum(2.0 for indicator in ai_ml_indicators if indicator in job_text_lower)
        cleantech_score = sum(2.0 for indicator in cleantech_indicators if indicator in job_text_lower)
        internal_tools_score = sum(2.0 for indicator in internal_tools_indicators if indicator in job_text_lower)
        
        # Debug logging
        logger.info(f"Blurb ID: {blurb_id}")
        logger.info(f"Growth score: {growth_score}, AI/ML score: {ai_ml_score}, Cleantech score: {cleantech_score}, Internal tools score: {internal_tools_score}")
        
        # Match blurb to highest scoring theme
        if blurb_id == 'growth' and growth_score > max(ai_ml_score, cleantech_score, internal_tools_score):
            logger.info(f"Selected growth blurb with score {growth_score}")
            return 10.0  # High score for perfect theme match
        elif blurb_id == 'ai_ml' and ai_ml_score > max(growth_score, cleantech_score, internal_tools_score):
            logger.info(f"Selected ai_ml blurb with score {ai_ml_score}")
            return 10.0
        elif blurb_id == 'cleantech' and cleantech_score > max(growth_score, ai_ml_score, internal_tools_score):
            logger.info(f"Selected cleantech blurb with score {cleantech_score}")
            return 10.0
        elif blurb_id == 'internal_tools' and internal_tools_score > max(growth_score, ai_ml_score, cleantech_score):
            logger.info(f"Selected internal_tools blurb with score {internal_tools_score}")
            return 10.0
        else:
            # Lower score for non-matching themes
            logger.info(f"Non-matching theme for {blurb_id}, returning low score")
            return 1.0
    
    def _should_include_leadership_blurb(self, job: JobDescription) -> bool:
        """Return True if the role is a leadership role or JD mentions managing/mentoring."""
        title = job.job_title.lower()
        jd_text = job.raw_text.lower()
        leadership_titles = ['lead', 'director', 'head', 'vp', 'chief', 'manager', 'executive']
        if any(t in title for t in leadership_titles):
            return True
        if 'managing' in jd_text or 'mentoring' in jd_text:
            return True
        return False

    def generate_cover_letter(self, job: JobDescription, selected_blurbs: dict, missing_requirements: List[str] = None) -> str:
        """Generate a cover letter from selected blurbs using approved content. Optionally fill gaps with role_specific_alignment blurbs."""
        logger.info("Generating cover letter...")
        cover_letter_parts = []
        # Greeting
        company = job.company_name.strip() if hasattr(job, 'company_name') and job.company_name else ''
        if company:
            greeting = f"Dear {company} team,"
        else:
            greeting = "Dear Hiring Team,"
        cover_letter_parts.append(greeting)
        cover_letter_parts.append("")
        # Intro
        intro_text = self._select_appropriate_intro_blurb(job)
        intro_text = self._customize_intro_for_role(intro_text, job)
        cover_letter_parts.append(intro_text)
        cover_letter_parts.append("")
        # Paragraph 2 (role-specific alignment) - only if strong match
        para2_text = self._select_paragraph2_blurb(job)
        if para2_text and para2_text.strip():
            cover_letter_parts.append(para2_text)
            cover_letter_parts.append("")
        # Dynamically selected case studies (top 2–3)
        case_studies = self._select_top_case_studies(job)
        for case_study in case_studies:
            cover_letter_parts.append(case_study)
            cover_letter_parts.append("")
        # Leadership blurb if leadership role or JD mentions managing/mentoring
        if self._should_include_leadership_blurb(job):
            for blurb in self.blurbs.get('leadership', []):
                if blurb['id'] == 'leadership':
                    cover_letter_parts.append(blurb['text'])
                    cover_letter_parts.append("")
                    break
        # PATCH: Add role_specific_alignment blurbs for missing/partial requirements (robust, no duplicates)
        if missing_requirements:
            used_blurbs = set()
            for req in missing_requirements:
                for blurb in self.blurbs.get('role_specific_alignment', []):
                    if any(tag.lower() in req.lower() or req.lower() in tag.lower() for tag in blurb.get('tags', [])):
                        if blurb['text'] not in used_blurbs:
                            cover_letter_parts.append(blurb['text'])
                            cover_letter_parts.append("")
                            used_blurbs.add(blurb['text'])
        # Closing: choose standard, mission_aligned, or growth_focused
        closing = self._generate_compelling_closing(job)
        cover_letter_parts.append(closing)
        cover_letter_parts.append("")
        cover_letter_parts.append("Best regards,")
        cover_letter_parts.append("Peter Spannagle")
        cover_letter_parts.append("linkedin.com/in/pspan")
        # Join and clean up
        cover_letter = "\n".join([line.strip() for line in cover_letter_parts if line.strip()])
        cover_letter = re.sub(r'\n+', '\n\n', cover_letter)
        cover_letter = re.sub(r' +', ' ', cover_letter)
        # Remove any resume data or skills lines
        cover_letter = re.sub(r'Key Skills:.*?(\n|$)', '', cover_letter, flags=re.IGNORECASE)
        # Remove deprecated blurbs (GenAI, Climate Week, etc.) if present
        for deprecated in ['GenAI', 'Climate Week', 'sf_climate_week', 'genai_voice', 'duke']:
            cover_letter = re.sub(deprecated, '', cover_letter, flags=re.IGNORECASE)
        return cover_letter

    def _requirements_mapping_section(self, job: JobDescription) -> str:
        """Map each core requirement to the case study or experience that demonstrates it."""
        mapping = {
            'User interviews': 'Meta, Enact',
            'Manage XFN teams': 'Meta, Enact, Aurora',
            'Electrification domain expertise': 'Aurora, Enact',
            'Figma': 'Samsung, Meta (background in design and front end)',
            'Data': 'Enact, SpatialThink, Aurora, Meta',
            'Startup experience': 'Aurora (early team), Enact (founder)',
        }
        lines = []
        for req, exp in mapping.items():
            lines.append(f"- {req}: {exp}")
        return "\n".join(lines)
    
    def review_jd_vs_draft(self, job: JobDescription, cover_letter: str) -> Dict[str, Any]:
        """Review JD vs draft cover letter and identify weaknesses and improvements."""
        analysis = {
            'job_requirements': self._extract_key_requirements(job),
            'demonstrated_skills': self._extract_demonstrated_skills(cover_letter),
            'gaps': [],
            'improvements': [],
            'strengths': []
        }
        
        # Extract key requirements from JD
        requirements = analysis['job_requirements']
        demonstrated = analysis['demonstrated_skills']
        
        # Identify gaps
        for req in requirements:
            if req not in demonstrated:
                analysis['gaps'].append(f"Missing demonstration of: {req}")
        
        # Identify strengths
        for skill in demonstrated:
            if skill in requirements:
                analysis['strengths'].append(f"Strong demonstration of: {skill}")
        
        # Generate improvement suggestions
        if analysis['gaps']:
            analysis['improvements'].append("Add specific examples that demonstrate missing requirements")
        
        if len(cover_letter.split()) < 300:
            analysis['improvements'].append("Cover letter may be too brief - consider adding more detail")
        
        if len(cover_letter.split()) > 600:
            analysis['improvements'].append("Cover letter may be too long - consider condensing")
        
        # Check for quantified impact
        if not re.search(r'\d+%', cover_letter):
            analysis['improvements'].append("Add more quantified impact metrics")
        
        return analysis
    
    def _extract_key_requirements(self, job: JobDescription) -> List[str]:
        """Extract key requirements from job description."""
        requirements = []
        job_text_lower = job.raw_text.lower()
        
        # Extract requirements based on common patterns
        requirement_patterns = [
            r'(\d+)\+?\s+years?\s+of\s+([^,\n]+)',
            r'experience\s+with\s+([^,\n]+)',
            r'proficiency\s+in\s+([^,\n]+)',
            r'familiarity\s+with\s+([^,\n]+)',
            r'expertise\s+in\s+([^,\n]+)',
        ]
        
        for pattern in requirement_patterns:
            matches = re.findall(pattern, job_text_lower)
            for match in matches:
                if isinstance(match, tuple):
                    requirements.append(' '.join(match))
                else:
                    requirements.append(match)
        
        # Add common requirements based on keywords
        if 'product manager' in job_text_lower:
            requirements.extend(['product management', 'user research', 'data analysis'])
        
        if 'python' in job_text_lower:
            requirements.append('python')
        
        if 'figma' in job_text_lower:
            requirements.append('figma')
        
        if 'user interviews' in job_text_lower:
            requirements.append('user interviews')
        
        if 'data analysis' in job_text_lower:
            requirements.append('data analysis')
        
        return list(set(requirements))  # Remove duplicates
    
    def _extract_demonstrated_skills(self, cover_letter: str) -> List[str]:
        """Extract skills demonstrated in the cover letter."""
        skills = []
        cover_letter_lower = cover_letter.lower()
        
        # Check for demonstrated skills
        skill_indicators = {
            'product management': ['product strategy', 'roadmap', 'user research', 'customer insights'],
            'data analysis': ['analytics', 'data', 'metrics', 'quantified', '210%', '876%'],
            'user research': ['user interviews', 'discovery', 'workflow analysis', 'customer insights'],
            'python': ['python', 'analytics', 'data analysis'],
            'figma': ['figma', 'design', 'mockups'],
            'growth': ['growth', 'scaling', 'user acquisition', 'retention'],
            'leadership': ['led', 'managed', 'team', 'cross-functional'],
            'startup experience': ['startup', 'series a', '0-1', 'founding'],
            'cleantech': ['solar', 'energy', 'climate', 'renewable'],
            'ai/ml': ['ai', 'ml', 'machine learning', 'explainable ai']
        }
        
        for skill, indicators in skill_indicators.items():
            if any(indicator in cover_letter_lower for indicator in indicators):
                skills.append(skill)
        
        return skills
    
    def _select_appropriate_intro_blurb(self, job: JobDescription) -> str:
        """Always use the approved standard intro from blurbs.yaml. No fallback or custom text."""
        if 'intro' in self.blurbs:
            for blurb in self.blurbs['intro']:
                if blurb['id'] == 'standard':
                    return blurb['text']
        return ""

    def _customize_intro_for_role(self, intro_text: str, job: JobDescription) -> str:
        """Replace [product leader/manager] (straight or curly quotes) with the correct role in the intro."""
        role = job.job_title.lower()
        for placeholder in ['[product leader/manager]', '"[product leader/manager]"', '"[product leader/manager]"']:
            if placeholder in intro_text:
                if 'manager' in role:
                    intro_text = intro_text.replace(placeholder, 'product manager')
                elif 'lead' in role:
                    intro_text = intro_text.replace(placeholder, 'product leader')
                else:
                    intro_text = intro_text.replace(placeholder, 'product leader')
        return intro_text

    def _select_paragraph2_blurb(self, job: JobDescription) -> str:
        """Select a cleantech blurb if any cleantech/energy keyword is present in the JD; fallback to standard or blank."""
        para2_blurbs = self.blurbs.get('paragraph2', [])
        jd_text = job.raw_text.lower()
        cleantech_keywords = ['cleantech', 'renewable', 'solar', 'climate', 'energy', 'grid', 'interconnection']
        # Scan entire JD for cleantech/energy keywords
        if any(kw in jd_text for kw in cleantech_keywords):
            for blurb in para2_blurbs:
                if 'cleantech' in blurb.get('tags', []) or blurb.get('id') == 'cleantech':
                    return blurb['text']
        # Fallback to standard blurb if exists
        for blurb in para2_blurbs:
            if blurb.get('id') == 'standard':
                return blurb['text']
        # Fallback to blank
        return ""

    def _select_top_case_studies(self, job: JobDescription) -> list:
        """Select up to 3 top case studies dynamically; fallback to Enact, Aurora, Meta if not enough are found. Use only 2 if there is high uncertainty (very low scores or no strong matches)."""
        selected = self.get_case_studies(job.keywords)
        # If we have 3 or more, use top 3
        if len(selected) >= 3:
            return [cs['text'] for cs in selected[:3]]
        # If we have 2, use 2
        if len(selected) == 2:
            return [cs['text'] for cs in selected]
        # If we have 1, use 1
        if len(selected) == 1:
            return [cs['text'] for cs in selected]
        # Fallback: if 0, use static list
        all_examples = {cs['id']: cs for cs in self.blurbs.get('examples', [])}
        fallback = [all_examples.get('enact'), all_examples.get('aurora'), all_examples.get('meta')]
        fallback = [cs for cs in fallback if cs]
        return [cs['text'] for cs in fallback[:3]]
    
    def _generate_personalized_greeting(self, job: JobDescription) -> str:
        """Generate a personalized greeting based on company name."""
        company = job.company_name.strip() if hasattr(job, 'company_name') and job.company_name else ''
        if company:
            return f"Dear {company} team,"
        else:
            return "Dear Hiring Team,"
    
    def _generate_compelling_opening(self, job: JobDescription) -> str:
        """Generate a compelling opening paragraph with direct value proposition."""
        company = job.company_name
        role = job.job_title
        
        # Extract key themes from job description
        themes = self._extract_job_themes(job)
        
        # Build opening based on role type and themes
        if 'product' in role.lower():
            opening = f"I've helped early-stage companies find product-market fit, scale revenue, and build products users love. "
            opening += f"As a product leader with experience in {', '.join(themes[:2])}, I'm excited to bring this expertise to {company}—"
            opening += f"helping you {self._get_role_specific_value(job)}."
        elif 'growth' in role.lower():
            opening = f"I've helped companies scale revenue and user acquisition through data-driven growth strategies. "
            opening += f"As a growth leader with experience in {', '.join(themes[:2])}, I'm excited to bring this expertise to {company}—"
            opening += f"helping you {self._get_role_specific_value(job)}."
        elif 'venture' in role.lower() or 'investment' in role.lower():
            opening = f"I've helped early-stage companies find product-market fit, scale revenue, and raise capital. "
            opening += f"As an operator and product leader, I've built software from scratch, worked alongside investors, and led go-to-market strategy. "
            opening += f"I'm excited to bring this perspective to {company}—helping founders grow faster with strategic support grounded in lived experience."
        else:
            opening = f"I've helped companies achieve their strategic goals through innovative solutions and execution. "
            opening += f"As a leader with experience in {', '.join(themes[:2])}, I'm excited to bring this expertise to {company}—"
            opening += f"helping you {self._get_role_specific_value(job)}."
        
        return opening
    
    def _extract_job_themes(self, job: JobDescription) -> List[str]:
        """Extract key themes from job description."""
        themes = []
        job_text_lower = job.raw_text.lower()
        
        # Extract themes based on keywords
        if 'product' in job_text_lower:
            themes.append("product development")
        if 'growth' in job_text_lower:
            themes.append("growth strategy")
        if 'user' in job_text_lower:
            themes.append("user experience")
        if 'data' in job_text_lower:
            themes.append("data-driven decision making")
        if 'scale' in job_text_lower:
            themes.append("scaling operations")
        if 'revenue' in job_text_lower:
            themes.append("revenue optimization")
        
        return themes[:3]  # Return top 3 themes
    
    def _get_role_specific_value(self, job: JobDescription) -> str:
        """Get role-specific value proposition."""
        role = job.job_title.lower()
        
        if 'product' in role:
            return "build products that users love and drive business impact"
        elif 'growth' in role:
            return "scale user acquisition and revenue through data-driven strategies"
        elif 'venture' in role or 'investment' in role:
            return "identify breakout opportunities and support founders"
        else:
            return "achieve your strategic goals through innovative execution"
    
    def _enhance_with_quantified_impact(self, text: str, job: JobDescription) -> str:
        """Enhance text with quantified impact metrics."""
        # Add specific metrics if not present
        if '210%' not in text and 'MAUs' not in text:
            # Add quantified impact
            text = text.replace("boosted MAUs", "boosted MAUs by 210%")
            text = text.replace("increased events", "increased visitor events by 876%")
            text = text.replace("improved retention", "improved time-in-app by 853%")
        
        return text
    
    def _enhance_with_strategic_positioning(self, text: str, job: JobDescription) -> str:
        """Enhance text with strategic positioning."""
        # Add strategic context if not present
        if 'Series A' not in text and 'Series C' not in text:
            text = text.replace("At Aurora Solar", "At Aurora Solar, I was the founding PM and helped scale the company from Series A to Series C")
        
        if 'valuation' not in text:
            text = text.replace("captured the majority", "captured the majority of the U.S. solar installer market and reach a $4B valuation")
        
        return text
    
    def _extract_mission_from_jd(self, job: JobDescription) -> str:
        """Extract a mission statement (problem + desired outcome) from the JD text."""
        lines = job.raw_text.split('\n')
        for line in lines:
            if 'mission' in line.lower() or 'our goal' in line.lower() or 'we aim' in line.lower() or 'purpose' in line.lower():
                if len(line.strip()) > 20:
                    return line.strip()
        return ""

    def _find_custom_closer(self, job: JobDescription, mission_text: str) -> str:
        """Find a custom closer in blurbs.yaml matching the mission/problem tags or company."""
        if 'closing' in self.blurbs:
            for blurb in self.blurbs['closing']:
                # Match by tag or company/mission keyword
                for tag in blurb.get('tags', []):
                    if tag.lower() in job.company_name.lower() or tag.lower() in mission_text.lower():
                        return blurb['text']
        return ""

    def _propose_custom_closer(self, job: JobDescription, mission_text: str) -> str:
        """Propose a custom closer based on the extracted mission."""
        # Example for Nira; in practice, this could be more dynamic or use a template
        if 'nira' in job.company_name.lower():
            return ("I'm inspired by Nira's mission to accelerate renewables by making grid interconnection faster, "
                    "cheaper, and more transparent. I'd love to help you scale tools that reduce soft costs and unlock more fossil-free power.")
        # Generic fallback
        return f"I'm inspired by your mission: {mission_text}. I'd love to help you achieve this vision."

    def _generate_compelling_closing(self, job: JobDescription) -> str:
        """Use mission-aligned closer if a mission line is found in the JD; prompt user to confirm/edit if interactive."""
        company = job.company_name.strip() if hasattr(job, 'company_name') and job.company_name else ''
        # Scan JD for 'mission' line (case-insensitive, strip whitespace)
        mission_line = ''
        for line in job.raw_text.split('\n'):
            line_stripped = line.strip()
            if 'mission' in line_stripped.lower() and len(line_stripped) > 10:
                mission_line = line_stripped
                print(f"[DEBUG] Extracted mission line: {mission_line}")
                break
        # If found, use as mission-aligned closer
        if mission_line:
            closer = f"I'm inspired by your mission: {mission_line} I'd love to help you achieve this vision."
            return closer
        # Fallback to standard closing
        if 'closing' in self.blurbs:
            for blurb in self.blurbs['closing']:
                if blurb['id'] == 'standard':
                    text = blurb['text']
                    text = text.replace('[Company Name]', company)
                    text = text.replace('[company name]', company)
                    text = text.replace('[company]', company)
                    return text
        # Generic fallback
        return f"I'm excited about the opportunity to help {company} scale and grow. I'd love to discuss how my background can contribute to your next chapter."
    
    def _customize_closing_paragraph(self, closing_text: str, job: JobDescription) -> str:
        """Customize closing paragraph with company-specific mission and language."""
        # Extract company mission from job description
        mission_keywords = ['mission', 'vision', 'goal', 'purpose', 'bring', 'enable', 'help']
        job_text_lower = job.raw_text.lower()
        
        # Find mission statement
        mission_statement = ""
        lines = job.raw_text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in mission_keywords):
                if len(line.strip()) > 20:  # Substantial mission statement
                    mission_statement = line.strip()
                    break
        
        # Extract key mission elements
        mission_elements = []
        if 'billion' in job_text_lower:
            mission_elements.append("scale to millions/billions of users")
        if 'developer' in job_text_lower:
            mission_elements.append("empower developers")
        if 'web3' in job_text_lower:
            mission_elements.append("bring web3 to mainstream")
        if 'onboarding' in job_text_lower:
            mission_elements.append("simplify user onboarding")
        if 'activation' in job_text_lower:
            mission_elements.append("drive user activation")
        
        # Create customized mission statement
        if mission_elements:
            custom_mission = f"Unknown Company's mission to {mission_elements[0]}"
        elif mission_statement:
            custom_mission = mission_statement
        else:
            custom_mission = "Unknown Company's mission"
        
        # Replace placeholders
            closing_text = closing_text.replace("[Company Name]", job.company_name)
        closing_text = closing_text.replace("[specific mission]", custom_mission)
        
        # Add experience connection if not present
        if "experience" not in closing_text.lower():
            experience_connections = [
                "My experience building products that create real impact aligns perfectly with your vision.",
                "My background in user-centric product development supports your mission.",
                "My track record of scaling products and teams would contribute to your goals."
            ]
            closing_text = closing_text.replace("I'm excited", f"{experience_connections[0]} I'm excited")
        
        return closing_text
    
    def _apply_brevity_improvements(self, cover_letter: str, job: JobDescription) -> str:
        """Apply minimal brevity improvements - preserve narrative flow."""
        # Only remove obvious filler phrases
        filler_phrases = [
            "I believe", "I think", "that said"
        ]
        
        for phrase in filler_phrases:
            cover_letter = cover_letter.replace(phrase, "")
        
        # Adjust tone for IC vs leadership roles
        job_title_lower = job.job_title.lower()
        job_text_lower = job.raw_text.lower()
        
        # Check for leadership indicators in JD
        leadership_indicators = ['managing', 'mentoring', 'leading', 'directing', 'overseeing']
        is_leadership_role = any(indicator in job_text_lower for indicator in leadership_indicators)
        
        # IC role detection
        is_ic_role = (
            'senior' not in job_title_lower and 
            'lead' not in job_title_lower and 
            'director' not in job_title_lower and
            'vp' not in job_title_lower and
            not is_leadership_role
        )
        
        if is_ic_role:
            # IC role - soften leadership language
            ic_replacements = {
                "owned P&L": "worked on P&L",
                "managed 8-person team": "worked with 8-person team",
                "led cross-functional team": "worked cross-functionally",
                "owned product strategy": "contributed to product strategy",
                "led a cross-functional team": "worked cross-functionally",
                "led the design": "designed",
                "led the rollout": "implemented"
            }
            
            for old, new in ic_replacements.items():
                cover_letter = cover_letter.replace(old, new)
        
        return cover_letter
    
    def review_draft(self, cover_letter: str, job: JobDescription) -> List[EnhancementSuggestion]:
        """Review the draft and generate enhancement suggestions."""
        logger.info("Reviewing draft for enhancement suggestions...")
        
        suggestions = []
        
        # Check for low score issues
        if job.score < self.logic['enhancement_suggestions']['triggers']['low_score']['threshold']:
            suggestions.append(EnhancementSuggestion(
                timestamp=datetime.now().isoformat(),
                job_id=f"JOB_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                enhancement_type="content_improvement",
                category="keyword_optimization",
                description=self.logic['enhancement_suggestions']['triggers']['low_score']['message'],
                status="open",
                priority="high"
            ))
        
        # Check for missing examples
        if 'examples' not in cover_letter.lower():
            suggestions.append(EnhancementSuggestion(
                timestamp=datetime.now().isoformat(),
                job_id=f"JOB_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                enhancement_type="content_improvement",
                category="experience_examples",
                description=self.logic['enhancement_suggestions']['triggers']['missing_examples']['message'],
                status="open",
                priority="medium"
            ))
        
        # Check for weak closing
        if len([line for line in cover_letter.split('\n') if 'excited' in line.lower()]) == 0:
            suggestions.append(EnhancementSuggestion(
                timestamp=datetime.now().isoformat(),
                job_id=f"JOB_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                enhancement_type="content_improvement",
                category="company_research",
                description=self.logic['enhancement_suggestions']['triggers']['weak_closing']['message'],
                status="open",
                priority="medium"
            ))
        
        # Check for generic content
        generic_phrases = ['I am excited', 'I would love', 'I believe', 'I think']
        generic_count = sum(1 for phrase in generic_phrases if phrase.lower() in cover_letter.lower())
        if generic_count > 2:
            suggestions.append(EnhancementSuggestion(
                timestamp=datetime.now().isoformat(),
                job_id=f"JOB_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                enhancement_type="content_improvement",
                category="tone_adjustment",
                description=self.logic['enhancement_suggestions']['triggers']['generic_content']['message'],
                status="open",
                priority="medium"
            ))
        
        # Add suggestions to log
        for suggestion in suggestions:
            self.enhancement_log.append({
                'timestamp': suggestion.timestamp,
                'job_id': suggestion.job_id,
                'enhancement_type': suggestion.enhancement_type,
                'category': suggestion.category,
                'description': suggestion.description,
                'status': suggestion.status,
                'priority': suggestion.priority,
                'notes': suggestion.notes
            })
        
        self._save_enhancement_log()
        
        return suggestions
    
    def process_job_description(self, job_text: str, debug=False, explain=False, track_enhance=False, interactive=False):
        """Main processing function for a job description. Optionally returns debug info. If interactive, prompt user to confirm/override each extraction and gap-filling step."""
        logger.info("Processing job description...")
        debug_info = {}
        # Parse job description
        job = self.parse_job_description(job_text)
        # --- INTERACTIVE: Confirm/override company name ---
        if interactive:
            print(f"\n[STEP] Extracted company name: '{job.company_name}'")
            user_input = input("Press Enter to accept, or type a new company name: ").strip()
            if user_input:
                job.company_name = user_input
        # Robust: Always prompt if company name is empty after extraction
        if not job.company_name:
            print("\n[INFO] Could not confidently extract company name from job description.")
            company_name = input("Please enter the company name: ").strip()
            job.company_name = company_name
        # --- INTERACTIVE: Confirm/override mission extraction ---
        mission_text = self._extract_mission_from_jd(job)
        if interactive:
            print(f"\n[STEP] Extracted mission: '{mission_text}'")
            user_input = input("Press Enter to accept, or type a new mission statement: ").strip()
            if user_input:
                mission_text = user_input
        # --- INTERACTIVE: Confirm/override requirements extraction ---
        try:
            try:
                from agents.gap_analysis import extract_requirements_llm, gap_analysis_llm
            except ImportError:
                from gap_analysis import extract_requirements_llm, gap_analysis_llm
            api_key = os.environ.get('OPENAI_API_KEY') or ""
            jd_reqs = extract_requirements_llm(job_text, api_key)
            if interactive:
                print("\n[STEP] Extracted requirements:")
                for cat, reqs in jd_reqs.items():
                    print(f"  {cat}: {reqs}")
                user_input = input("Press Enter to accept, or type 'edit' to manually enter requirements: ").strip()
                if user_input.lower() == 'edit':
                    jd_reqs = {}
                    for cat in ['tools', 'team_dynamics', 'domain_knowledge', 'soft_skills', 'responsibilities', 'outcomes']:
                        reqs = input(f"Enter requirements for {cat} (comma-separated, or leave blank): ").strip()
                        if reqs:
                            jd_reqs[cat] = [r.strip() for r in reqs.split(',') if r.strip()]
            # Generate initial draft
            selected_blurbs = self.select_blurbs(job)
            if isinstance(selected_blurbs, tuple):
                selected_blurbs = selected_blurbs[0]
            draft = self.generate_cover_letter(job, selected_blurbs, [])
            gap_report = gap_analysis_llm(jd_reqs, draft, api_key)
            missing_requirements = []
            if interactive:
                print("\n[STEP] Gap analysis results:")
                for req_cat, reqs in jd_reqs.items():
                    for req in reqs:
                        info = gap_report.get(req, {})
                        status = info.get('status') if isinstance(info, dict) else ''
                        rec = info.get('recommendation') if isinstance(info, dict) else ''
                        print(f"  {req}: {status} {rec}")
            # --- INTERACTIVE: Confirm/override gap-filling ---
            for req_cat, reqs in jd_reqs.items():
                for req in reqs:
                    info = gap_report.get(req, {})
                    if isinstance(info, dict) and info.get('status') in ['❌', '⚠️']:
                        if interactive:
                            print(f"\n[STEP] Gap detected: {req}")
                            action = input("Type 'add' to insert a matching blurb, 'skip' to ignore, or enter custom text: ").strip()
                            if action == 'add' or action == '':
                                missing_requirements.append(req)
                            elif action == 'skip':
                                continue
                            else:
                                # Custom blurb
                                from agents.gap_analysis import add_new_blurb
                                add_new_blurb(req, 'w')
                                missing_requirements.append(req)
                        else:
                            missing_requirements.append(req)
        except Exception as e:
            logger.warning(f"Gap analysis failed: {e}")
            missing_requirements = []
        # Generate enhanced cover letter with gap-filling
        selected_blurbs = self.select_blurbs(job)
        if isinstance(selected_blurbs, tuple):
            selected_blurbs = selected_blurbs[0]
        cover_letter = self.generate_cover_letter(job, selected_blurbs, missing_requirements)
        # --- LLM-DRIVEN REVIEW AND ENHANCE STEP ---
        if interactive:
            print("\n[STEP] LLM review and enhancement suggestions:")
            try:
                import openai
                api_key = os.environ.get('OPENAI_API_KEY') or ""
                client = openai.OpenAI(api_key=api_key)
                prompt = f"""
Here is a draft cover letter and the job description. Suggest specific, truthful, and tailored improvements to maximize interview odds. Highlight any missing requirements, propose new blurbs, and suggest edits for clarity, impact, and alignment with the company's mission. Output as a JSON list of suggestions, each with 'type' (add, edit, replace, blurb), 'target' (paragraph, requirement, closer, etc.), 'suggestion' (the new or improved text), and 'reason' (why this improves the letter).

Job Description:
{job_text}

Draft Cover Letter:
{cover_letter}
"""
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0
                )
                content = response.choices[0].message.content
                import json
                suggestions = []
                if content:
                    try:
                        suggestions = json.loads(content)
                    except Exception:
                        # Try to extract JSON from the response
                        start = content.find('[') if content else -1
                        end = content.rfind(']') + 1 if content else -1
                        if start != -1 and end != -1:
                            try:
                                suggestions = json.loads(content[start:end])
                            except Exception:
                                print("[LLM Review Warning] Could not parse suggestions from LLM response.")
                                suggestions = []
                        else:
                            print("[LLM Review Warning] No valid suggestions found in LLM response.")
                else:
                    print("[LLM Review Warning] No content returned from LLM.")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"\nSuggestion {i}: [{suggestion.get('type')}] {suggestion.get('target')}")
                    print(f"Reason: {suggestion.get('reason')}")
                    print(f"Proposed text:\n{suggestion.get('suggestion')}\n")
                    action = input("Type 'accept' to apply, 'edit' to modify, or 'skip' to ignore: ").strip().lower()
                    if action == 'accept' or action == '':
                        # Apply suggestion
                        cover_letter = self._apply_llm_suggestion(cover_letter, suggestion)
                        # Save new blurbs if type is 'blurb'
                        if suggestion.get('type') == 'blurb':
                            self._save_new_blurb(suggestion)
                    elif action == 'edit':
                        new_text = input("Enter your edited version: ").strip()
                        suggestion['suggestion'] = new_text
                        cover_letter = self._apply_llm_suggestion(cover_letter, suggestion)
                        if suggestion.get('type') == 'blurb':
                            self._save_new_blurb(suggestion)
                    elif action == 'skip':
                        continue
                rerun = input("\nWould you like another round of LLM review? (y/N): ").strip().lower()
                if rerun == 'y':
                    # Recursive call for another round
                    return self.process_job_description(job_text, debug, explain, track_enhance, interactive)
            except Exception as e:
                print(f"[LLM Review Error] {e}")
        # Review draft
        suggestions = self.review_draft(cover_letter, job) if track_enhance else []
        
        # Upload cover letter draft to Google Drive if available
        if self.google_drive and self.google_drive.available:
            try:
                file_id = self.google_drive.upload_cover_letter_draft(
                    cover_letter, 
                    job.company_name, 
                    job.job_title, 
                    job.score
                )
                if file_id:
                    logger.info(f"Cover letter draft uploaded to Google Drive with ID: {file_id}")
                else:
                    logger.warning("Failed to upload cover letter draft to Google Drive")
            except Exception as e:
                logger.error(f"Error uploading to Google Drive: {e}")
        
        if debug or explain:
            return job, cover_letter, suggestions, debug_info
        return job, cover_letter, suggestions

    def _apply_llm_suggestion(self, cover_letter: str, suggestion: dict) -> str:
        """Apply an LLM suggestion to the cover letter based on type and target."""
        # Simple implementation: replace or append text
        if suggestion.get('type') == 'replace' and suggestion.get('target'):
            target = suggestion['target']
            return cover_letter.replace(target, suggestion['suggestion'])
        elif suggestion.get('type') == 'edit' and suggestion.get('target'):
            target = suggestion['target']
            return cover_letter.replace(target, suggestion['suggestion'])
        elif suggestion.get('type') == 'add':
            return cover_letter + "\n\n" + suggestion['suggestion']
        elif suggestion.get('type') == 'blurb':
            return cover_letter + "\n\n" + suggestion['suggestion']
        else:
            return cover_letter

    def _save_new_blurb(self, suggestion: dict):
        """Save a new blurb to the blurb database for future reuse."""
        import yaml
        blurb_db_path = self.data_dir / "blurbs.yaml"
        try:
            with open(blurb_db_path, 'r') as f:
                blurbs = yaml.safe_load(f) or {}
        except Exception:
            blurbs = {}
        # Add to role_specific_alignment or a new section
        section = 'role_specific_alignment'
        if section not in blurbs:
            blurbs[section] = []
        blurbs[section].append({
            'id': f"llm_{len(blurbs[section])+1}",
            'tags': [],
            'text': suggestion.get('suggestion', '')
        })
        with open(blurb_db_path, 'w') as f:
            yaml.safe_dump(blurbs, f)
    
    def get_enhancement_suggestions(self, status: str = None) -> List[Dict]:
        """Get enhancement suggestions, optionally filtered by status."""
        if status:
            return [s for s in self.enhancement_log if s['status'] == status]
        return self.enhancement_log
    
    def update_enhancement_status(self, job_id: str, enhancement_type: str, status: str, notes: str = ""):
        """Update the status of an enhancement suggestion."""
        for suggestion in self.enhancement_log:
            if suggestion['job_id'] == job_id and suggestion['enhancement_type'] == enhancement_type:
                suggestion['status'] = status
                if notes:
                    suggestion['notes'] = notes
                break
        
        self._save_enhancement_log()

    def _find_role_specific_blurbs(self, job: JobDescription, missing_requirements: List[str]) -> List[str]:
        """Find blurbs from role_specific_alignment that match missing requirements by tag."""
        role_blurbs = []
        if 'role_specific_alignment' in self.blurbs:
            for req in missing_requirements:
                for blurb in self.blurbs['role_specific_alignment']:
                    if any(tag.lower() in req.lower() or req.lower() in tag.lower() for tag in blurb.get('tags', [])):
                        if blurb['text'] not in role_blurbs:
                            role_blurbs.append(blurb['text'])
        return role_blurbs

    def _spellcheck_cover_letter(self, text: str) -> str:
        """Run spell/grammar check on the cover letter using language_tool_python if available."""
        if TOOL_AVAILABLE:
            tool = language_tool_python.LanguageTool('en-US')
            matches = tool.check(text)
            return language_tool_python.utils.correct(text, matches)
        else:
            logger.warning("language_tool_python not available; skipping spell/grammar check.")
            return text


if __name__ == "__main__":
    # Example usage
    agent = CoverLetterAgent()
    
    # Example job description
    job_text = """
    Senior Product Manager - AI/ML Platform
    
    We are looking for a Senior Product Manager to join our AI/ML platform team at TechCorp. 
    You will be responsible for building and scaling AI-powered products that millions of users trust.
    
    Requirements:
    - 5+ years of product management experience
    - Experience with AI/ML products
    - Strong analytical skills
    - Experience with B2B products
    
    Responsibilities:
    - Define product strategy for AI features
    - Work with engineering teams to ship ML models
    - Analyze user data to improve product performance
    - Build trust with enterprise customers
    """
    
    job, cover_letter, suggestions = agent.process_job_description(job_text)
    
    print(f"Job Score: {job.score}")
    print(f"Go/No-Go: {job.go_no_go}")
    print(f"Job Type: {job.job_type}")
    print(f"Keywords: {job.keywords}")
    print("\n" + "="*50 + "\n")
    print("COVER LETTER:")
    print(cover_letter)
    print("\n" + "="*50 + "\n")
    print("ENHANCEMENT SUGGESTIONS:")
    for suggestion in suggestions:
        print(f"- {suggestion.description} ({suggestion.priority} priority)") 