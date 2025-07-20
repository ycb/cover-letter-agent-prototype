#!/usr/bin/env python3
"""
Work History Context Enhancement Module
=====================================

Enhances case study selection by preserving parent-child work history relationships.
Implements tag inheritance and semantic tag matching to improve context preservation.
"""

import yaml
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class WorkHistoryEntry:
    """Represents a work history entry with company and role context."""
    company: str
    role: str
    duration: Optional[str]
    summary: str
    achievements: List[str]
    tags: List[str]
    detailed_examples: List[Dict[str, Any]]


@dataclass
class EnhancedCaseStudy:
    """Represents a case study with enhanced context from work history."""
    case_study_id: str
    original_tags: List[str]
    inherited_tags: List[str]
    semantic_tags: List[str]
    enhanced_tags: List[str]
    parent_context: Dict[str, Any]
    confidence_score: float
    tag_provenance: Dict[str, str]  # Maps tag to source: "direct", "inherited", "semantic"
    tag_weights: Dict[str, float]   # Maps tag to weight: 1.0 for direct, 0.6 for inherited, 0.8 for semantic


class WorkHistoryContextEnhancer:
    """Enhances case studies with work history context and tag inheritance."""
    
    def __init__(self, work_history_file: str = "users/peter/work_history.yaml"):
        """Initialize the context enhancer with work history data."""
        self.work_history_file = work_history_file
        self.work_history = self._load_work_history()
        self.semantic_tag_mappings = self._create_semantic_mappings()
        
        # Tag suppression rules - tags that should not be inherited
        self.suppressed_inheritance_tags = {
            'frontend', 'backend', 'mobile', 'web', 'marketing', 'sales',
            'finance', 'hr', 'legal', 'operations', 'support', 'customer_service',
            'design', 'ux', 'ui', 'graphic_design', 'content', 'copywriting',
            'social_media', 'seo', 'ppc', 'advertising', 'pr', 'communications'
        }
        
    def _load_work_history(self) -> List[WorkHistoryEntry]:
        """Load work history from YAML file."""
        try:
            with open(self.work_history_file, 'r') as f:
                data = yaml.safe_load(f)
            
            entries = []
            # Handle the nested structure where work history is under resume entries
            for resume_entry in data:
                if 'examples' in resume_entry:
                    for example in resume_entry['examples']:
                        if 'company' in example:
                            # Extract tags from achievements and detailed examples
                            achievement_tags = self._extract_tags_from_achievements(example.get('achievements', []))
                            detailed_tags = []
                            
                            # Extract tags from detailed examples
                            for detailed in example.get('detailed_examples', []):
                                detailed_tags.extend(detailed.get('tags', []))
                            
                            # Combine all tags
                            all_tags = list(set(achievement_tags + detailed_tags))
                            
                            work_entry = WorkHistoryEntry(
                                company=example['company'],
                                role=example.get('title', ''),
                                duration=example.get('start_date', '') + ' - ' + example.get('end_date', ''),
                                summary=example.get('description', ''),
                                achievements=example.get('achievements', []),
                                tags=all_tags,
                                detailed_examples=example.get('detailed_examples', [])
                            )
                            entries.append(work_entry)
                            logger.debug(f"Loaded work history for: {work_entry.company} with {len(all_tags)} tags")
            
            logger.info(f"Loaded {len(entries)} work history entries")
            return entries
            
        except Exception as e:
            logger.error(f"Failed to load work history: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def _extract_tags_from_achievements(self, achievements: List[str]) -> List[str]:
        """Extract relevant tags from achievement descriptions."""
        tags = []
        for achievement in achievements:
            # Handle both string and dictionary achievements
            if isinstance(achievement, dict):
                achievement_text = achievement.get('text', '')
            else:
                achievement_text = str(achievement)
            
            achievement_lower = achievement_text.lower()
            
            # Industry tags
            if any(word in achievement_lower for word in ['solar', 'energy', 'clean']):
                tags.append('cleantech')
            if any(word in achievement_lower for word in ['ai', 'ml', 'machine learning']):
                tags.append('ai_ml')
            if any(word in achievement_lower for word in ['mobile', 'app']):
                tags.append('mobile')
            if any(word in achievement_lower for word in ['startup', 'early', '0-1']):
                tags.append('startup')
            if any(word in achievement_lower for word in ['enterprise', 'b2b']):
                tags.append('enterprise')
            if any(word in achievement_lower for word in ['consumer', 'b2c']):
                tags.append('consumer')
            
            # Role tags
            if any(word in achievement_lower for word in ['lead', 'leadership', 'team']):
                tags.append('leadership')
            if any(word in achievement_lower for word in ['product', 'strategy']):
                tags.append('product_strategy')
            if any(word in achievement_lower for word in ['growth', 'revenue']):
                tags.append('growth')
            if any(word in achievement_lower for word in ['platform', 'system']):
                tags.append('platform')
            
            # Process tags
            if any(word in achievement_lower for word in ['user', 'customer', 'research']):
                tags.append('user_research')
            if any(word in achievement_lower for word in ['data', 'analytics']):
                tags.append('data_driven')
            if any(word in achievement_lower for word in ['cross', 'functional']):
                tags.append('cross_functional')
        
        return list(set(tags))  # Remove duplicates
    
    def _create_semantic_mappings(self) -> Dict[str, List[str]]:
        """Create semantic tag mappings for improved matching."""
        return {
            'internal_tools': ['platform', 'enterprise_systems', 'productivity', 'operations'],
            'platform': ['internal_tools', 'enterprise_systems', 'infrastructure'],
            'enterprise_systems': ['internal_tools', 'platform', 'b2b'],
            'ai_ml': ['machine_learning', 'artificial_intelligence', 'nlp', 'automation'],
            'machine_learning': ['ai_ml', 'artificial_intelligence', 'data_science'],
            'cleantech': ['energy', 'sustainability', 'renewable', 'climate'],
            'energy': ['cleantech', 'sustainability', 'renewable'],
            'startup': ['early_stage', 'founding', '0_to_1', 'seed'],
            'early_stage': ['startup', 'founding', '0_to_1'],
            'enterprise': ['b2b', 'large_scale', 'corporate'],
            'b2b': ['enterprise', 'business_to_business'],
            'consumer': ['b2c', 'user_experience', 'mobile'],
            'b2c': ['consumer', 'user_experience'],
            'leadership': ['management', 'team_lead', 'people_development'],
            'management': ['leadership', 'team_lead', 'people_development'],
            'growth': ['scaling', 'expansion', 'revenue_growth'],
            'scaling': ['growth', 'expansion', 'scaleup'],
            'product_strategy': ['product_vision', 'roadmap', 'strategy'],
            'user_research': ['customer_research', 'user_experience', 'discovery'],
            'data_driven': ['analytics', 'metrics', 'data_analysis'],
            'cross_functional': ['collaboration', 'teamwork', 'alignment']
        }
    
    def find_parent_work_history(self, case_study_id: str) -> Optional[WorkHistoryEntry]:
        """Find the parent work history entry for a case study."""
        # Map case study IDs to companies
        case_study_to_company = {
            'enact': 'Enact Systems Inc.',
            'aurora': 'Aurora Solar',
            'meta': 'Meta',
            'samsung': 'Samsung Research America',
            'spatialthink': 'SpatialThink'
        }
        
        company = case_study_to_company.get(case_study_id.lower())
        if not company:
            logger.warning(f"No company mapping found for case study: {case_study_id}")
            return None
        
        # Find matching work history entry
        for entry in self.work_history:
            if isinstance(entry.company, str) and entry.company.lower() == company.lower():
                return entry
        
        logger.warning(f"No work history found for company: {company}")
        logger.debug(f"Available companies: {[e.company for e in self.work_history]}")
        return None
    
    def enhance_case_study_context(self, case_study: Dict[str, Any]) -> EnhancedCaseStudy:
        """Enhance a case study with work history context and tag inheritance."""
        case_study_id = case_study.get('id', case_study.get('name', ''))
        original_tags = case_study.get('tags', [])
        
        # Initialize provenance and weights for original tags
        tag_provenance = {tag: "direct" for tag in original_tags}
        tag_weights = {tag: 1.0 for tag in original_tags}
        
        # Find parent work history
        parent_entry = self.find_parent_work_history(case_study_id)
        
        if not parent_entry:
            # No parent found, return original case study
            return EnhancedCaseStudy(
                case_study_id=case_study_id,
                original_tags=original_tags,
                inherited_tags=[],
                semantic_tags=[],
                enhanced_tags=original_tags,
                parent_context={},
                confidence_score=0.0,
                tag_provenance=tag_provenance,
                tag_weights=tag_weights
            )
        
        # Inherit relevant tags from parent (with suppression rules)
        inherited_tags = self._inherit_relevant_tags(original_tags, parent_entry.tags)
        
        # Add semantic tags based on parent context
        semantic_tags = self._add_semantic_tags(original_tags, parent_entry)
        
        # Update provenance and weights for inherited tags
        for tag in inherited_tags:
            tag_provenance[tag] = "inherited"
            tag_weights[tag] = 0.6  # Lower weight for inherited tags
        
        # Update provenance and weights for semantic tags
        for tag in semantic_tags:
            if tag not in tag_provenance:  # Don't override direct tags
                tag_provenance[tag] = "semantic"
                tag_weights[tag] = 0.8  # Medium weight for semantic tags
        
        # Combine all tags
        enhanced_tags = list(set(original_tags + inherited_tags + semantic_tags))
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(original_tags, inherited_tags, semantic_tags)
        
        return EnhancedCaseStudy(
            case_study_id=case_study_id,
            original_tags=original_tags,
            inherited_tags=inherited_tags,
            semantic_tags=semantic_tags,
            enhanced_tags=enhanced_tags,
            parent_context={
                'company': parent_entry.company,
                'role': parent_entry.role,
                'summary': parent_entry.summary,
                'achievements': parent_entry.achievements
            },
            confidence_score=confidence_score,
            tag_provenance=tag_provenance,
            tag_weights=tag_weights
        )
    
    def _inherit_relevant_tags(self, case_study_tags: List[str], parent_tags: List[str]) -> List[str]:
        """Inherit relevant tags from parent work history with suppression rules."""
        inherited = []
        
        # Inherit industry context (high confidence)
        if 'cleantech' in parent_tags and not any(tag in case_study_tags for tag in ['cleantech', 'energy']):
            inherited.append('cleantech')
        
        # Inherit company stage context (high confidence)
        if 'startup' in parent_tags and not any(tag in case_study_tags for tag in ['startup', 'early_stage']):
            inherited.append('startup')
        
        # Inherit business model context (medium confidence)
        if 'enterprise' in parent_tags and not any(tag in case_study_tags for tag in ['enterprise', 'b2b']):
            inherited.append('enterprise')
        elif 'consumer' in parent_tags and not any(tag in case_study_tags for tag in ['consumer', 'b2c']):
            inherited.append('consumer')
        
        # Inherit role context (high confidence)
        if 'leadership' in parent_tags and not 'leadership' in case_study_tags:
            inherited.append('leadership')
        
        # Inherit process context (medium confidence)
        if 'data_driven' in parent_tags and not 'data_driven' in case_study_tags:
            inherited.append('data_driven')
        if 'cross_functional' in parent_tags and not 'cross_functional' in case_study_tags:
            inherited.append('cross_functional')
        
        # Apply suppression rules - filter out tags that shouldn't be inherited
        inherited = [tag for tag in inherited if tag not in self.suppressed_inheritance_tags]
        
        return inherited
    
    def _add_semantic_tags(self, case_study_tags: List[str], parent_entry: WorkHistoryEntry) -> List[str]:
        """Add semantic tags based on parent context and semantic mappings."""
        semantic_tags = []
        
        # Add semantic matches for existing tags
        for tag in case_study_tags:
            if tag in self.semantic_tag_mappings:
                semantic_tags.extend(self.semantic_tag_mappings[tag])
        
        # Add semantic tags based on parent achievements
        for achievement in parent_entry.achievements:
            # Handle both string and dictionary achievements
            if isinstance(achievement, dict):
                achievement_text = achievement.get('text', '')
            else:
                achievement_text = str(achievement)
            
            achievement_lower = achievement_text.lower()
            
            # Map achievement keywords to semantic tags
            if any(word in achievement_lower for word in ['platform', 'system', 'infrastructure']):
                semantic_tags.append('platform')
            if any(word in achievement_lower for word in ['internal', 'tools', 'productivity']):
                semantic_tags.append('internal_tools')
            if any(word in achievement_lower for word in ['ai', 'ml', 'machine learning']):
                semantic_tags.append('ai_ml')
            if any(word in achievement_lower for word in ['user', 'experience', 'ux']):
                semantic_tags.append('user_experience')
            if any(word in achievement_lower for word in ['growth', 'scaling', 'expansion']):
                semantic_tags.append('growth')
        
        return list(set(semantic_tags))  # Remove duplicates
    
    def _calculate_confidence_score(self, original_tags: List[str], inherited_tags: List[str], semantic_tags: List[str]) -> float:
        """Calculate confidence score for the enhancement."""
        base_score = 0.5
        
        # Bonus for inherited tags (indicates good parent-child relationship)
        if inherited_tags:
            base_score += 0.2
        
        # Bonus for semantic tags (indicates good semantic matching)
        if semantic_tags:
            base_score += 0.2
        
        # Bonus for having both original and enhanced tags
        if original_tags and (inherited_tags or semantic_tags):
            base_score += 0.1
        
        return min(base_score, 1.0)  # Cap at 1.0
    
    def enhance_case_studies_batch(self, case_studies: List[Dict[str, Any]]) -> List[EnhancedCaseStudy]:
        """Enhance multiple case studies with work history context."""
        enhanced = []
        
        for case_study in case_studies:
            enhanced_case_study = self.enhance_case_study_context(case_study)
            enhanced.append(enhanced_case_study)
            
            logger.info(f"Enhanced {enhanced_case_study.case_study_id}:")
            logger.info(f"  Original tags: {enhanced_case_study.original_tags}")
            logger.info(f"  Inherited tags: {enhanced_case_study.inherited_tags}")
            logger.info(f"  Semantic tags: {enhanced_case_study.semantic_tags}")
            logger.info(f"  Enhanced tags: {enhanced_case_study.enhanced_tags}")
            logger.info(f"  Confidence: {enhanced_case_study.confidence_score:.2f}")
        
        return enhanced


def test_work_history_context_enhancement():
    """Test the work history context enhancement functionality."""
    print("🧪 Testing Work History Context Enhancement...")
    
    enhancer = WorkHistoryContextEnhancer()
    
    # Test case studies
    test_case_studies = [
        {
            'id': 'enact',
            'name': 'Enact 0 to 1 Case Study',
            'tags': ['growth', 'consumer', 'clean_energy', 'user_experience']
        },
        {
            'id': 'aurora',
            'name': 'Aurora Solar Growth Case Study',
            'tags': ['growth', 'B2B', 'clean_energy', 'scaling']
        },
        {
            'id': 'meta',
            'name': 'Meta Explainable AI Case Study',
            'tags': ['AI', 'ML', 'trust', 'internal_tools', 'explainable']
        }
    ]
    
    enhanced = enhancer.enhance_case_studies_batch(test_case_studies)
    
    print("\n📊 Results:")
    for enhanced_case_study in enhanced:
        print(f"\n  {enhanced_case_study.case_study_id.upper()}:")
        print(f"    Original: {enhanced_case_study.original_tags}")
        print(f"    Inherited: {enhanced_case_study.inherited_tags}")
        print(f"    Semantic: {enhanced_case_study.semantic_tags}")
        print(f"    Enhanced: {enhanced_case_study.enhanced_tags}")
        print(f"    Confidence: {enhanced_case_study.confidence_score:.2f}")
        
        if enhanced_case_study.parent_context:
            print(f"    Parent: {enhanced_case_study.parent_context['company']}")
    
    print("\n✅ Work History Context Enhancement test completed!")


if __name__ == "__main__":
    test_work_history_context_enhancement() 