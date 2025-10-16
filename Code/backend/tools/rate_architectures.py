"""
Architecture Rating Tool - Phase C Week 2

Interactive tool to rate CPPN architectures on organic quality,
coherence, audio reactivity, and aesthetic appeal.

Usage:
    python rate_architectures.py [exploration_dir]
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List
import subprocess

def find_latest_exploration() -> Path:
    """Find the most recent architecture exploration directory."""
    explorations_dir = Path(__file__).parent.parent / 'explorations' / 'architecture_matrix'
    
    if not explorations_dir.exists():
        return None
    
    # Get all exploration directories
    dirs = [d for d in explorations_dir.iterdir() if d.is_dir()]
    
    if not dirs:
        return None
    
    # Return most recent
    return max(dirs, key=lambda d: d.stat().st_mtime)


def load_exploration_metadata(exploration_dir: Path) -> Dict:
    """Load metadata from exploration run."""
    metadata_path = exploration_dir / 'metadata.json'
    
    if not metadata_path.exists():
        print(f"Warning: No metadata.json found in {exploration_dir}")
        return None
    
    with open(metadata_path, 'r') as f:
        return json.load(f)


def list_videos(exploration_dir: Path) -> List[Path]:
    """List all video files in exploration directory."""
    videos = sorted(exploration_dir.glob('*.mp4'))
    return [v for v in videos if not v.name.startswith('.')]


def play_video(video_path: Path):
    """Play video using system default player."""
    try:
        if sys.platform == 'win32':
            os.startfile(str(video_path))
        elif sys.platform == 'darwin':  # macOS
            subprocess.run(['open', str(video_path)])
        else:  # linux
            subprocess.run(['xdg-open', str(video_path)])
        return True
    except Exception as e:
        print(f"Error playing video: {e}")
        return False


def parse_video_filename(filename: str) -> Dict:
    """Extract architecture info from filename."""
    # Format: arch_2L_32D_seed42.mp4
    parts = filename.replace('.mp4', '').split('_')
    
    try:
        return {
            'layers': int(parts[1].replace('L', '')),
            'hidden_dim': int(parts[2].replace('D', '')),
            'seed': int(parts[3].replace('seed', ''))
        }
    except:
        return None


def get_rating(prompt: str, min_val: int = 1, max_val: int = 5) -> int:
    """Get integer rating from user."""
    while True:
        try:
            value = input(f"{prompt} ({min_val}-{max_val}): ").strip()
            
            if value.lower() in ['q', 'quit', 'exit']:
                return None
            
            if value == '':
                return None  # Skip
            
            rating = int(value)
            if min_val <= rating <= max_val:
                return rating
            else:
                print(f"Please enter a number between {min_val} and {max_val}")
        except ValueError:
            print("Please enter a valid number")


def get_notes() -> str:
    """Get optional notes from user."""
    notes = input("Notes (optional, press Enter to skip): ").strip()
    return notes if notes else None


def rate_video(video_path: Path, video_num: int, total_videos: int) -> Dict:
    """Rate a single video."""
    print(f"\n{'='*60}")
    print(f"Video {video_num}/{total_videos}: {video_path.name}")
    print(f"{'='*60}")
    
    # Parse filename to get architecture info
    arch_info = parse_video_filename(video_path.name)
    if arch_info:
        print(f"\nArchitecture:")
        print(f"  Layers: {arch_info['layers']}")
        print(f"  Hidden dim: {arch_info['hidden_dim']}")
        print(f"  Seed: {arch_info['seed']}")
    
    # Play video
    print(f"\nOpening video... (close when done watching)")
    play_video(video_path)
    
    input("\nPress Enter when ready to rate...")
    
    # Get ratings
    print("\nRate this video:")
    print("  1 = Poor, 2 = Below Average, 3 = Average, 4 = Good, 5 = Excellent")
    print("  (or press Enter to skip, 'q' to quit)\n")
    
    organic = get_rating("1. Organic Quality (spirals, cells, fluid forms)")
    if organic is None:
        return None
    
    coherence = get_rating("2. Coherence (spatial continuity)")
    if coherence is None:
        return None
    
    reactivity = get_rating("3. Audio Reactivity (responsiveness to music)")
    if reactivity is None:
        return None
    
    aesthetic = get_rating("4. Aesthetic Appeal (subjective beauty)")
    if aesthetic is None:
        return None
    
    notes = get_notes()
    
    # Calculate overall score
    overall = (organic + coherence + reactivity + aesthetic) / 4.0
    
    rating = {
        'video': video_path.name,
        'architecture': arch_info,
        'ratings': {
            'organic_quality': organic,
            'coherence': coherence,
            'audio_reactivity': reactivity,
            'aesthetic_appeal': aesthetic,
            'overall': round(overall, 2)
        },
        'notes': notes
    }
    
    print(f"\n✅ Rated: Overall {overall:.2f}/5.0")
    
    return rating


def save_ratings(ratings: List[Dict], exploration_dir: Path):
    """Save ratings to JSON file."""
    ratings_path = exploration_dir / 'ratings.json'
    
    with open(ratings_path, 'w') as f:
        json.dump({
            'ratings': ratings,
            'summary': generate_summary(ratings)
        }, f, indent=2)
    
    print(f"\n✅ Ratings saved to: {ratings_path}")


def generate_summary(ratings: List[Dict]) -> Dict:
    """Generate summary statistics from ratings."""
    if not ratings:
        return {}
    
    # Group by architecture (ignore seed)
    arch_groups = {}
    for rating in ratings:
        arch = rating['architecture']
        if arch:
            key = f"{arch['layers']}L_{arch['hidden_dim']}D"
            if key not in arch_groups:
                arch_groups[key] = []
            arch_groups[key].append(rating)
    
    # Calculate averages per architecture
    arch_averages = {}
    for key, group in arch_groups.items():
        avg_organic = sum(r['ratings']['organic_quality'] for r in group) / len(group)
        avg_coherence = sum(r['ratings']['coherence'] for r in group) / len(group)
        avg_reactivity = sum(r['ratings']['audio_reactivity'] for r in group) / len(group)
        avg_aesthetic = sum(r['ratings']['aesthetic_appeal'] for r in group) / len(group)
        avg_overall = sum(r['ratings']['overall'] for r in group) / len(group)
        
        arch_averages[key] = {
            'count': len(group),
            'averages': {
                'organic_quality': round(avg_organic, 2),
                'coherence': round(avg_coherence, 2),
                'audio_reactivity': round(avg_reactivity, 2),
                'aesthetic_appeal': round(avg_aesthetic, 2),
                'overall': round(avg_overall, 2)
            }
        }
    
    # Find top architectures
    sorted_archs = sorted(
        arch_averages.items(),
        key=lambda x: x[1]['averages']['overall'],
        reverse=True
    )
    
    top_5 = [{'architecture': k, **v} for k, v in sorted_archs[:5]]
    
    return {
        'total_rated': len(ratings),
        'architectures_tested': len(arch_averages),
        'architecture_averages': arch_averages,
        'top_5_overall': top_5
    }


def generate_catalog(ratings: List[Dict], exploration_dir: Path):
    """Generate ARCHITECTURE_CATALOG.md markdown file."""
    
    summary = generate_summary(ratings)
    
    catalog = f"""# Architecture Catalog - Visual Quality Ratings

