#!/usr/bin/env python3
"""
Script to update cover letter agent to use LLM parsing
"""

import re

def update_parse_job_description():
    """Update the parse_job_description method to use LLM parser."""
    
    with open('agents/cover_letter_agent.py', 'r') as f:
        content = f.read()
    
    # Find the first parse_job_description method
    pattern = r'def parse_job_description\(self, job_text: str\) -> JobDescription:\s*"""Parse and analyze a job description\."""\s*# Start performance monitoring\s*monitor = get_performance_monitor\(\)\s*monitor\.start_timer\("job_parsing"\)\s*logger\.info\("Parsing job description\.\.\."\)\s*# Extract basic information\s*company_name = self\._extract_company_name\(job_text\)\s*job_title = self\._extract_job_title\(job_text\)\s*keywords = self\._extract_keywords\(job_text\)\s*job_type = self\._classify_job_type\(job_text\)\s*# Calculate score\s*score = self\._calculate_job_score\(job_text, keywords\)\s*# Determine go/no-go\s*go_no_go = self\._evaluate_go_no_go\(job_text, keywords, score\)\s*# Extract additional information\s*extracted_info = \{\s*"requirements": self\._extract_requirements\(job_text\),\s*"responsibilities": self\._extract_responsibilities\(job_text\),\s*"company_info": self\._extract_company_info\(job_text\),\s*\}\s*# Evaluate job targeting\s*targeting = self\._evaluate_job_targeting\(job_text, job_title, extracted_info\)\s*# End performance monitoring\s*monitor\.end_timer\("job_parsing"\)\s*return JobDescription\(\s*raw_text=job_text,\s*company_name=company_name,\s*job_title=job_title,\s*keywords=keywords,\s*job_type=job_type,\s*score=score,\s*go_no_go=go_no_go,\s*extracted_info=extracted_info,\s*targeting=targeting,\s*\)'
    
    replacement = '''def parse_job_description(self, job_text: str) -> JobDescription:
        """Parse and analyze a job description using LLM parser."""
        # Start performance monitoring
        monitor = get_performance_monitor()
        monitor.start_timer("job_parsing")

        logger.info("Parsing job description...")

        # Use LLM parser instead of manual parsing
        from agents.job_parser_llm import JobParserLLM
        
        try:
            llm_parser = JobParserLLM()
            parsed_data = llm_parser.parse_job_description(job_text)
            
            # Extract information from LLM parser result
            company_name = parsed_data.get('company_name', 'Unknown')
            job_title = parsed_data.get('job_title', 'Product Manager')
            inferred_level = parsed_data.get('inferred_level', 'L3')
            inferred_role_type = parsed_data.get('inferred_role_type', 'generalist')
            
            # Extract keywords from LLM result
            keywords = []
            if 'key_requirements' in parsed_data:
                keywords.extend(parsed_data['key_requirements'])
            if 'required_competencies' in parsed_data:
                keywords.extend(list(parsed_data['required_competencies'].keys()))
            
            # Add inferred level and role type to keywords
            keywords.extend([inferred_level, inferred_role_type])
            
            # Classify job type based on inferred role type
            job_type = inferred_role_type if inferred_role_type != 'generalist' else 'general'
            
            # Calculate score using existing logic
            score = self._calculate_job_score(job_text, keywords)
            
            # Determine go/no-go
            go_no_go = self._evaluate_go_no_go(job_text, keywords, score)
            
            # Extract additional information from LLM result
            extracted_info = {
                "requirements": parsed_data.get('key_requirements', []),
                "responsibilities": [],  # LLM parser doesn't extract this separately
                "company_info": parsed_data.get('company_info', {}),
                "job_context": parsed_data.get('job_context', {}),
                "inferred_level": inferred_level,
                "inferred_role_type": inferred_role_type,
                "required_competencies": parsed_data.get('required_competencies', {}),
                "confidence": parsed_data.get('confidence', 0.0),
                "notes": parsed_data.get('notes', '')
            }
            
            # Evaluate job targeting
            targeting = self._evaluate_job_targeting(job_text, job_title, extracted_info)
            
            # End performance monitoring
            monitor.end_timer("job_parsing")
            
            return JobDescription(
                raw_text=job_text,
                company_name=company_name,
                job_title=job_title,
                keywords=keywords,
                job_type=job_type,
                score=score,
                go_no_go=go_no_go,
                extracted_info=extracted_info,
                targeting=targeting,
            )
            
        except Exception as e:
            logger.warning(f"LLM parsing failed: {e}. Falling back to manual parsing.")
            # Fallback to original manual parsing
            return self._parse_job_description_manual(job_text)
    
    def _parse_job_description_manual(self, job_text: str) -> JobDescription:
        """Original manual parsing method as fallback."""
        # Start performance monitoring
        monitor = get_performance_monitor()
        monitor.start_timer("job_parsing")

        logger.info("Parsing job description (manual fallback)...")

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
            "requirements": self._extract_requirements(job_text),
            "responsibilities": self._extract_responsibilities(job_text),
            "company_info": self._extract_company_info(job_text),
        }

        # Evaluate job targeting
        targeting = self._evaluate_job_targeting(job_text, job_title, extracted_info)

        # End performance monitoring
        monitor.end_timer("job_parsing")

        return JobDescription(
            raw_text=job_text,
            company_name=company_name,
            job_title=job_title,
            keywords=keywords,
            job_type=job_type,
            score=score,
            go_no_go=go_no_go,
            extracted_info=extracted_info,
            targeting=targeting,
        )'''
    
    # Replace the first occurrence
    updated_content = re.sub(pattern, replacement, content, count=1)
    
    with open('agents/cover_letter_agent.py', 'w') as f:
        f.write(updated_content)
    
    print("Updated cover letter agent to use LLM parser")

if __name__ == "__main__":
    update_parse_job_description() 