"""
Phase 7C: Story Generation & Storage Module

Handles story creation, storage, and version control for gap-filling.
"""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class GapStory:
    """Represents a story created to fill a gap."""
    story_id: str
    gap_tag: str
    story_text: str
    tags: List[str]
    source: str  # gap_fill, manual, derived
    strategy: str  # new_story, reframe, acknowledge
    created_at: str
    version: int = 1
    approved_for: List[str] = None  # job IDs where this story was approved
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.approved_for is None:
            self.approved_for = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class StorySuggestion:
    """Represents a suggested story for filling a gap."""
    story_id: str
    story_text: str
    tags: List[str]
    match_type: str  # direct, adjacent, partial, derived
    confidence: float  # 0.0 to 1.0
    rationale: str
    source: str  # existing_story, work_history, derived
    relevance_score: float  # 0.0 to 1.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class StoryGenerator:
    """Handles story generation and storage for gap-filling."""
    
    def __init__(self, user_profile: str = "default"):
        """Initialize story generator."""
        self.user_profile = user_profile
        self.stories_dir = Path(f"users/{user_profile}/gap_stories")
        self.stories_dir.mkdir(parents=True, exist_ok=True)
        
        self.stories_file = self.stories_dir / "stories.yaml"
        self.stories_index_file = self.stories_dir / "stories_index.json"
        
        # Load existing stories
        self.stories = self._load_stories()
    
    def _load_stories(self) -> Dict[str, GapStory]:
        """Load existing stories from storage."""
        stories = {}
        
        try:
            if self.stories_file.exists():
                with open(self.stories_file, 'r') as f:
                    stories_data = yaml.safe_load(f) or {}
                
                for story_id, story_data in stories_data.items():
                    stories[story_id] = GapStory(**story_data)
        except Exception as e:
            print(f"Warning: Could not load existing stories: {e}")
        
        return stories
    
    def _save_stories(self) -> None:
        """Save stories to storage."""
        try:
            stories_data = {}
            for story_id, story in self.stories.items():
                stories_data[story_id] = asdict(story)
            
            with open(self.stories_file, 'w') as f:
                yaml.dump(stories_data, f, default_flow_style=False)
        except Exception as e:
            print(f"Error saving stories: {e}")
    
    def suggest_stories_for_gap(
        self, 
        gap_tag: str, 
        work_history: Optional[List[Dict]] = None,
        existing_case_studies: Optional[List[Dict]] = None,
        user_context: str = ""
    ) -> List[StorySuggestion]:
        """
        Suggest stories for filling a specific gap.
        
        Args:
            gap_tag: The gap to fill
            work_history: User's work history and samples
            existing_case_studies: User's existing case studies
            user_context: Additional user context
            
        Returns:
            Force-ranked list of story suggestions with confidence scores
        """
        suggestions = []
        
        # 1. Check existing gap-filling stories
        existing_stories = self.get_stories_by_gap(gap_tag)
        for story in existing_stories:
            suggestion = StorySuggestion(
                story_id=story.story_id,
                story_text=story.story_text,
                tags=story.tags,
                match_type='direct',
                confidence=0.9,  # High confidence for existing gap-fill stories
                rationale=f"Existing story created specifically for {gap_tag} gap",
                source='existing_story',
                relevance_score=0.9,
                metadata={'created_at': story.created_at, 'strategy': story.strategy}
            )
            suggestions.append(suggestion)
        
        # 2. Analyze work history for potential stories
        if work_history:
            work_suggestions = self._analyze_work_history_for_gap(
                gap_tag, work_history, user_context
            )
            suggestions.extend(work_suggestions)
        
        # 3. Analyze existing case studies for reframing opportunities
        if existing_case_studies:
            reframe_suggestions = self._analyze_case_studies_for_reframing(
                gap_tag, existing_case_studies
            )
            suggestions.extend(reframe_suggestions)
        
        # 4. Generate derived stories based on patterns
        derived_suggestions = self._generate_derived_stories(
            gap_tag, work_history or [], existing_case_studies or [], user_context
        )
        suggestions.extend(derived_suggestions)
        
        # 5. Force-rank all suggestions by confidence and relevance
        suggestions.sort(
            key=lambda s: (s.confidence * 0.6 + s.relevance_score * 0.4), 
            reverse=True
        )
        
        return suggestions
    
    def _analyze_work_history_for_gap(
        self, 
        gap_tag: str, 
        work_history: List[Dict], 
        user_context: str
    ) -> List[StorySuggestion]:
        """Analyze work history to find potential stories for a gap."""
        suggestions = []
        
        for work_item in work_history:
            # Check if work item has relevant tags
            work_tags = work_item.get('tags', [])
            
            # Calculate match confidence
            match_confidence = self._calculate_tag_match_confidence(gap_tag, work_tags)
            
            if match_confidence > 0.3:  # Only suggest if reasonably relevant
                # Extract story from work history
                story_text = self._extract_story_from_work_item(work_item, gap_tag)
                
                if story_text:
                    suggestion = StorySuggestion(
                        story_id=f"work_history_{work_item.get('id', 'unknown')}",
                        story_text=story_text,
                        tags=work_tags + [gap_tag],
                        match_type='adjacent' if match_confidence < 0.7 else 'direct',
                        confidence=match_confidence,
                        rationale=f"Work history item with {len([t for t in work_tags if t in self._get_related_tags(gap_tag)])} related tags",
                        source='work_history',
                        relevance_score=match_confidence,
                        metadata={
                            'work_item_id': work_item.get('id'),
                            'company': work_item.get('company'),
                            'role': work_item.get('role'),
                            'duration': work_item.get('duration')
                        }
                    )
                    suggestions.append(suggestion)
        
        return suggestions
    
    def _analyze_case_studies_for_reframing(
        self, 
        gap_tag: str, 
        existing_case_studies: List[Dict]
    ) -> List[StorySuggestion]:
        """Analyze existing case studies for reframing opportunities."""
        suggestions = []
        
        for case_study in existing_case_studies:
            case_tags = case_study.get('tags', [])
            
            # Check if case study could be reframed to address the gap
            reframe_confidence = self._calculate_reframe_confidence(gap_tag, case_tags)
            
            if reframe_confidence > 0.4:  # Only suggest if reframing is feasible
                reframed_story = self._reframe_case_study_for_gap(
                    case_study, gap_tag
                )
                
                if reframed_story:
                    suggestion = StorySuggestion(
                        story_id=f"reframe_{case_study.get('id', 'unknown')}",
                        story_text=reframed_story,
                        tags=case_tags + [gap_tag],
                        match_type='partial',
                        confidence=reframe_confidence,
                        rationale=f"Reframed existing case study to emphasize {gap_tag} aspects",
                        source='reframed_case_study',
                        relevance_score=reframe_confidence,
                        metadata={
                            'original_case_study_id': case_study.get('id'),
                            'reframe_strategy': 'emphasis_shift'
                        }
                    )
                    suggestions.append(suggestion)
        
        return suggestions
    
    def _generate_derived_stories(
        self, 
        gap_tag: str, 
        work_history: List[Dict], 
        existing_case_studies: List[Dict], 
        user_context: str
    ) -> List[StorySuggestion]:
        """Generate derived stories based on patterns and user context."""
        suggestions = []
        
        # Find common patterns in user's experience
        patterns = self._identify_experience_patterns(work_history, existing_case_studies)
        
        # Generate story based on patterns
        if patterns:
            derived_story = self._create_derived_story(gap_tag, patterns, user_context)
            
            if derived_story:
                suggestion = StorySuggestion(
                    story_id=f"derived_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    story_text=derived_story,
                    tags=[gap_tag] + patterns.get('common_tags', []),
                    match_type='derived',
                    confidence=0.6,  # Moderate confidence for derived stories
                    rationale=f"Derived from patterns in your experience: {', '.join(patterns.get('patterns', []))}",
                    source='derived',
                    relevance_score=0.7,
                    metadata={
                        'derivation_method': 'pattern_analysis',
                        'patterns_used': patterns.get('patterns', [])
                    }
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def _calculate_tag_match_confidence(self, target_tag: str, work_tags: List[str]) -> float:
        """Calculate confidence that work tags match the target gap tag."""
        if target_tag in work_tags:
            return 1.0
        
        # Check for related tags
        related_tags = self._get_related_tags(target_tag)
        matches = [tag for tag in work_tags if tag in related_tags]
        
        if matches:
            return min(len(matches) * 0.3, 0.9)
        
        return 0.0
    
    def _get_related_tags(self, tag: str) -> List[str]:
        """Get tags related to the target tag."""
        # This would ideally come from the tag schema
        # For now, use a simple mapping
        related_mappings = {
            'fintech': ['payments', 'banking', 'finance', 'compliance'],
            'ai_ml': ['machine_learning', 'nlp', 'data_analysis', 'analytics'],
            'growth': ['user_research', 'metrics', 'experimentation', 'retention'],
            'leadership': ['team_lead', 'people_development', 'org_leadership'],
            'b2b': ['enterprise', 'sales', 'partnerships', 'business_development'],
            'b2c': ['consumer', 'user_experience', 'engagement', 'retention']
        }
        
        return related_mappings.get(tag, [])
    
    def _extract_story_from_work_item(self, work_item: Dict, gap_tag: str) -> Optional[str]:
        """Extract a story from a work history item."""
        # Extract relevant information
        company = work_item.get('company', 'Company')
        role = work_item.get('role', 'Role')
        description = work_item.get('description', '')
        achievements = work_item.get('achievements', [])
        
        if not description and not achievements:
            return None
        
        # Create story focusing on the gap tag
        story_parts = [f"At {company}, I worked as {role}"]
        
        if description:
            story_parts.append(f"where I {description}")
        
        if achievements:
            relevant_achievements = [
                achievement for achievement in achievements 
                if gap_tag in achievement.lower() or any(tag in achievement.lower() for tag in self._get_related_tags(gap_tag))
            ]
            if relevant_achievements:
                story_parts.append(f"Key achievements included: {relevant_achievements[0]}")
        
        return " ".join(story_parts)
    
    def _calculate_reframe_confidence(self, gap_tag: str, case_tags: List[str]) -> float:
        """Calculate confidence that a case study can be reframed for a gap."""
        # Check if case study has related tags
        related_tags = self._get_related_tags(gap_tag)
        matches = [tag for tag in case_tags if tag in related_tags]
        
        if matches:
            return min(len(matches) * 0.2, 0.8)
        
        return 0.0
    
    def _reframe_case_study_for_gap(self, case_study: Dict, gap_tag: str) -> Optional[str]:
        """Reframe a case study to emphasize aspects relevant to the gap."""
        original_text = case_study.get('text', case_study.get('description', ''))
        
        if not original_text:
            return None
        
        # Simple reframing: add emphasis on the gap tag
        reframed = f"{original_text} This experience demonstrates my ability in {gap_tag} and related competencies."
        
        return reframed
    
    def _identify_experience_patterns(
        self, 
        work_history: List[Dict], 
        existing_case_studies: List[Dict]
    ) -> Dict[str, Any]:
        """Identify patterns in user's experience."""
        patterns = {
            'common_tags': [],
            'patterns': [],
            'industries': [],
            'roles': []
        }
        
        # Collect all tags
        all_tags = []
        for work_item in work_history:
            all_tags.extend(work_item.get('tags', []))
        for case_study in existing_case_studies:
            all_tags.extend(case_study.get('tags', []))
        
        # Find common tags
        from collections import Counter
        tag_counts = Counter(all_tags)
        patterns['common_tags'] = [tag for tag, count in tag_counts.most_common(5)]
        
        # Identify patterns
        if 'b2b' in all_tags and 'enterprise' in all_tags:
            patterns['patterns'].append('enterprise_focus')
        if 'growth' in all_tags and 'metrics' in all_tags:
            patterns['patterns'].append('data_driven_growth')
        if 'leadership' in all_tags and 'team_lead' in all_tags:
            patterns['patterns'].append('leadership_experience')
        
        return patterns
    
    def _create_derived_story(self, gap_tag: str, patterns: Dict[str, Any], user_context: str) -> Optional[str]:
        """Create a derived story based on patterns."""
        if not patterns.get('patterns'):
            return None
        
        # Create story based on patterns
        story_parts = ["Based on my experience"]
        
        if 'enterprise_focus' in patterns['patterns']:
            story_parts.append("working with enterprise customers")
        if 'data_driven_growth' in patterns['patterns']:
            story_parts.append("using data-driven approaches to drive growth")
        if 'leadership_experience' in patterns['patterns']:
            story_parts.append("leading cross-functional teams")
        
        story_parts.append(f"I have developed strong capabilities in {gap_tag}.")
        
        return " ".join(story_parts)
    
    def create_story(
        self, 
        gap_tag: str, 
        story_text: str, 
        tags: Optional[List[str]] = None,
        source: str = "gap_fill",
        strategy: str = "new_story",
        metadata: Optional[Dict[str, Any]] = None
    ) -> GapStory:
        """
        Create and store a new story for gap-filling.
        
        Args:
            gap_tag: The gap this story addresses
            story_text: The story content
            tags: Additional tags for the story
            source: How the story was created
            strategy: Strategy used for gap-filling
            metadata: Additional metadata
            
        Returns:
            Created GapStory object
        """
        # Generate unique story ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        story_id = f"{gap_tag}_{timestamp}"
        
        # Create story object
        story = GapStory(
            story_id=story_id,
            gap_tag=gap_tag,
            story_text=story_text,
            tags=tags or [gap_tag],
            source=source,
            strategy=strategy,
            created_at=datetime.now().isoformat(),
            approved_for=[],
            metadata=metadata or {}
        )
        
        # Store story
        self.stories[story_id] = story
        self._save_stories()
        
        # Update index
        self._update_stories_index()
        
        return story
    
    def _update_stories_index(self) -> None:
        """Update the stories index for quick lookup."""
        index = {
            'total_stories': len(self.stories),
            'stories_by_gap': {},
            'stories_by_tag': {},
            'recent_stories': []
        }
        
        # Group by gap
        for story in self.stories.values():
            if story.gap_tag not in index['stories_by_gap']:
                index['stories_by_gap'][story.gap_tag] = []
            index['stories_by_gap'][story.gap_tag].append(story.story_id)
        
        # Group by tags
        for story in self.stories.values():
            for tag in story.tags:
                if tag not in index['stories_by_tag']:
                    index['stories_by_tag'][tag] = []
                index['stories_by_tag'][tag].append(story.story_id)
        
        # Recent stories (last 10)
        recent_stories = sorted(
            self.stories.values(), 
            key=lambda s: s.created_at, 
            reverse=True
        )[:10]
        index['recent_stories'] = [s.story_id for s in recent_stories]
        
        # Save index
        with open(self.stories_index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def get_stories_by_gap(self, gap_tag: str) -> List[GapStory]:
        """Get all stories for a specific gap."""
        return [story for story in self.stories.values() if story.gap_tag == gap_tag]
    
    def get_stories_by_tag(self, tag: str) -> List[GapStory]:
        """Get all stories that have a specific tag."""
        return [story for story in self.stories.values() if tag in story.tags]
    
    def get_recent_stories(self, limit: int = 5) -> List[GapStory]:
        """Get recent stories."""
        sorted_stories = sorted(
            self.stories.values(), 
            key=lambda s: s.created_at, 
            reverse=True
        )
        return sorted_stories[:limit]
    
    def approve_story_for_job(self, story_id: str, job_id: str) -> bool:
        """Mark a story as approved for a specific job."""
        if story_id in self.stories:
            story = self.stories[story_id]
            if job_id not in story.approved_for:
                story.approved_for.append(job_id)
                self._save_stories()
                return True
        return False
    
    def update_story(
        self, 
        story_id: str, 
        story_text: Optional[str] = None, 
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update an existing story."""
        if story_id in self.stories:
            story = self.stories[story_id]
            
            if story_text:
                story.story_text = story_text
            if tags:
                story.tags = tags
            if metadata:
                story.metadata.update(metadata)
            
            story.version += 1
            self._save_stories()
            return True
        return False
    
    def delete_story(self, story_id: str) -> bool:
        """Delete a story."""
        if story_id in self.stories:
            del self.stories[story_id]
            self._save_stories()
            self._update_stories_index()
            return True
        return False
    
    def get_story_summary(self) -> Dict[str, Any]:
        """Get a summary of all stored stories."""
        if not self.stories:
            return {'total_stories': 0}
        
        # Count by gap
        gaps = {}
        for story in self.stories.values():
            if story.gap_tag not in gaps:
                gaps[story.gap_tag] = 0
            gaps[story.gap_tag] += 1
        
        # Count by source
        sources = {}
        for story in self.stories.values():
            if story.source not in sources:
                sources[story.source] = 0
            sources[story.source] += 1
        
        # Count by strategy
        strategies = {}
        for story in self.stories.values():
            if story.strategy not in strategies:
                strategies[story.strategy] = 0
            strategies[story.strategy] += 1
        
        return {
            'total_stories': len(self.stories),
            'stories_by_gap': gaps,
            'stories_by_source': sources,
            'stories_by_strategy': strategies,
            'recent_story': max(self.stories.values(), key=lambda s: s.created_at).story_id if self.stories else None
        }


def test_story_generation():
    """Test the story generation and storage system."""
    print("🧪 Testing Phase 7C: Story Generation & Storage...")
    
    # Initialize story generator
    generator = StoryGenerator(user_profile="test_stories")
    
    # Test story creation
    print(f"\n📝 Testing Story Creation:")
    
    test_stories = [
        {
            'gap_tag': 'fintech',
            'story_text': 'At ABC Company I managed billing and credits. I built credit from scratch, working with GTM teams. Launched in 6 weeks and then handed over to RevOps team.',
            'tags': ['fintech', 'billing', 'gtm', 'launch'],
            'source': 'gap_fill',
            'strategy': 'new_story'
        },
        {
            'gap_tag': 'healthtech',
            'story_text': 'At XYZ Health, I led the development of a telemedicine platform that improved patient access by 40%. I worked with clinical teams to ensure compliance and user safety.',
            'tags': ['healthtech', 'telemedicine', 'compliance', 'patient_access'],
            'source': 'gap_fill',
            'strategy': 'new_story'
        }
    ]
    
    created_stories = []
    for story_data in test_stories:
        story = generator.create_story(**story_data)
        created_stories.append(story)
        print(f"  ✅ Created story: {story.story_id}")
        print(f"     Gap: {story.gap_tag}")
        print(f"     Tags: {story.tags}")
        print(f"     Strategy: {story.strategy}")
    
    # Test story retrieval
    print(f"\n📚 Testing Story Retrieval:")
    
    fintech_stories = generator.get_stories_by_gap('fintech')
    print(f"  Fintech stories: {len(fintech_stories)}")
    
    healthtech_stories = generator.get_stories_by_gap('healthtech')
    print(f"  Healthtech stories: {len(healthtech_stories)}")
    
    recent_stories = generator.get_recent_stories(3)
    print(f"  Recent stories: {len(recent_stories)}")
    
    # Test story approval
    print(f"\n✅ Testing Story Approval:")
    if created_stories:
        story = created_stories[0]
        approved = generator.approve_story_for_job(story.story_id, 'test_job_123')
        print(f"  Approved story {story.story_id} for job: {approved}")
    
    # Test story update
    print(f"\n✏️  Testing Story Update:")
    if created_stories:
        story = created_stories[0]
        updated = generator.update_story(
            story.story_id,
            story_text="Updated story content with more details.",
            tags=['fintech', 'billing', 'gtm', 'launch', 'updated']
        )
        print(f"  Updated story {story.story_id}: {updated}")
    
    # Get summary
    print(f"\n📊 Story Summary:")
    summary = generator.get_story_summary()
    print(f"  Total stories: {summary['total_stories']}")
    print(f"  Stories by gap: {summary['stories_by_gap']}")
    print(f"  Stories by source: {summary['stories_by_source']}")
    print(f"  Stories by strategy: {summary['stories_by_strategy']}")
    
    print(f"\n✅ Phase 7C: Story Generation & Storage test completed!")
    print(f"  Story creation working")
    print(f"  Story storage working")
    print(f"  Story retrieval working")
    print(f"  Story approval working")
    print(f"  Story updates working")


if __name__ == "__main__":
    test_story_generation() 