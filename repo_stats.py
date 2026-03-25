#!/usr/bin/env python3
"""repo-stats — Summarize GitHub repo portfolio stats."""
import subprocess, json, sys, os
from collections import Counter

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def get_repos(user, limit=2000):
    """Fetch all public repos via gh CLI."""
    out = run(f'gh api "/users/{user}/repos?per_page=100&sort=created&direction=desc&type=public" --paginate --jq ".[] | {{name, language, stargazers_count, forks_count, created_at, description}}"')
    repos = []
    for line in out.split('\n'):
        if line.strip():
            try:
                repos.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return repos

def main():
    user = sys.argv[1] if len(sys.argv) > 1 else "rogue-agent1"
    print(f"Fetching repos for {user}...")
    repos = get_repos(user)
    
    if not repos:
        print("No repos found or API error.")
        return
    
    # Stats
    langs = Counter(r.get('language') or 'None' for r in repos)
    total_stars = sum(r.get('stargazers_count', 0) for r in repos)
    total_forks = sum(r.get('forks_count', 0) for r in repos)
    starred = [r for r in repos if r.get('stargazers_count', 0) > 0]
    
    # Date range
    dates = sorted(r['created_at'][:10] for r in repos if r.get('created_at'))
    
    print(f"\n📊 {user} — GitHub Portfolio")
    print(f"{'='*40}")
    print(f"Total repos:  {len(repos)}")
    print(f"Total stars:  {total_stars}")
    print(f"Total forks:  {total_forks}")
    print(f"Date range:   {dates[0]} → {dates[-1]}" if dates else "")
    
    print(f"\n🔤 Languages (top 10):")
    for lang, count in langs.most_common(10):
        pct = count / len(repos) * 100
        bar = '█' * int(pct / 2)
        print(f"  {lang:20s} {count:4d} ({pct:4.1f}%) {bar}")
    
    if starred:
        print(f"\n⭐ Starred repos ({len(starred)}):")
        for r in sorted(starred, key=lambda x: x['stargazers_count'], reverse=True)[:10]:
            print(f"  ⭐{r['stargazers_count']:3d}  {r['name']}")
    
    # Repos per day
    day_counts = Counter(d for d in (r['created_at'][:10] for r in repos if r.get('created_at')))
    if day_counts:
        best_day, best_count = day_counts.most_common(1)[0]
        print(f"\n🏆 Most productive day: {best_day} ({best_count} repos)")
        print(f"📅 Active days: {len(day_counts)}")
        print(f"📈 Avg repos/active day: {len(repos)/len(day_counts):.1f}")

if __name__ == '__main__':
    main()
