"""
Phase 7A: Core Gap Detection Module

Identifies missing skills, industries, roles, and company stages
based on job description requirements vs user's available case studies.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Gap:
    """Represents a detected gap in user's experience."""
    tag: str
    category: str
    priority: str  # high, medium, low
    job_requirement: str
    user_coverage: List[str]  # existing tags that partially cover this gap
    confidence: float  # 0.0 to 1.0


@dataclass
class ContentMatch:
    """Represents a potential match for filling a gap."""
    case_study_id: str
    case_study_name: str
    match_type: str  # direct, adjacent, partial
    confidence: float  # 0.0 to 1.0
    rationale: str
    relevant_tags: List[str]


class GapDetector:
    """Core gap detection and content matching system."""
    
    def __init__(self, config_path: str = "config/tag_schema.yaml"):
        """Initialize gap detector with tag schema."""
        self.config_path = Path(config_path)
        self.tag_schema = self._load_tag_schema()
        self.gap_priorities = self.tag_schema.get('gap_priorities', {})
        self.tag_relationships = self.tag_schema.get('tag_relationships', {})
    
    def _load_tag_schema(self) -> Dict:
        """Load the unified tag schema."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: Tag schema not found at {self.config_path}")
            return {}
    
    def detect_gaps(
        self, 
        jd_tags: List[str], 
        user_tags: List[str]
    ) -> List[Gap]:
        """
        Detect gaps between job requirements and user's experience.
        
        Args:
            jd_tags: Tags from job description
            user_tags: Tags from user's case studies
            
        Returns:
            List of detected gaps with priority and coverage info
        """
        gaps = []
        user_tag_set = set(user_tags)
        
        # Check each job requirement tag
        for jd_tag in jd_tags:
            if jd_tag not in user_tag_set:
                # Check if user has adjacent/related tags
                adjacent_tags = self._find_adjacent_tags(jd_tag, user_tag_set)
                
                # Determine priority
                priority = self._determine_priority(jd_tag)
                
                # Calculate confidence based on coverage
                confidence = self._calculate_coverage_confidence(jd_tag, adjacent_tags)
                
                gap = Gap(
                    tag=jd_tag,
                    category=self._categorize_tag(jd_tag),
                    priority=priority,
                    job_requirement=jd_tag,
                    user_coverage=adjacent_tags,
                    confidence=confidence
                )
                gaps.append(gap)
        
        # Sort by priority and confidence
        gaps.sort(key=lambda g: (self._priority_score(g.priority), g.confidence), reverse=True)
        
        return gaps
    
    def _find_adjacent_tags(self, target_tag: str, user_tags: set) -> List[str]:
        """Find tags in user's experience that are adjacent to the target tag."""
        adjacent = []
        
        # Check direct relationships
        if target_tag in self.tag_relationships:
            for related_tag in self.tag_relationships[target_tag]:
                if related_tag in user_tags:
                    adjacent.append(related_tag)
        
        # Check reverse relationships
        for source_tag, related_tags in self.tag_relationships.items():
            if target_tag in related_tags and source_tag in user_tags:
                adjacent.append(source_tag)
        
        return adjacent
    
    def _determine_priority(self, tag: str) -> str:
        """Determine priority of a gap based on tag schema."""
        for priority, tags in self.gap_priorities.items():
            if tag in tags:
                return priority
        return "low"  # Default to low priority
    
    def _priority_score(self, priority: str) -> int:
        """Convert priority string to numeric score for sorting."""
        scores = {"high": 3, "medium": 2, "low": 1}
        return scores.get(priority, 0)
    
    def _categorize_tag(self, tag: str) -> str:
        """Categorize a tag into skills, industries, roles, etc."""
        categories = self.tag_schema.get('tag_categories', {})
        
        for category, subcategories in categories.items():
            if isinstance(subcategories, dict):
                for subcategory, tags in subcategories.items():
                    if tag in tags:
                        return f"{category}.{subcategory}"
            elif isinstance(subcategories, list) and tag in subcategories:
                return category
        
        return "other"
    
    def _calculate_coverage_confidence(self, target_tag: str, adjacent_tags: List[str]) -> float:
        """Calculate confidence that adjacent tags cover the gap."""
        if not adjacent_tags:
            return 0.0
        
        # Simple heuristic: more adjacent tags = higher confidence
        # In a more sophisticated version, this could use LLM to assess coverage
        base_confidence = min(len(adjacent_tags) * 0.2, 0.8)
        
        # Boost confidence for closely related tags
        if target_tag in self.tag_relationships:
            direct_relations = self.tag_relationships[target_tag]
            direct_matches = [tag for tag in adjacent_tags if tag in direct_relations]
            if direct_matches:
                base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def match_existing_content(
        self, 
        gap: Gap, 
        case_studies: List[Dict]
    ) -> List[ContentMatch]:
        """
        Find existing case studies that could fill a gap.
        
        Args:
            gap: The gap to fill
            case_studies: Available case studies
            
        Returns:
            Ranked list of potential matches
        """
        matches = []
        
        for case_study in case_studies:
            case_study_tags = case_study.get('tags', [])
            
            # Check for direct match
            if gap.tag in case_study_tags:
                match = ContentMatch(
                    case_study_id=case_study.get('id', 'unknown'),
                    case_study_name=case_study.get('name', 'Unknown'),
                    match_type='direct',
                    confidence=1.0,
                    rationale=f"Direct match for {gap.tag}",
                    relevant_tags=[gap.tag]
                )
                matches.append(match)
                continue
            
            # Check for adjacent matches
            adjacent_tags = self._find_adjacent_tags(gap.tag, set(case_study_tags))
            if adjacent_tags:
                # Calculate confidence based on number and relevance of adjacent tags
                confidence = min(len(adjacent_tags) * 0.3, 0.9)
                
                match = ContentMatch(
                    case_study_id=case_study.get('id', 'unknown'),
                    case_study_name=case_study.get('name', 'Unknown'),
                    match_type='adjacent',
                    confidence=confidence,
                    rationale=f"Adjacent match: {', '.join(adjacent_tags)}",
                    relevant_tags=adjacent_tags
                )
                matches.append(match)
        
        # Sort by confidence and match type
        matches.sort(key=lambda m: (m.match_type == 'direct', m.confidence), reverse=True)
        
        return matches
    
    def get_gap_summary(self, gaps: List[Gap]) -> Dict:
        """Generate a summary of detected gaps."""
        summary = {
            'total_gaps': len(gaps),
            'high_priority': len([g for g in gaps if g.priority == 'high']),
            'medium_priority': len([g for g in gaps if g.priority == 'medium']),
            'low_priority': len([g for g in gaps if g.priority == 'low']),
            'categories': {},
            'top_gaps': []
        }
        
        # Categorize gaps
        for gap in gaps:
            category = gap.category.split('.')[0]  # Get main category
            if category not in summary['categories']:
                summary['categories'][category] = 0
            summary['categories'][category] += 1
        
        # Get top 5 gaps
        summary['top_gaps'] = [
            {
                'tag': gap.tag,
                'category': gap.category,
                'priority': gap.priority,
                'confidence': gap.confidence
            }
            for gap in gaps[:5]
        ]
        
        return summary


