#!/usr/bin/env python3
"""
Resume Parser
============

Extracts structured information from PDF resumes to serve as the ultimate
source of truth for cover letter generation.
"""

import re
import pdfplumber
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class ResumeSection:
    """Represents a section of the resume."""
    title: str
    content: str
    start_line: int
    end_line: int


@dataclass
class Experience:
    """Represents a work experience entry."""
    company: str
    title: str
    duration: str
    location: str
    description: List[str]
    achievements: List[str]
    skills_used: List[str]


@dataclass
class Education:
    """Represents an education entry."""
    institution: str
    degree: str
    field: str
    duration: str
    location: str


@dataclass
class Skill:
    """Represents a skill with proficiency level."""
    name: str
    category: str
    proficiency: str  # beginner, intermediate, advanced, expert


@dataclass
class ParsedResume:
    """Complete parsed resume data."""
    name: str
    email: str
    phone: str
    location: str
    summary: str
    experience: List[Experience]
    education: List[Education]
    skills: List[Skill]
    achievements: List[str]
    certifications: List[str]
    projects: List[str]
    raw_text: str


class ResumeParser:
    """Parses PDF resumes and extracts structured information."""
    
    def __init__(self):
        """Initialize the resume parser."""
        self.section_patterns = {
            'experience': r'(experience|work\s+history|professional\s+experience|employment)',
            'education': r'(education|academic|degree)',
            'skills': r'(skills|technical\s+skills|competencies)',
            'summary': r'(summary|profile|objective)',
            'achievements': r'(achievements|accomplishments|highlights)',
            'certifications': r'(certifications|certificates)',
            'projects': r'(projects|portfolio)'
        }
        
        self.skill_categories = {
            'programming': ['python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin'],
            'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'dynamodb'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins'],
            'ai_ml': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'nlp', 'computer vision'],
            'product': ['product management', 'agile', 'scrum', 'user research', 'a/b testing', 'analytics'],
            'design': ['ui/ux', 'figma', 'sketch', 'adobe', 'photoshop', 'illustrator'],
            'tools': ['git', 'jira', 'confluence', 'slack', 'zoom', 'notion', 'asana']
        }
    
    def parse_resume(self, pdf_path: str) -> ParsedResume:
        """Parse a PDF resume and extract structured information."""
        try:
            # Extract text from PDF
            text = self._extract_text_from_pdf(pdf_path)
            
            # Parse basic information
            name = self._extract_name(text)
            email = self._extract_email(text)
            phone = self._extract_phone(text)
            location = self._extract_location(text)
            
            # Parse sections
            sections = self._identify_sections(text)
            summary = self._extract_summary(sections)
            experience = self._extract_experience(sections)
            education = self._extract_education(sections)
            skills = self._extract_skills(sections)
            achievements = self._extract_achievements(sections)
            certifications = self._extract_certifications(sections)
            projects = self._extract_projects(sections)
            
            return ParsedResume(
                name=name,
                email=email,
                phone=phone,
                location=location,
                summary=summary,
                experience=experience,
                education=education,
                skills=skills,
                achievements=achievements,
                certifications=certifications,
                projects=projects,
                raw_text=text
            )
            
        except Exception as e:
            logger.error(f"Error parsing resume {pdf_path}: {e}")
            raise
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
        
        return text
    
    def _extract_name(self, text: str) -> str:
        """Extract name from resume text."""
        # Look for name patterns (usually at the top)
        lines = text.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line and len(line) < 50:  # Reasonable name length
                # Check if it looks like a name (no special chars, proper case)
                if re.match(r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*$', line):
                    return line
        
        return "Unknown"
    
    def _extract_email(self, text: str) -> str:
        """Extract email address from resume text."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else ""
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number from resume text."""
        phone_patterns = [
            r'\(\d{3}\)\s*\d{3}-\d{4}',  # (123) 456-7890
            r'\d{3}-\d{3}-\d{4}',        # 123-456-7890
            r'\d{10}',                    # 1234567890
            r'\+\d{1,3}\s*\d{3}\s*\d{3}\s*\d{4}'  # +1 123 456 7890
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return ""
    
    def _extract_location(self, text: str) -> str:
        """Extract location from resume text."""
        # Look for city, state patterns
        location_pattern = r'[A-Z][a-z]+,\s*[A-Z]{2}'
        match = re.search(location_pattern, text)
        return match.group(0) if match else ""
    
    def _identify_sections(self, text: str) -> Dict[str, ResumeSection]:
        """Identify and extract resume sections."""
        sections = {}
        lines = text.split('\n')
        
        current_section = None
        section_start = 0
        section_content = []
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Check if this line starts a new section
            for section_name, pattern in self.section_patterns.items():
                if re.search(pattern, line_lower):
                    # Save previous section if exists
                    if current_section and section_content:
                        sections[current_section] = ResumeSection(
                            title=current_section,
                            content='\n'.join(section_content),
                            start_line=section_start,
                            end_line=i-1
                        )
                    
                    # Start new section
                    current_section = section_name
                    section_start = i
                    section_content = [line]
                    break
            else:
                # Add line to current section
                if current_section:
                    section_content.append(line)
        
        # Save last section
        if current_section and section_content:
            sections[current_section] = ResumeSection(
                title=current_section,
                content='\n'.join(section_content),
                start_line=section_start,
                end_line=len(lines)-1
            )
        
        return sections
    
    def _extract_summary(self, sections: Dict[str, ResumeSection]) -> str:
        """Extract summary/profile section."""
        if 'summary' in sections:
            return sections['summary'].content
        return ""
    
    def _extract_experience(self, sections: Dict[str, ResumeSection]) -> List[Experience]:
        """Extract work experience entries."""
        experiences = []
        
        if 'experience' not in sections:
            return experiences
        
        content = sections['experience'].content
        lines = content.split('\n')
        
        current_experience = None
        current_company = ""
        current_title = ""
        current_duration = ""
        current_location = ""
        current_description = []
        current_achievements = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for company/title patterns
            company_pattern = r'^([A-Z][A-Za-z\s&]+)$'
            title_pattern = r'^([A-Z][a-z\s]+(?:Manager|Director|Lead|Engineer|Developer|Analyst))'
            duration_pattern = r'(\d{4}\s*[-–]\s*\d{4}|\d{4}\s*[-–]\s*Present|Present)'
            
            company_match = re.search(company_pattern, line)
            title_match = re.search(title_pattern, line)
            duration_match = re.search(duration_pattern, line)
            
            if company_match:
                # Save previous experience if exists
                if current_experience:
                    experiences.append(current_experience)
                
                # Start new experience
                current_company = company_match.group(1).strip()
                current_title = ""
                current_duration = ""
                current_location = ""
                current_description = []
                current_achievements = []
                
            elif title_match:
                current_title = title_match.group(1).strip()
                
            elif duration_match:
                current_duration = duration_match.group(1).strip()
                
            elif line.startswith('•') or line.startswith('-'):
                # Achievement bullet point
                achievement = line[1:].strip()
                current_achievements.append(achievement)
                
            else:
                # Regular description line
                current_description.append(line)
        
        # Add last experience
        if current_company:
            current_experience = Experience(
                company=current_company,
                title=current_title,
                duration=current_duration,
                location=current_location,
                description=current_description,
                achievements=current_achievements,
                skills_used=self._extract_skills_from_text(' '.join(current_description + current_achievements))
            )
            experiences.append(current_experience)
        
        return experiences
    
    def _extract_education(self, sections: Dict[str, ResumeSection]) -> List[Education]:
        """Extract education entries."""
        education = []
        
        if 'education' not in sections:
            return education
        
        content = sections['education'].content
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for education patterns
            institution_pattern = r'^([A-Z][A-Za-z\s&]+)$'
            degree_pattern = r'([A-Z][a-z]+(?:\s+of\s+[A-Z][a-z]+)?)'
            
            institution_match = re.search(institution_pattern, line)
            degree_match = re.search(degree_pattern, line)
            
            if institution_match:
                education.append(Education(
                    institution=institution_match.group(1).strip(),
                    degree="",
                    field="",
                    duration="",
                    location=""
                ))
        
        return education
    
    def _extract_skills(self, sections: Dict[str, ResumeSection]) -> List[Skill]:
        """Extract skills from resume."""
        skills = []
        
        if 'skills' not in sections:
            return skills
        
        content = sections['skills'].content
        text = content.lower()
        
        # Extract skills by category
        for category, skill_list in self.skill_categories.items():
            for skill in skill_list:
                if skill.lower() in text:
                    # Determine proficiency based on context
                    proficiency = self._determine_proficiency(text, skill)
                    skills.append(Skill(
                        name=skill,
                        category=category,
                        proficiency=proficiency
                    ))
        
        return skills
    
    def _extract_achievements(self, sections: Dict[str, ResumeSection]) -> List[str]:
        """Extract achievements from resume."""
        achievements = []
        
        if 'achievements' in sections:
            content = sections['achievements'].content
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line.startswith('•') or line.startswith('-')):
                    achievements.append(line[1:].strip())
        
        return achievements
    
    def _extract_certifications(self, sections: Dict[str, ResumeSection]) -> List[str]:
        """Extract certifications from resume."""
        certifications = []
        
        if 'certifications' in sections:
            content = sections['certifications'].content
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line:
                    certifications.append(line)
        
        return certifications
    
    def _extract_projects(self, sections: Dict[str, ResumeSection]) -> List[str]:
        """Extract projects from resume."""
        projects = []
        
        if 'projects' in sections:
            content = sections['projects'].content
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line:
                    projects.append(line)
        
        return projects
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills mentioned in text."""
        skills = []
        text_lower = text.lower()
        
        for category, skill_list in self.skill_categories.items():
            for skill in skill_list:
                if skill.lower() in text_lower:
                    skills.append(skill)
        
        return skills
    
    def _determine_proficiency(self, text: str, skill: str) -> str:
        """Determine skill proficiency level based on context."""
        text_lower = text.lower()
        skill_lower = skill.lower()
        
        # Look for proficiency indicators
        if any(word in text_lower for word in ['expert', 'advanced', 'senior', 'lead']):
            return 'expert'
        elif any(word in text_lower for word in ['intermediate', 'mid-level', 'experienced']):
            return 'intermediate'
        elif any(word in text_lower for word in ['beginner', 'basic', 'learning']):
            return 'beginner'
        else:
            return 'intermediate'  # Default assumption
    
    def get_resume_summary(self, parsed_resume: ParsedResume) -> Dict[str, Any]:
        """Get a summary of the parsed resume for the agent."""
        return {
            'name': parsed_resume.name,
            'email': parsed_resume.email,
            'location': parsed_resume.location,
            'summary': parsed_resume.summary,
            'total_experience': len(parsed_resume.experience),
            'companies': [exp.company for exp in parsed_resume.experience],
            'titles': [exp.title for exp in parsed_resume.experience],
            'skills': [skill.name for skill in parsed_resume.skills],
            'skill_categories': list(set([skill.category for skill in parsed_resume.skills])),
            'achievements_count': len(parsed_resume.achievements),
            'education_count': len(parsed_resume.education),
            'certifications_count': len(parsed_resume.certifications),
            'projects_count': len(parsed_resume.projects)
        }
    
    def get_relevant_experience(self, parsed_resume: ParsedResume, job_keywords: List[str]) -> List[Experience]:
        """Get experience entries relevant to the job keywords."""
        relevant_experience = []
        
        for exp in parsed_resume.experience:
            # Check if experience matches job keywords
            exp_text = f"{exp.company} {exp.title} {' '.join(exp.description)} {' '.join(exp.achievements)}"
            exp_text_lower = exp_text.lower()
            
            for keyword in job_keywords:
                if keyword.lower() in exp_text_lower:
                    relevant_experience.append(exp)
                    break
        
        return relevant_experience
    
    def get_relevant_skills(self, parsed_resume: ParsedResume, job_keywords: List[str]) -> List[Skill]:
        """Get skills relevant to the job keywords."""
        relevant_skills = []
        
        for skill in parsed_resume.skills:
            for keyword in job_keywords:
                if keyword.lower() in skill.name.lower():
                    relevant_skills.append(skill)
                    break
        
        return relevant_skills


if __name__ == "__main__":
    # Test the resume parser
    parser = ResumeParser()
    
    # Test with your resume
    try:
        parsed = parser.parse_resume("Peter Spannagle-Resume.pdf")
        print("Resume parsed successfully!")
        print(f"Name: {parsed.name}")
        print(f"Email: {parsed.email}")
        print(f"Experience entries: {len(parsed.experience)}")
        print(f"Skills: {len(parsed.skills)}")
        print(f"Achievements: {len(parsed.achievements)}")
        
        summary = parser.get_resume_summary(parsed)
        print(f"Companies: {summary['companies']}")
        print(f"Skills: {summary['skills']}")
        
    except Exception as e:
        print(f"Error parsing resume: {e}") 