**Exploration Directory:** `{exploration_dir.name}`  
**Total Videos Rated:** {summary.get('total_rated', 0)}  
**Architectures Tested:** {summary.get('architectures_tested', 0)}

---

## Rating Scale

**1 = Poor** | **2 = Below Average** | **3 = Average** | **4 = Good** | **5 = Excellent**

### Categories

1. **Organic Quality** - Spirals, cells, fluid forms, biological patterns
2. **Coherence** - Spatial continuity, pattern coherence
3. **Audio Reactivity** - Responsiveness to music
4. **Aesthetic Appeal** - Subjective visual beauty

---

## Top 5 Architectures (by Overall Score)

"""
    
    if 'top_5_overall' in summary:
        for i, arch in enumerate(summary['top_5_overall'], 1):
            name = arch['architecture']
            avgs = arch['averages']
            catalog += f"""
### {i}. {name}

| Metric | Score |
|--------|-------|
| **Overall** | **{avgs['overall']:.2f}/5.0** |
| Organic Quality | {avgs['organic_quality']:.2f}/5.0 |
| Coherence | {avgs['coherence']:.2f}/5.0 |
| Audio Reactivity | {avgs['audio_reactivity']:.2f}/5.0 |
| Aesthetic Appeal | {avgs['aesthetic_appeal']:.2f}/5.0 |

**Samples:** {arch['count']} videos rated

"""
    
    catalog += """
---

## All Architectures (Sorted by Overall Score)

| Rank | Architecture | Overall | Organic | Coherence | Reactivity | Aesthetic | Samples |
|------|--------------|---------|---------|-----------|------------|-----------|---------|
"""
    
    if 'architecture_averages' in summary:
        sorted_archs = sorted(
            summary['architecture_averages'].items(),
            key=lambda x: x[1]['averages']['overall'],
            reverse=True
        )
        
        for i, (name, data) in enumerate(sorted_archs, 1):
            avgs = data['averages']
            catalog += f"| {i} | {name} | {avgs['overall']:.2f} | {avgs['organic_quality']:.2f} | {avgs['coherence']:.2f} | {avgs['audio_reactivity']:.2f} | {avgs['aesthetic_appeal']:.2f} | {data['count']} |\n"
    
    catalog += """
---

## Individual Ratings

"""
    
    # Add individual ratings
    for rating in ratings:
        catalog += f"""
### {rating['video']}

"""
        if rating['architecture']:
            arch = rating['architecture']
            catalog += f"**Architecture:** {arch['layers']} layers × {arch['hidden_dim']} dim (seed={arch['seed']})\n\n"
        
        catalog += f"""**Ratings:**