def test_gap_detection():
    """Test the gap detection system."""
    print("🧪 Testing Phase 7A: Core Gap Detection...")
    
    # Initialize gap detector
    detector = GapDetector()
    
    # Test data
    jd_tags = ['ai_ml', 'platform', 'enterprise', 'leadership', 'growth']
    user_tags = ['mobile', 'b2c', 'ux', 'data_analysis', 'team_lead']
    
    print(f"Job Description Tags: {jd_tags}")
    print(f"User Experience Tags: {user_tags}")
    
    # Detect gaps
    gaps = detector.detect_gaps(jd_tags, user_tags)
    
    print(f"\n📊 Gap Detection Results:")
    print(f"  Total gaps detected: {len(gaps)}")
    
    for gap in gaps:
        print(f"  - {gap.tag} ({gap.category}) - {gap.priority} priority")
        print(f"    Coverage: {gap.user_coverage} (confidence: {gap.confidence:.2f})")
    
    # Generate summary
    summary = detector.get_gap_summary(gaps)
    print(f"\n📈 Gap Summary:")
    print(f"  High priority: {summary['high_priority']}")
    print(f"  Medium priority: {summary['medium_priority']}")
    print(f"  Low priority: {summary['low_priority']}")
    print(f"  Categories: {summary['categories']}")
    
    # Test content matching
    test_case_studies = [
        {
            'id': 'meta_ai',
            'name': 'Meta AI Tools',
            'tags': ['ai_ml', 'platform', 'internal_tools', 'enterprise']
        },
        {
            'id': 'aurora_platform',
            'name': 'Aurora Platform',
            'tags': ['platform', 'b2b', 'enterprise', 'growth']
        }
    ]
    
    if gaps:
        top_gap = gaps[0]
        matches = detector.match_existing_content(top_gap, test_case_studies)
        
        print(f"\n🔍 Content Matching for '{top_gap.tag}':")
        for match in matches:
            print(f"  - {match.case_study_name}: {match.match_type} match")
            print(f"    Confidence: {match.confidence:.2f}")
            print(f"    Rationale: {match.rationale}")
    
    print(f"\n✅ Phase 7A: Core Gap Detection test completed!")


if __name__ == "__main__":
    test_gap_detection() 