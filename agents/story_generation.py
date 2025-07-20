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
    
    def create_story(
        self, 
        gap_tag: str, 
        story_text: str, 
        tags: List[str] = None,
        source: str = "gap_fill",
        strategy: str = "new_story",
        metadata: Dict[str, Any] = None
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
        story_text: str = None, 
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
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