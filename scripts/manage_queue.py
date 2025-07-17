#!/usr/bin/env python3
"""
Data Queue Management CLI
Manages the prioritized queue of data sources that need to be analyzed and incorporated into cover letter creation.
"""

import sys
import os
import yaml
import argparse
from datetime import datetime
from pathlib import Path

USER_ID = "peter"
USER_DIR = f"users/{USER_ID}"
QUEUE_PATH = f"{USER_DIR}/data_queue.yaml"
APPROVED_STORIES_PATH = f"{USER_DIR}/approved_star_stories.yaml"

def load_queue():
    """Load the data queue."""
    try:
        with open(QUEUE_PATH, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ Queue file not found: {QUEUE_PATH}")
        return None

def save_queue(queue_data):
    """Save the data queue."""
    with open(QUEUE_PATH, 'w') as f:
        yaml.dump(queue_data, f, default_flow_style=False, sort_keys=False)
    print(f"✅ Queue saved to: {QUEUE_PATH}")

def show_queue_status():
    """Show the current queue status."""
    queue_data = load_queue()
    if not queue_data:
        return
    
    queue = queue_data.get('queue', {})
    stats = queue_data.get('queue_stats', {})
    
    print(f"\n📊 DATA QUEUE STATUS")
    print(f"{'='*50}")
    
    # Show statistics
    print(f"📈 Queue Statistics:")
    print(f"  • Total items: {stats.get('total_items', 0)}")
    print(f"  • High priority: {stats.get('high_priority', 0)}")
    print(f"  • Medium priority: {stats.get('medium_priority', 0)}")
    print(f"  • Low priority: {stats.get('low_priority', 0)}")
    print(f"  • Pending: {stats.get('pending', 0)}")
    print(f"  • Blocked: {stats.get('blocked', 0)}")
    print(f"  • Completed: {stats.get('completed', 0)}")
    print(f"  • Estimated effort: {stats.get('total_estimated_effort', 'Unknown')}")
    
    # Show high priority items
    high_priority = queue.get('high_priority', [])
    if high_priority:
        print(f"\n🔥 HIGH PRIORITY:")
        for item in high_priority:
            status_emoji = "⏳" if item.get('status') == 'pending' else "🚫" if item.get('status') == 'blocked' else "✅"
            print(f"  {status_emoji} {item.get('description', 'No description')}")
            print(f"     Source: {item.get('source', 'Unknown')}")
            print(f"     Effort: {item.get('estimated_effort', 'Unknown')}")
            print(f"     Notes: {item.get('notes', 'No notes')}")
            print()
    
    # Show medium priority items
    medium_priority = queue.get('medium_priority', [])
    if medium_priority:
        print(f"\n📋 MEDIUM PRIORITY:")
        for item in medium_priority:
            status_emoji = "⏳" if item.get('status') == 'pending' else "🚫" if item.get('status') == 'blocked' else "✅"
            print(f"  {status_emoji} {item.get('description', 'No description')}")
            print(f"     Source: {item.get('source', 'Unknown')}")
            print(f"     Effort: {item.get('estimated_effort', 'Unknown')}")
            print()
    
    # Show low priority items
    low_priority = queue.get('low_priority', [])
    if low_priority:
        print(f"\n📝 LOW PRIORITY:")
        for item in low_priority:
            status_emoji = "⏳" if item.get('status') == 'pending' else "🚫" if item.get('status') == 'blocked' else "✅"
            print(f"  {status_emoji} {item.get('description', 'No description')}")
            print(f"     Source: {item.get('source', 'Unknown')}")
            print(f"     Effort: {item.get('estimated_effort', 'Unknown')}")
            print()

def show_next_item():
    """Show the next priority item to work on."""
    queue_data = load_queue()
    if not queue_data:
        return
    
    queue = queue_data.get('queue', {})
    
    # Find the next pending item
    for priority_level in ['high_priority', 'medium_priority', 'low_priority']:
        items = queue.get(priority_level, [])
        for item in items:
            if item.get('status') == 'pending':
                print(f"\n🎯 NEXT PRIORITY ITEM:")
                print(f"{'='*40}")
                print(f"📋 Description: {item.get('description', 'No description')}")
                print(f"🏷️  Source: {item.get('source', 'Unknown')}")
                print(f"⏱️  Estimated Effort: {item.get('estimated_effort', 'Unknown')}")
                print(f"📝 Notes: {item.get('notes', 'No notes')}")
                print(f"🔢 Priority: {item.get('priority', 'Unknown')}")
                return
    
    print("✅ No pending items in queue!")

def mark_item_complete(item_id):
    """Mark an item as complete."""
    queue_data = load_queue()
    if not queue_data:
        return
    
    queue = queue_data.get('queue', {})
    
    # Find and update the item
    for priority_level in ['high_priority', 'medium_priority', 'low_priority']:
        items = queue.get(priority_level, [])
        for item in items:
            if item.get('id') == item_id:
                item['status'] = 'completed'
                item['completed_timestamp'] = datetime.now().isoformat()
                print(f"✅ Marked '{item.get('description', 'Unknown')}' as complete")
                
                # Update statistics
                stats = queue_data.get('queue_stats', {})
                stats['completed'] = stats.get('completed', 0) + 1
                stats['pending'] = stats.get('pending', 0) - 1
                queue_data['queue_stats'] = stats
                
                save_queue(queue_data)
                return
    
    print(f"❌ Item with ID '{item_id}' not found")

def add_item_to_queue(description, source, priority_level, estimated_effort, notes=""):
    """Add a new item to the queue."""
    queue_data = load_queue()
    if not queue_data:
        return
    
    queue = queue_data.get('queue', {})
    
    # Generate a new ID
    import uuid
    item_id = f"item_{uuid.uuid4().hex[:8]}"
    
    # Find the next priority number
    max_priority = 0
    for level in ['high_priority', 'medium_priority', 'low_priority']:
        items = queue.get(level, [])
        for item in items:
            max_priority = max(max_priority, item.get('priority', 0))
    
    new_item = {
        'id': item_id,
        'source': source,
        'description': description,
        'status': 'pending',
        'priority': max_priority + 1,
        'estimated_effort': estimated_effort,
        'notes': notes,
        'created_timestamp': datetime.now().isoformat()
    }
    
    # Add to the appropriate priority level
    if priority_level not in queue:
        queue[priority_level] = []
    queue[priority_level].append(new_item)
    
    # Update statistics
    stats = queue_data.get('queue_stats', {})
    stats['total_items'] = stats.get('total_items', 0) + 1
    stats['pending'] = stats.get('pending', 0) + 1
    stats[priority_level] = stats.get(priority_level, 0) + 1
    queue_data['queue_stats'] = stats
    
    save_queue(queue_data)
    print(f"✅ Added '{description}' to {priority_level} queue")

def show_refinement_status():
    """Show STAR stories refinement status."""
    try:
        with open(APPROVED_STORIES_PATH, 'r') as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ Approved stories file not found: {APPROVED_STORIES_PATH}")
        return
    
    approved_stories = data.get('approved_stories', [])
    pending = [s for s in approved_stories if s.get('status') == 'pending_refinement']
    refined = [s for s in approved_stories if s.get('status') == 'refined']
    
    print(f"\n📝 STAR STORIES REFINEMENT STATUS:")
    print(f"{'='*50}")
    print(f"  📝 Pending refinement: {len(pending)}")
    print(f"  ✅ Refined: {len(refined)}")
    print(f"  📊 Total approved: {len(approved_stories)}")
    
    if pending:
        print(f"\n⏳ Pending Stories:")
        for story in pending:
            print(f"  • {story['title']} (Score: {story.get('importance_score', 'N/A')})")
    
    if refined:
        print(f"\n✅ Refined Stories:")
        for story in refined:
            print(f"  • {story['title']} (Score: {story.get('importance_score', 'N/A')})")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Manage data analysis queue")
    parser.add_argument('--status', action='store_true', help='Show queue status')
    parser.add_argument('--next', action='store_true', help='Show next priority item')
    parser.add_argument('--complete', type=str, help='Mark item as complete by ID')
    parser.add_argument('--add', action='store_true', help='Add new item to queue')
    parser.add_argument('--refinement', action='store_true', help='Show refinement status')
    parser.add_argument('--all', action='store_true', help='Show all status information')
    
    args = parser.parse_args()
    
    if args.status or args.all:
        show_queue_status()
    
    if args.next:
        show_next_item()
    
    if args.complete:
        mark_item_complete(args.complete)
    
    if args.refinement or args.all:
        show_refinement_status()
    
    if args.add:
        print("Adding new item to queue...")
        description = input("Description: ")
        source = input("Source: ")
        priority = input("Priority level (high_priority/medium_priority/low_priority): ")
        effort = input("Estimated effort: ")
        notes = input("Notes (optional): ")
        
        add_item_to_queue(description, source, priority, effort, notes)
    
    # If no arguments provided, show status
    if not any([args.status, args.next, args.complete, args.add, args.refinement, args.all]):
        show_queue_status()
        print()
        show_refinement_status()

if __name__ == "__main__":
    main() 