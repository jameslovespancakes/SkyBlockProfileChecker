#!/usr/bin/env python3
"""
SkyBlock Profile Checker - Minimal CLI tool for Hypixel SkyBlock profiles

Usage:
    1. Install dependencies: pip install requests
    2. Run: python skyblock_checker.py
    3. Get API key from Hypixel Developer Dashboard (https://developer.hypixel.net)
       - Provide via prompt, environment variable HYPIXEL_API_KEY, or edit constant below

Author: Hypixel SkyBlock Profile Checker
Version: 1.0.0
"""

import os
import sys
import json
import math
import argparse
import requests
from typing import Optional, Dict, Any

# Configuration - Edit this to hardcode your API key (optional)
HYPIXEL_API_KEY = None  # Set to "your-api-key-here" if you want to hardcode it

# API endpoints
MOJANG_API_URL = "https://api.mojang.com/users/profiles/minecraft/{username}"
HYPIXEL_API_URL = "https://api.hypixel.net/v2/skyblock/profiles"

# Cache for username to UUID conversions (single run only)
username_cache: Dict[str, str] = {}

# Global debug flag
DEBUG = False


def get_api_key() -> str:
    """Get API key from constant, environment variable, or user prompt."""
    # Check hardcoded constant first
    if HYPIXEL_API_KEY:
        return HYPIXEL_API_KEY
    
    # Check environment variable
    env_key = os.environ.get("HYPIXEL_API_KEY")
    if env_key:
        return env_key
    
    # Prompt user for API key
    print("Enter your Hypixel API key:")
    api_key = input("> ").strip()
    if not api_key:
        print("Error: API key cannot be empty")
        sys.exit(1)
    
    return api_key


def normalize_uuid(uuid_str: str) -> str:
    """Remove dashes from UUID string to normalize it."""
    return uuid_str.replace("-", "").lower()


def is_valid_uuid(uuid_str: str) -> bool:
    """Check if string is a valid UUID (with or without dashes)."""
    normalized = normalize_uuid(uuid_str)
    return len(normalized) == 32 and all(c in "0123456789abcdef" for c in normalized)


