import requests
import re

def get_github_profile(github_url: str):
    """
    Extract username from GitHub URL and fetch profile data from the official GitHub REST API.
    """
    if not github_url:
        return None
        
    github_url = github_url.strip()
    
    # Extract username
    username = None
    if "/" not in github_url and "." not in github_url:
        username = github_url
    else:
        # Match github.com/<username> or www.github.com/<username>
        match = re.search(r'(?:github\.com/)([a-zA-Z0-9_\-]+)', github_url, re.IGNORECASE)
        if match:
            username = match.group(1)
            
    if not username:
        print(f"Invalid GitHub URL or username could not be extracted: {github_url}")
        return None
        
    print(f"GitHub username detected: {username}")
    url = f"https://api.github.com/users/{username}"
    
    try:
        print("Calling GitHub API...")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("GitHub profile fetched successfully.")
            return response.json()
        elif response.status_code == 404:
            print(f"GitHub user '{username}' not found.")
            return None
        elif response.status_code == 403:
            print("GitHub API rate limit exceeded or access forbidden.")
            return None
        else:
            print(f"GitHub API returned status code {response.status_code}.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Network error when calling GitHub API: {e}")
        return None
