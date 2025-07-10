#!/usr/bin/env python3

import sys
import os
sys.path.append('agents')

from cover_letter_agent import CoverLetterAgent

def test_improvements():
    """Test the improved cover letter system with Nira Energy job description."""
    
    # Initialize the agent
    agent = CoverLetterAgent()
    
    # Nira Energy job description
    job_description = """About Nira Energy

Nira's mission is to help convert the US power grid to be 100% fossil-free.
We are profitable!
Nira is a software platform that helps renewable energy developers find the cheapest points on the grid to connect.
We focus on estimating the cost to interconnect with the electrical grid (aka the Interconnection Process). Depending on where developers connect, they may be on the hook to pay millions of dollars to upgrade power lines, substations etc.

What you'll do

As a PM at Nira, you'll work on software and data products that our customers use every week. Your work will directly accelerate renewables getting built. This work could include rolling out new regions, adding new features or even building brand new products out.
Being a PM at Nira is a unique blend of PM-ing a traditional software product, while having to go deep on a niche domain. Nira operates in the world of Grid Interconnection, and you'll need to be comfortable becoming an expert in a domain you've likely never heard of before. We're launching a variety of new products, so you should be comfortable with high autonomy and ownership. Most importantly, you should be passionate about fixing our climate! Some example projects:
Launch new markets in the US.
Launching new features in the US markets we're active in.
Build MVPs for new adjacent products we're exploring.

A day in the life

You'll spend ~3 hours a week doing user interviews to learn about workflows and gather feedback.
You'll manage small teams of 3-4 folks. (1 PM, 1 or 2 SWE and 1 transmission planning engineer)
You'll spend a few hours a week with transmission engineers getting into the nitty-gritty technical details of transmission.
You'll translate user requirements into Figma mockups.
You'll spend ~5 hours a week diving into our data and using Python to do light analytics.

About you

3+ years as a PM.
Mission-oriented and focused on working on climate.
Customer facing experience.
Data analysis experience - Python, SQL, etc.
Excited to work with Transmission Engineers and learn about how our electrical grid works.
Previous work experience in a niche domain is a plus.
Software background a plus.
Figma skills a plus.
Operate well in ambiguity and excited about taking ownership.
Capable of rolling with the punches. Plans change when working at a rapidly growing startup"""
    
    print("🔍 Analyzing job description...")
    
    # Process the job description
    job, cover_letter, suggestions = agent.process_job_description(job_description)
    
    print(f"\n📊 JOB ANALYSIS:")
    print(f"Company: {job.company_name}")
    print(f"Title: {job.job_title}")
    print(f"Score: {job.score:.2f}")
    print(f"Go/No-Go: {'✅ GO' if job.go_no_go else '❌ NO-GO'}")
    
    if job.targeting:
        print(f"Targeting Score: {job.targeting.targeting_score:.2f}")
        print(f"Targeting Decision: {'✅ TARGET' if job.targeting.targeting_go_no_go else '❌ NOT TARGET'}")
    
    print(f"\n🎯 SELECTED BLURBS:")
    selected_blurbs = agent.select_blurbs(job)
    for blurb_type, blurb in selected_blurbs.items():
        print(f"  {blurb_type}: {blurb.blurb_id} (score: {blurb.score:.2f})")
    
    print(f"\n📝 GENERATED COVER LETTER:")
    print("=" * 80)
    print(cover_letter)
    print("=" * 80)
    
    # Save to file
    with open("test_nira_cover_letter.txt", "w") as f:
        f.write(cover_letter)
    
    print(f"\n💾 Cover letter saved to: test_nira_cover_letter.txt")
    
    # Perform JD vs draft review
    print(f"\n🔍 JD vs DRAFT ANALYSIS:")
    review = agent.review_jd_vs_draft(job, cover_letter)
    
    print(f"\n📋 KEY JOB REQUIREMENTS:")
    for req in review['job_requirements']:
        print(f"  • {req}")
    
    print(f"\n✅ DEMONSTRATED SKILLS:")
    for skill in review['demonstrated_skills']:
        print(f"  • {skill}")
    
    if review['gaps']:
        print(f"\n❌ GAPS:")
        for gap in review['gaps']:
            print(f"  • {gap}")
    
    if review['strengths']:
        print(f"\n💪 STRENGTHS:")
        for strength in review['strengths']:
            print(f"  • {strength}")
    
    if review['improvements']:
        print(f"\n🚀 IMPROVEMENTS:")
        for improvement in review['improvements']:
            print(f"  • {improvement}")
    
    if suggestions:
        print(f"\n💡 ENHANCEMENT SUGGESTIONS:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion.description}")
            print(f"   Category: {suggestion.category}")
            print(f"   Priority: {suggestion.priority}")

if __name__ == "__main__":
    test_improvements() 