#!/usr/bin/env python3
"""
gitch - Blessed Framework Version with Real GitHub API
Requires: pip install blessed requests

Usage:
    python gitch.py [username]

Environment Variables:
    GITHUB_TOKEN - Your GitHub personal access token (optional but recommended)

Examples:
    GITHUB_TOKEN=your_token python gitch.py
    GITHUB_TOKEN=your_token python gitch.py octocat
    python gitch.py torvalds  # Without token (rate limited)
"""

import random
import requests
import subprocess
import tempfile
import os
import sys
from blessed import Terminal

term = Terminal()


def get_github_headers():
    """Get GitHub API headers with token if available"""
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'GitHub-Fastfetch/1.0'
    }

    token = os.getenv('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = f'token {token}'
        print(term.dim + "Using GitHub API token..." + term.normal)
    else:
        print(term.yellow + "No GitHub token found. Using public API (rate limited)." + term.normal)
        print(term.dim + "Set GITHUB_TOKEN environment variable for better rate limits." + term.normal)

    return headers


def fetch_real_user_data(username=None):
    """Fetch real user data from GitHub API"""
    headers = get_github_headers()

    try:
        if username:
            # Fetch specific user
            user_url = f'https://api.github.com/users/{username}'
            print(term.dim + f"Fetching user: {username}" + term.normal)
        else:
            # Get random user from recent activity
            print(term.dim + "Fetching random user from recent events..." + term.normal)
            events_url = 'https://api.github.com/events'
            events_response = requests.get(events_url, headers=headers, timeout=10)
            events_response.raise_for_status()

            events = events_response.json()
            if events:
                # Pick a random actor from recent events
                random_event = random.choice(events[:50])  # From first 50 events
                username = random_event['actor']['login']
                user_url = f'https://api.github.com/users/{username}'
                print(term.dim + f"Selected random user: {username}" + term.normal)
            else:
                raise Exception("No recent events found")

        # Fetch user data
        print(term.dim + "Fetching user profile..." + term.normal)
        user_response = requests.get(user_url, headers=headers, timeout=10)
        user_response.raise_for_status()
        user_data = user_response.json()

        print(term.green + f"✓ Successfully fetched profile for {user_data['login']}" + term.normal)

        # Fetch user repositories for language stats
        print(term.dim + "Analyzing repositories..." + term.normal)
        repos_url = f'https://api.github.com/users/{username}/repos'
        repos_params = {'sort': 'updated', 'per_page': 100}
        repos_response = requests.get(repos_url, headers=headers, params=repos_params, timeout=10)

        repos = []
        total_stars = 0
        languages = {}

        if repos_response.status_code == 200:
            repos = repos_response.json()
            print(term.dim + f"Found {len(repos)} repositories" + term.normal)

            for repo in repos:
                if repo.get('stargazers_count'):
                    total_stars += repo['stargazers_count']
                if repo.get('language'):
                    languages[repo['language']] = languages.get(repo['language'], 0) + 1

        # Get most used language
        primary_language = max(languages, key=languages.get) if languages else "Unknown"
        print(term.dim + f"Primary language: {primary_language}" + term.normal)

        # Parse join date
        joined_year = user_data['created_at'][:4] if user_data.get('created_at') else "Unknown"

        # Create data structure with real_data flag
        result = {
            'id': user_data['id'],
            'username': user_data['login'],
            'name': user_data.get('name', user_data['login']),
            'company': user_data.get('company', 'Not specified') or 'Not specified',
            'location': user_data.get('location', 'Not specified') or 'Not specified',
            'language': primary_language,
            'repos': user_data.get('public_repos', 0),
            'followers': user_data.get('followers', 0),
            'following': user_data.get('following', 0),
            'stars': total_stars,
            'contributions': random.randint(100, 5000),  # API doesn't provide this easily
            'joined': joined_year,
            'bio': user_data.get('bio', '') or '',
            'blog': user_data.get('blog', '') or '',
            'avatar_url': user_data.get('avatar_url', ''),
            'real_data': True  # Flag to indicate real data
        }

        print(term.green + "✓ Data processing complete" + term.normal)
        return result

    except requests.RequestException as e:
        print(term.red + f"API Error: {e}" + term.normal)
        if hasattr(e, 'response') and e.response is not None:
            print(term.red + f"HTTP Status: {e.response.status_code}" + term.normal)
            if e.response.status_code == 403:
                print(term.yellow + "Rate limit exceeded or token invalid!" + term.normal)
            elif e.response.status_code == 404:
                print(term.yellow + f"User '{username}' not found!" + term.normal)
        print(term.yellow + "Falling back to dummy data..." + term.normal)
        return generate_dummy_data()
    except Exception as e:
        print(term.red + f"Error: {e}" + term.normal)
        print(term.yellow + "Falling back to dummy data..." + term.normal)
        return generate_dummy_data()


def generate_dummy_data():
    """Generate dummy user data as fallback"""
    users = ["octocat", "torvalds", "gaearon", "tj", "sindresorhus", "addyosmani", "getify", "kentcdodds", "wesbos",
             "bradtraversy"]
    languages = ["JavaScript", "Python", "Go", "Rust", "TypeScript", "Java", "C++", "PHP", "Ruby", "Swift"]
    companies = ["GitHub", "Google", "Microsoft", "Meta", "Netflix", "Spotify", "Stripe", "Vercel", "OpenAI",
                 "Freelancer"]
    locations = ["San Francisco", "Berlin", "London", "Tokyo", "New York", "Amsterdam", "Toronto", "Sydney",
                 "Stockholm", "Zürich"]

    user_id = random.randint(1, 5000000)
    username = random.choice(users)

    return {
        'id': user_id,
        'username': username,
        'name': username,
        'company': random.choice(companies),
        'location': random.choice(locations),
        'language': random.choice(languages),
        'repos': random.randint(1, 500),
        'followers': random.randint(100, 10000),
        'following': random.randint(50, 1000),
        'stars': random.randint(100, 50000),
        'contributions': random.randint(100, 5000),
        'joined': random.randint(2014, 2024),
        'bio': '',
        'blog': '',
        'avatar_url': '',
        'real_data': False  # Flag to indicate dummy data
    }


def format_number(num):
    if num > 999:
        return f"{num // 1000}.{(num % 1000) // 100}k"
    return str(num)


def get_avatar_ascii(user_data):
    """Download avatar and convert to ASCII using chafa"""
    try:
        # Use real avatar URL if available, otherwise construct from ID
        if 'avatar_url' in user_data and user_data['avatar_url']:
            url = user_data['avatar_url']
        else:
            url = f"https://avatars.githubusercontent.com/u/{user_data['id']}"

        response = requests.get(url, timeout=5)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name

        # Use chafa to convert to ASCII
        result = subprocess.run(['chafa', '--size=24x12', tmp_path],
                                capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            return result.stdout.strip().split('\n')
        else:
            return ["🎨 Avatar", "   Loading", "   Failed"] + [""] * 9

    except Exception as e:
        print(term.yellow + f"Avatar error: {e}" + term.normal)
        return ["🎨 Avatar", "   Not", "   Available"] + [""] * 9


def check_rate_limit():
    """Check GitHub API rate limit"""
    headers = get_github_headers()
    try:
        response = requests.get('https://api.github.com/rate_limit', headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            remaining = data['rate']['remaining']
            limit = data['rate']['limit']
            print(term.dim + f"API Rate Limit: {remaining}/{limit} remaining" + term.normal)

            if remaining < 10:
                print(term.red + "Warning: Low API rate limit remaining!" + term.normal)

    except Exception:
        pass  # Ignore rate limit check errors


def main():
    print(term.clear)

    # Parse command line arguments
    username = sys.argv[1] if len(sys.argv) > 1 else None

    if username:
        print(f"Fetching data for user: {username}")
    else:
        print("Fetching random GitHub user...")

    # Check rate limit
    check_rate_limit()

    # Fetch user data (real or dummy)
    data = fetch_real_user_data(username)

    # Show loading
    print("Loading avatar...")

    # Get avatar
    avatar_lines = get_avatar_ascii(data)

    # Clear and start display
    print(term.clear)

    # Starting position
    start_y = 2
    avatar_width = 26
    info_x = avatar_width + 2

    # Display header at info position - show real name if available
    display_name = data.get('name', data['username'])
    if display_name != data['username'] and data.get('name'):
        header_text = f"{display_name} ({data['username']})"
    else:
        header_text = data['username']

    with term.location(info_x, start_y):
        print(term.bold_green + header_text + term.normal +
              term.white + "@" + term.normal +
              term.bold_blue + "github" + term.normal)

    with term.location(info_x, start_y + 1):
        print(term.dim + "─" * 40 + term.normal)

    # Display avatar and info side by side
    info_items = [
        ("🆔", "User ID", str(data['id']), term.red),
        ("👤", "Username", data['username'], term.green),
        ("🏢", "Company", data.get('company', 'Not specified'), term.yellow),
        ("📍", "Location", data.get('location', 'Not specified'), term.blue),
        ("💻", "Primary Lang", data['language'], term.magenta),
        ("📚", "Repositories", format_number(data['repos']), term.cyan),
        ("👥", "Followers", format_number(data['followers']), term.red),
        ("👤", "Following", format_number(data['following']), term.green),
        ("⭐", "Total Stars", format_number(data['stars']), term.yellow),
        ("📈", "Contributions", format_number(data['contributions']), term.blue),
        ("🗓️", "Joined", str(data['joined']), term.magenta),
    ]

    # Add bio if available
    if data.get('bio') and data['bio'].strip():
        info_items.append(("💬", "Bio", data['bio'][:30] + "..." if len(data['bio']) > 30 else data['bio'], term.cyan))

    # Add blog if available
    if data.get('blog') and data['blog'].strip():
        blog_url = data['blog'][:25] + "..." if len(data['blog']) > 25 else data['blog']
        info_items.append(("🌐", "Website", blog_url, term.blue))

    # Display avatar and info
    max_lines = max(len(avatar_lines), len(info_items) + 2)

    for i in range(max_lines):
        # Display avatar line
        if i < len(avatar_lines):
            with term.location(0, start_y + i):
                print(avatar_lines[i])

        # Display info line
        if i >= 2 and (i - 2) < len(info_items):
            icon, label, value, color = info_items[i - 2]
            with term.location(info_x, start_y + i):
                print(f"{color}{icon}{term.normal} {term.bold_white}{label:<14}{term.normal} {value}")

    # Move to next section
    current_y = start_y + max_lines + 2
    # Final newlines
    print(term.move_y(current_y))


if __name__ == "__main__":
    main()