- Organic Quality: {rating['ratings']['organic_quality']}/5
- Coherence: {rating['ratings']['coherence']}/5
- Audio Reactivity: {rating['ratings']['audio_reactivity']}/5
- Aesthetic Appeal: {rating['ratings']['aesthetic_appeal']}/5
- **Overall: {rating['ratings']['overall']}/5**

"""
        if rating.get('notes'):
            catalog += f"**Notes:** {rating['notes']}\n\n"
    
    catalog += """
---

## Next Steps

1. **Select Winners** - Choose top 3-5 architectures for CLIP training (Week 3)
2. **Document Patterns** - Note what makes winning architectures successful
3. **Plan Training** - Prepare organic prompts for CLIP optimization

---

**Generated:** {exploration_dir.name}  
**Phase:** C - Week 2 (Visual Catalog & Rating)
"""
    
    # Save catalog
    catalog_path = Path(__file__).parent.parent.parent / 'docs' / 'Phase2-POC' / 'ARCHITECTURE_CATALOG.md'
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    catalog_path.write_text(catalog)
    
    print(f"✅ Catalog saved to: {catalog_path}")
    
    return catalog_path


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Rate CPPN architectures for organic pattern quality'
    )
    parser.add_argument(
        'exploration_dir',
        nargs='?',
        type=str,
        default=None,
        help='Path to exploration directory (default: latest)'
    )
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume rating from existing ratings.json'
    )
    
    args = parser.parse_args()
    
    # Find exploration directory
    if args.exploration_dir:
        exploration_dir = Path(args.exploration_dir)
    else:
        exploration_dir = find_latest_exploration()
        if exploration_dir is None:
            print("Error: No exploration directories found")
            print("Run explore_architectures.py first")
            sys.exit(1)
    
    if not exploration_dir.exists():
        print(f"Error: Directory not found: {exploration_dir}")
        sys.exit(1)
    
    print(f"\n🎯 Architecture Rating Tool")
    print(f"📁 Exploration: {exploration_dir.name}")
    
    # Load metadata
    metadata = load_exploration_metadata(exploration_dir)
    if metadata:
        print(f"📊 Matrix: {len(metadata['matrix']['layers'])} layers × "
              f"{len(metadata['matrix']['hidden_dims'])} dims × "
              f"{len(metadata['matrix']['seeds'])} seeds")
    
    # List videos
    videos = list_videos(exploration_dir)
    print(f"🎬 Videos found: {len(videos)}")
    
    if not videos:
        print("No videos found in exploration directory")
        sys.exit(1)
    
    # Load existing ratings if resuming
    existing_ratings = []
    rated_videos = set()
    
    if args.resume:
        ratings_path = exploration_dir / 'ratings.json'
        if ratings_path.exists():
            with open(ratings_path, 'r') as f:
                data = json.load(f)
                existing_ratings = data.get('ratings', [])
                rated_videos = {r['video'] for r in existing_ratings}
                print(f"📝 Resuming: {len(existing_ratings)} videos already rated")
    
    # Filter out already rated videos
    videos_to_rate = [v for v in videos if v.name not in rated_videos]
    
    if not videos_to_rate:
        print("\n✅ All videos already rated!")
        generate_catalog(existing_ratings, exploration_dir)
        sys.exit(0)
    
    print(f"\n🎬 Videos to rate: {len(videos_to_rate)}")
    print(f"\nInstructions:")
    print(f"  - Each video will open in your default player")
    print(f"  - Watch and close the player when done")
    print(f"  - Rate on 1-5 scale (or press Enter to skip)")
    print(f"  - Press 'q' at any rating to quit")
    print(f"\nReady? Press Enter to begin...")
    input()
    
    # Rate videos
    ratings = existing_ratings.copy()
    
    for i, video_path in enumerate(videos_to_rate, 1):
        rating = rate_video(video_path, i, len(videos_to_rate))
        
        if rating is None:
            print("\nQuitting...")
            break
        
        ratings.append(rating)
        
        # Save after each rating (in case of interruption)
        save_ratings(ratings, exploration_dir)
    
    # Generate final catalog
    print(f"\n{'='*60}")
    print("Generating architecture catalog...")
    print(f"{'='*60}")
    
    catalog_path = generate_catalog(ratings, exploration_dir)
    
    # Print summary
    summary = generate_summary(ratings)
    
    print(f"\n{'='*60}")
    print("🎉 Rating Complete!")
    print(f"{'='*60}")
    print(f"✅ Videos rated: {len(ratings)}")
    print(f"📁 Ratings: {exploration_dir / 'ratings.json'}")
    print(f"📄 Catalog: {catalog_path}")
    
    if 'top_5_overall' in summary and summary['top_5_overall']:
        print(f"\n🏆 Top Architecture: {summary['top_5_overall'][0]['architecture']}")
        print(f"   Overall Score: {summary['top_5_overall'][0]['averages']['overall']:.2f}/5.0")
    
    print(f"\n➡️  Next: Select top 3-5 for CLIP training (Week 3)")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()