def username_to_uuid(username: str) -> Optional[str]:
    """Convert Minecraft username to UUID using Mojang API."""
    # Check cache first
    if username.lower() in username_cache:
        if DEBUG:
            print(f"[DEBUG] Found cached UUID for '{username}': {username_cache[username.lower()]}")
        return username_cache[username.lower()]
    
    try:
        print(f"Resolving username '{username}'...")
        url = MOJANG_API_URL.format(username=username)
        if DEBUG:
            print(f"[DEBUG] Mojang API URL: {url}")
        
        response = requests.get(url, timeout=10)
        
        if DEBUG:
            print(f"[DEBUG] Mojang API response status: {response.status_code}")
            print(f"[DEBUG] Mojang API response headers: {dict(response.headers)}")
            print(f"[DEBUG] Mojang API response body: {response.text[:500]}")
        
        if response.status_code == 204 or response.status_code == 404:
            print(f"Error: Username '{username}' not found")
            return None
        
        if response.status_code != 200:
            print(f"Error: Failed to resolve username (HTTP {response.status_code})")
            if DEBUG:
                print(f"[DEBUG] Full response: {response.text}")
            return None
        
        data = response.json()
        uuid = data.get("id")
        if uuid:
            # Cache the result
            username_cache[username.lower()] = uuid
            if DEBUG:
                print(f"[DEBUG] Successfully resolved '{username}' to UUID: {uuid}")
            return uuid
        
        print("Error: Invalid response from Mojang API")
        if DEBUG:
            print(f"[DEBUG] Response data: {data}")
        return None
        
    except requests.exceptions.Timeout:
        print("Error: Request to Mojang API timed out")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error: Network error while resolving username: {e}")
        if DEBUG:
            print(f"[DEBUG] Full exception: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        print("Error: Invalid JSON response from Mojang API")
        if DEBUG:
            print(f"[DEBUG] JSON decode error: {str(e)}")
            print(f"[DEBUG] Raw response: {response.text}")
        return None


def fetch_skyblock_profiles(uuid: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Fetch SkyBlock profiles from Hypixel API."""
    try:
        print(f"Fetching SkyBlock profiles for UUID: {uuid}")
        
        params = {"uuid": uuid}
        headers = {"API-Key": api_key}
        
        if DEBUG:
            print(f"[DEBUG] Hypixel API URL: {HYPIXEL_API_URL}")
            print(f"[DEBUG] Request params: {params}")
            print(f"[DEBUG] Request headers: {headers}")
        
        response = requests.get(
            HYPIXEL_API_URL,
            params=params,
            headers=headers,
            timeout=10
        )
        
        if DEBUG:
            print(f"[DEBUG] Hypixel API response status: {response.status_code}")
            print(f"[DEBUG] Hypixel API response headers: {dict(response.headers)}")
            print(f"[DEBUG] Hypixel API response body (first 1000 chars): {response.text[:1000]}")
        
        if response.status_code == 429:
            print("Error: Rate limited. Please wait a moment and try again.")
            if DEBUG:
                rate_limit_headers = {
                    k: v for k, v in response.headers.items() 
                    if 'ratelimit' in k.lower() or 'retry' in k.lower()
                }
                print(f"[DEBUG] Rate limit headers: {rate_limit_headers}")
            return None
        
        if response.status_code == 403:
            print("Error: Invalid API key or access denied")
            if DEBUG:
                print(f"[DEBUG] Full 403 response: {response.text}")
            return None
        
        if response.status_code == 404:
            print("Error: Player not found or has no SkyBlock profiles")
            if DEBUG:
                print(f"[DEBUG] Full 404 response: {response.text}")
            return None
        
        if response.status_code == 422:
            print("Error: Invalid data provided to API")
            if DEBUG:
                print(f"[DEBUG] Full 422 response: {response.text}")
            return None
        
        if response.status_code != 200:
            print(f"Error: Hypixel API returned HTTP {response.status_code}")
            if DEBUG:
                print(f"[DEBUG] Full response: {response.text}")
            return None
        
        data = response.json()
        
        if DEBUG:
            print(f"[DEBUG] Parsed JSON data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            if isinstance(data, dict) and 'profiles' in data:
                profiles = data.get('profiles', [])
                print(f"[DEBUG] Number of profiles found: {len(profiles) if profiles else 0}")
        
        # Check success flag
        if not data.get("success", False):
            cause = data.get("cause", "Unknown error")
            print(f"Error: Hypixel API request failed - {cause}")
            if DEBUG:
                print(f"[DEBUG] Full error response: {data}")
            return None
        
        return data
        
    except requests.exceptions.Timeout:
        print("Error: Request to Hypixel API timed out")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error: Network error while fetching profiles: {e}")
        if DEBUG:
            print(f"[DEBUG] Full exception: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        print("Error: Invalid JSON response from Hypixel API")
        if DEBUG:
            print(f"[DEBUG] JSON decode error: {str(e)}")
            print(f"[DEBUG] Raw response: {response.text}")
        return None


def calculate_skyblock_level(experience: float) -> int:
    """Calculate SkyBlock level from experience points."""
    return math.floor(experience / 100)


def format_number(num: float) -> str:
    """Format number with commas for readability."""
    return f"{num:,.2f}"


def get_nested_value(data: Dict, *keys, default=None):
    """Safely get nested dictionary value."""
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def print_profile(profile: Dict[str, Any], uuid: str, is_selected: bool):
    """Print formatted profile information."""
    profile_name = profile.get("cute_name", "Unknown")
    member_data = profile.get("members", {}).get(uuid, {})
    game_mode = profile.get("game_mode")
    
    # Header
    if is_selected:
        print(f"\n[Selected] Profile: {profile_name}")
    else:
        print(f"\nProfile: {profile_name}")
    
    # Game mode (if available)
    if game_mode:
        print(f"  Game Mode: {game_mode.title()}")
    
    # SkyBlock Level
    experience = get_nested_value(member_data, "leveling", "experience")
    if experience is not None:
        level = calculate_skyblock_level(experience)
        print(f"  SkyBlock Level: {level} (experience: {experience:.0f})")
    else:
        print("  SkyBlock Level: N/A")
    
    # Coins in purse
    coin_purse = member_data.get("coin_purse", 0)
    print(f"  Purse: {format_number(coin_purse)}")
    
    # Bank balance
    bank_balance = get_nested_value(profile, "banking", "balance", default=0)
    print(f"  Bank: {format_number(bank_balance)}")
    
    # Skills
    skills = []
    skill_names = ["mining", "farming", "combat", "foraging", "fishing", "enchanting", "alchemy", "taming"]
    
    for skill in skill_names:
        exp_key = f"experience_skill_{skill}"
        if exp_key in member_data:
            skills.append(f"{skill}={member_data[exp_key]:.0f}")
    
    if skills:
        print(f"  Skills (exp): {', '.join(skills[:5])}")  # Show first 5 skills
    else:
        print("  Skills (exp): not available")


def main():
    """Main entry point."""
    global DEBUG
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='SkyBlock Profile Checker')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--json', action='store_true', help='Output raw JSON response')
    args = parser.parse_args()
    
    DEBUG = args.debug
    
    print("=== SkyBlock Profile Checker ===\n")
    if DEBUG:
        print("[DEBUG] Debug mode enabled")
    
    # Get API key
    api_key = get_api_key()
    if DEBUG:
        print(f"[DEBUG] Using API key: {api_key[:8]}...{api_key[-4:]}")
    
    # Get username or UUID
    print("\nEnter Minecraft username or UUID:")
    user_input = input("> ").strip()
    
    if not user_input:
        print("Error: Username/UUID cannot be empty")
        sys.exit(1)
    
    # Determine if input is UUID or username
    uuid = None
    if is_valid_uuid(user_input):
        uuid = normalize_uuid(user_input)
        print(f"Using UUID: {uuid}")
    else:
        # Assume it's a username, try to convert
        uuid = username_to_uuid(user_input)
        if not uuid:
            sys.exit(1)
        print(f"Username resolved to UUID: {uuid}")
    
    # Fetch SkyBlock profiles
    data = fetch_skyblock_profiles(uuid, api_key)
    if not data:
        sys.exit(1)
    
    # Output raw JSON if requested
    if args.json:
        print("\n=== RAW JSON RESPONSE ===")
        print(json.dumps(data, indent=2))
        print("=== END RAW JSON ===")
    
    profiles = data.get("profiles", [])
    
    if DEBUG:
        print(f"[DEBUG] Retrieved {len(profiles)} profiles from API")
        if profiles:
            for i, profile in enumerate(profiles):
                print(f"[DEBUG] Profile {i}: {profile.get('cute_name', 'Unknown')} (ID: {profile.get('profile_id', 'Unknown')})")
    
    if not profiles:
        print("\nNo SkyBlock profiles found for this player")
        if DEBUG:
            print("[DEBUG] This could mean:")
            print("[DEBUG] 1. Player has never played SkyBlock")
            print("[DEBUG] 2. Player's profiles are private")
            print("[DEBUG] 3. API returned empty profiles array")
        sys.exit(0)
    
    print(f"\nFound {len(profiles)} profile(s):")
    print("-" * 50)
    
    # Find selected profile
    selected_profile_id = None
    for profile in profiles:
        if profile.get("selected", False):
            selected_profile_id = profile.get("profile_id")
            break
    
    # Print each profile
    for profile in profiles:
        is_selected = profile.get("profile_id") == selected_profile_id
        print_profile(profile, uuid, is_selected)
    
    print("-" * 50)
    print("\nDone!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
