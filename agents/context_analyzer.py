#!/usr/bin/env python3
"""
Context Analyzer
===============

Analyzes contextual data (past cover letters, achievements, case studies)
to inform cover letter strategy and content generation.
"""

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Achievement:
    """Represents a specific achievement with metrics and context."""

    title: str
    description: str
    metrics: Dict[str, Any]
    company: str
    role: str
    year: str
    tags: List[str]
    impact_level: str  # high, medium, low


@dataclass
class PastCoverLetter:
    """Represents a past cover letter with analysis."""

    company: str
    position: str
    date: str
    content: str
    outcome: str  # accepted, rejected, interview, no_response
    key_phrases: List[str]
    tone: str
    length: int
    strengths: List[str]
    weaknesses: List[str]


@dataclass
class StrategicInsight:
    """Represents a strategic insight for cover letter generation."""

    insight_type: str  # achievement, tone, approach, company_specific
    description: str
    confidence: float
    source: str
    recommended_action: str


class ContextAnalyzer:
    """Analyzes contextual data to inform cover letter strategy."""

    def __init__(self):
        """Initialize the context analyzer."""
        self.achievements = []
        self.past_cover_letters = []
        self.company_insights = {}
        self.strategic_recommendations = []

    def extract_achievements_from_text(
        self, text: str, company: str = "", role: str = "", year: str = ""
    ) -> List[Achievement]:
        """Extract achievements from text content."""
        achievements = []

        # Common achievement patterns
        patterns = [
            r"(?:increased|improved|grew|scaled|led|managed|built|launched|reduced|optimized)\s+"
            r"([^.]*?)\s+(?:by|from|to|at|with)\s+([^.]*?)(?:\.|$)",
            r"(?:achieved|reached|attained|delivered|completed|implemented)\s+([^.]*?)(?:\.|$)",
            r"(?:led|managed|oversaw|directed)\s+([^.]*?)(?:team|project|initiative)"
            r"(?:.*?)"
            r"(?:resulting in|leading to|which|that)\s+([^.]*?)(?:\.|$)",
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 2:
                    action = match.group(1).strip()
                    result = match.group(2).strip()

                    # Extract metrics
                    metrics = self._extract_metrics(result)

                    # Determine impact level
                    impact_level = self._assess_impact_level(action, result)

                    # Extract tags
                    tags = self._extract_tags(action + " " + result)

                    achievement = Achievement(
                        title=action[:100] + "..." if len(action) > 100 else action,
                        description=f"{action} {result}",
                        metrics=metrics,
                        company=company,
                        role=role,
                        year=year,
                        tags=tags,
                        impact_level=impact_level,
                    )
                    achievements.append(achievement)

        return achievements

    def _extract_metrics(self, text: str) -> Dict[str, Any]:
        """Extract numerical metrics from text."""
        metrics = {}

        # Percentage patterns
        percentage_patterns = [
            r"(\d+(?:\.\d+)?)\s*%",
            r"(\d+(?:\.\d+)?)\s*percent",
        ]

        for pattern in percentage_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                metrics["percentage"] = float(matches[0])

        # Number patterns (users, revenue, etc.)
        number_patterns = [
            r"(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:users|customers|employees|revenue|dollars|\$)",
            r"(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:million|billion|thousand)",
        ]

        for pattern in number_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                metrics["scale"] = matches[0]

        # Time patterns
        time_patterns = [
            r"(\d+)\s*(?:months|weeks|days|years)",
        ]

        for pattern in time_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                metrics["timeframe"] = matches[0]

        return metrics

    def _assess_impact_level(self, action: str, result: str) -> str:
        """Assess the impact level of an achievement."""
        high_impact_keywords = ["40x", "10,000", "50,000", "millions", "billion", "95%", "30%"]
        medium_impact_keywords = ["doubled", "tripled", "50%", "25%", "1000", "5000"]

        text = (action + " " + result).lower()

        for keyword in high_impact_keywords:
            if keyword.lower() in text:
                return "high"

        for keyword in medium_impact_keywords:
            if keyword.lower() in text:
                return "medium"

        return "low"

    def _extract_tags(self, text: str) -> List[str]:
        """Extract relevant tags from text."""
        tags = []

        # Define tag keywords
        tag_keywords = {
            "growth": ["growth", "scale", "expand", "increase", "grow"],
            "leadership": ["led", "managed", "directed", "oversaw", "team"],
            "technical": ["AI", "ML", "algorithm", "system", "platform"],
            "business": ["revenue", "profit", "customer", "market", "business"],
            "innovation": ["launched", "created", "built", "developed", "innovated"],
            "efficiency": ["optimized", "improved", "reduced", "streamlined", "efficient"],
            "trust": ["trust", "transparent", "explainable", "reliable", "secure"],
        }

        text_lower = text.lower()
        for tag, keywords in tag_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                tags.append(tag)

        return tags

    def analyze_past_cover_letter(
        self, content: str, company: str, position: str, date: str, outcome: str = ""
    ) -> PastCoverLetter:
        """Analyze a past cover letter for insights."""
        # Extract key phrases
        key_phrases = self._extract_key_phrases(content)

        # Analyze tone
        tone = self._analyze_tone(content)

        # Identify strengths and weaknesses
        strengths = self._identify_strengths(content)
        weaknesses = self._identify_weaknesses(content)

        return PastCoverLetter(
            company=company,
            position=position,
            date=date,
            content=content,
            outcome=outcome,
            key_phrases=key_phrases,
            tone=tone,
            length=len(content.split()),
            strengths=strengths,
            weaknesses=weaknesses,
        )

    def _extract_key_phrases(self, content: str) -> List[str]:
        """Extract key phrases from cover letter content."""
        phrases = []

        # Look for achievement statements
        achievement_patterns = [
            r"I\s+(?:led|managed|built|scaled|improved|increased)\s+[^.]*?\.",
            r"At\s+[^,]*,\s+I\s+[^.]*?\.",
            r"My\s+experience\s+includes\s+[^.]*?\.",
        ]

        for pattern in achievement_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            phrases.extend(matches)

        return phrases[:5]  # Limit to top 5

    def _analyze_tone(self, content: str) -> str:
        """Analyze the tone of the cover letter."""
        content_lower = content.lower()

        # Tone indicators
        professional_indicators = ["experience", "expertise", "leadership", "strategy", "management"]
        conversational_indicators = ["excited", "passionate", "love", "enjoy", "thrilled"]
        technical_indicators = ["algorithm", "system", "platform", "technology", "implementation"]

        professional_score = sum(1 for word in professional_indicators if word in content_lower)
        conversational_score = sum(1 for word in conversational_indicators if word in content_lower)
        technical_score = sum(1 for word in technical_indicators if word in content_lower)

        if technical_score > professional_score and technical_score > conversational_score:
            return "technical"
        elif conversational_score > professional_score:
            return "conversational"
        else:
            return "professional"

    def _identify_strengths(self, content: str) -> List[str]:
        """Identify strengths in the cover letter."""
        strengths = []

        # Check for specific metrics
        if re.search(r"\d+%", content):
            strengths.append("Includes specific metrics")

        # Check for company research
        if re.search(r"your\s+(?:company|organization|mission)", content, re.IGNORECASE):
            strengths.append("Shows company research")

        # Check for enthusiasm
        if re.search(r"excited|passionate|thrilled", content, re.IGNORECASE):
            strengths.append("Shows enthusiasm")

        # Check for concrete examples
        if re.search(r"At\s+\w+", content):
            strengths.append("Includes concrete examples")

        return strengths

    def _identify_weaknesses(self, content: str) -> List[str]:
        """Identify weaknesses in the cover letter."""
        weaknesses = []

        # Check for generic language
        generic_phrases = ["I am excited", "I would love", "I believe", "I think"]
        generic_count = sum(1 for phrase in generic_phrases if phrase.lower() in content.lower())
        if generic_count > 2:
            weaknesses.append("Too many generic phrases")

        # Check for length
        if len(content.split()) < 200:
            weaknesses.append("Too short")
        elif len(content.split()) > 400:
            weaknesses.append("Too long")

        # Check for lack of specificity
        if not re.search(r"\d+", content):
            weaknesses.append("Lacks specific metrics")

        return weaknesses

    def generate_strategic_insights(
        self, job_description: str, achievements: List[Achievement], past_cover_letters: List[PastCoverLetter]
    ) -> List[StrategicInsight]:
        """Generate strategic insights for cover letter generation."""
        insights = []

        # Analyze job requirements
        job_keywords = self._extract_job_keywords(job_description)

        # Find most relevant achievements
        relevant_achievements = self._find_relevant_achievements(achievements, job_keywords)

        if relevant_achievements:
            insights.append(
                StrategicInsight(
                    insight_type="achievement",
                    description=(
                        f"Highlight {len(relevant_achievements)} relevant "
                        f"achievements with "
                        f"{relevant_achievements[0].impact_level} impact"
                    ),
                    confidence=0.8,
                    source="achievement_analysis",
                    recommended_action=("Include specific metrics and outcomes from relevant achievements"),
                )
            )

        # Analyze company-specific patterns
        company_name = self._extract_company_name(job_description)
        company_cover_letters = [cl for cl in past_cover_letters if cl.company.lower() in company_name.lower()]

        if company_cover_letters:
            successful_letters = [cl for cl in company_cover_letters if cl.outcome in ["accepted", "interview"]]
            if successful_letters:
                insights.append(
                    StrategicInsight(
                        insight_type="company_specific",
                        description=(f"Found {len(successful_letters)} successful applications to " f"{company_name}"),
                        confidence=0.9,
                        source="past_applications",
                        recommended_action="Adapt successful elements from previous applications",
                    )
                )

        # Analyze tone preferences
        tone_insight = self._analyze_tone_preferences(past_cover_letters, job_description)
        if tone_insight:
            insights.append(tone_insight)

        return insights

    def _extract_job_keywords(self, job_description: str) -> List[str]:
        """Extract keywords from job description."""
        # Simple keyword extraction
        keywords = []
        common_keywords = ["growth", "scaling", "AI", "ML", "leadership", "team", "product", "user", "data", "analytics"]

        job_lower = job_description.lower()
        for keyword in common_keywords:
            if keyword in job_lower:
                keywords.append(keyword)

        return keywords

    def _find_relevant_achievements(self, achievements: List[Achievement], job_keywords: List[str]) -> List[Achievement]:
        """Find achievements most relevant to the job."""
        relevant_achievements = []

        for achievement in achievements:
            # Check tag overlap
            tag_overlap = sum(1 for tag in achievement.tags if tag in job_keywords)

            # Prioritize high impact achievements
            if achievement.impact_level == "high" and tag_overlap > 0:
                relevant_achievements.append(achievement)
            elif tag_overlap > 1:  # Multiple tag matches
                relevant_achievements.append(achievement)

        # Sort by impact level and relevance
        relevant_achievements.sort(
            key=lambda x: (x.impact_level == "high", len(set(x.tags) & set(job_keywords))), reverse=True
        )

        return relevant_achievements[:3]  # Return top 3

    def _extract_company_name(self, job_description: str) -> str:
        """Extract company name from job description."""
        patterns = [
            r"at\s+([A-Z][a-zA-Z\s&]+?)\s+(?:we|is|are)",
            r"([A-Z][a-zA-Z\s&]+?)\s+is\s+looking",
        ]

        for pattern in patterns:
            match = re.search(pattern, job_description, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return "Unknown Company"

    def _analyze_tone_preferences(
        self, past_cover_letters: List[PastCoverLetter], job_description: str
    ) -> Optional[StrategicInsight]:
        """Analyze tone preferences based on past cover letters and job description."""
        if not past_cover_letters:
            return None

        # Analyze successful cover letters
        successful_letters = [cl for cl in past_cover_letters if cl.outcome in ["accepted", "interview"]]

        if successful_letters:
            tones = [cl.tone for cl in successful_letters]
            most_common_tone = max(set(tones), key=tones.count)

            # Check if job description suggests a specific tone
            job_lower = job_description.lower()
            if "startup" in job_lower or "fast-paced" in job_lower:
                recommended_tone = "conversational"
            elif "enterprise" in job_lower or "corporate" in job_lower:
                recommended_tone = "professional"
            elif "AI" in job_lower or "ML" in job_lower:
                recommended_tone = "technical"
            else:
                recommended_tone = most_common_tone

            return StrategicInsight(
                insight_type="tone",
                description=(
                    f"Recommended tone: {recommended_tone} " f"(based on {len(successful_letters)} successful applications)"
                ),
                confidence=0.7,
                source="past_success_analysis",
                recommended_action=(f"Use {recommended_tone} tone throughout the cover letter"),
            )

        return None


if __name__ == "__main__":
    # Test the context analyzer
    analyzer = ContextAnalyzer()

    # Test achievement extraction
    test_text = "At Aurora Solar, I helped scale a B2B platform from 10 to 10,000+ customers, increasing revenue 40x while maintaining 95% customer satisfaction."
    achievements = analyzer.extract_achievements_from_text(test_text, "Aurora Solar", "Product Manager", "2023")

    print("Extracted Achievements:")
    for achievement in achievements:
        print(f"- {achievement.description}")
        print(f"  Impact: {achievement.impact_level}")
        print(f"  Tags: {achievement.tags}")
        print(f"  Metrics: {achievement.metrics}")
        print()
