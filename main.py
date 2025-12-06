# Monitor Users Roblox Activity, Friends and Followers
# Made by https://github.com/vmmie, first posted at https://github.com/vmmie/roblox-stalker

import requests
import time
import json
from datetime import datetime, UTC

# ===========================
# CONFIGURATION
# ===========================
ROBLOX_USER_ID = "YOUR_TARGETS_ROBLOX_ID"  # Replace with the target user ID
DISCORD_WEBHOOK_URL = "YOUR_WEBHOOK_URL"  # Replace with your Discord webhook URL
DISCORD_USER_ID_TO_PING = "YOUR_DISCORD_USER_ID"  # Replace with Discord user ID to ping (optional)
CHECK_INTERVAL = 60  # Time between checks in seconds (default: 60 seconds)

# Set to False if friends list tracking causes issues (will only track count)
DETAILED_FRIENDS_TRACKING = True

# ===========================
# ROBLOX API FUNCTIONS
# ===========================

def get_user_info(user_id):
    """Get basic user information"""
    try:
        response = requests.get(f"https://users.roblox.com/v1/users/{user_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error fetching user info: {e}")
        return None

def get_user_presence(user_id):
    """Get user's online status and game info"""
    try:
        payload = {"userIds": [user_id]}
        response = requests.post("https://presence.roblox.com/v1/presence/users", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("userPresences"):
                return data["userPresences"][0]
        return None
    except Exception as e:
        print(f"Error fetching user presence: {e}")
        return None

def get_friends_list(user_id):
    """Get user's friends list (limited to 200 by Roblox API)"""
    try:
        friends = {}
        url = f"https://friends.roblox.com/v1/users/{user_id}/friends"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()

            # The response structure is {"data": [{"id": ..., "name": ..., ...}]}
            for friend in data.get("data", []):
                friend_id = friend.get("id")
                friend_name = friend.get("name") or friend.get("username") or f"User_{friend_id}"
                if friend_id:
                    friends[friend_id] = friend_name

            return friends
        else:
            print(f"Friends API returned status {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching friends list: {e}")
        return None

def get_friends_count(user_id):
    """Get user's friends count"""
    try:
        response = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/friends/count")
        if response.status_code == 200:
            return response.json().get("count", 0)
        return None
    except Exception as e:
        print(f"Error fetching friends count: {e}")
        return None

def get_followers_count(user_id):
    """Get user's followers count"""
    try:
        response = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/followers/count")
        if response.status_code == 200:
            return response.json().get("count", 0)
        return None
    except Exception as e:
        print(f"Error fetching followers count: {e}")
        return None

def get_game_details(place_id):
    """Get game name from place ID"""
    try:
        response = requests.get(f"https://games.roblox.com/v1/games/multiget-place-details?placeIds={place_id}")
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return data[0].get("name", "Unknown Game")
        return "Unknown Game"
    except Exception as e:
        print(f"Error fetching game details: {e}")
        return "Unknown Game"

# ===========================
# DISCORD WEBHOOK FUNCTIONS
# ===========================

def send_discord_notification(message, ping=True):
    """Send a notification to Discord webhook"""
    try:
        embed = {
            "title": "🔔 Roblox User Activity Change Detected",
            "description": message,
            "color": 5814783,  # Blue color
            "timestamp": datetime.now(UTC).isoformat(),
            "footer": {
                "text": "Roblox Monitor"
            }
        }

        payload = {
            "content": f"<@{DISCORD_USER_ID_TO_PING}>" if ping and DISCORD_USER_ID_TO_PING != "YOUR_DISCORD_USER_ID" else None,
            "embeds": [embed]
        }

        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print(f"✓ Discord notification sent: {message}")
        else:
            print(f"✗ Failed to send Discord notification: {response.status_code}")
    except Exception as e:
        print(f"Error sending Discord notification: {e}")

# ===========================
# MONITORING LOGIC
# ===========================

def monitor_user():
    """Main monitoring loop"""
    global DETAILED_FRIENDS_TRACKING  # Declare global to modify it

    print("=" * 60)
    print("Roblox User Monitor - Starting...")
    print("=" * 60)

    # Get initial user info
    user_info = get_user_info(ROBLOX_USER_ID)
    if not user_info:
        print("✗ Failed to fetch user info. Check the user ID.")
        return

    username = user_info.get("name", "Unknown")
    print(f"Monitoring user: {username} (ID: {ROBLOX_USER_ID})")
    print(f"Check interval: {CHECK_INTERVAL} seconds")
    print(f"Detailed friends tracking: {DETAILED_FRIENDS_TRACKING}")
    print("=" * 60)

    # Initialize previous state
    previous_state = {
        "friends_dict": {},
        "friends_count": None,
        "followers_count": None,
        "online_status": None,
        "game_id": None,
        "game_name": None
    }

    # Get initial state
    if DETAILED_FRIENDS_TRACKING:
        print("Loading initial friends list...")
        friends_dict = get_friends_list(ROBLOX_USER_ID)
        if friends_dict is not None:
            previous_state["friends_dict"] = friends_dict
            print(f"Initial friends loaded: {len(friends_dict)} (API limit: 200)")
            if len(friends_dict) >= 200:
                print("⚠ Warning: User may have more than 200 friends. Only first 200 tracked.")
        else:
            print("⚠ Could not load friends list, falling back to count-only tracking")
            DETAILED_FRIENDS_TRACKING = False

    friends_count = get_friends_count(ROBLOX_USER_ID)
    followers_count = get_followers_count(ROBLOX_USER_ID)
    presence = get_user_presence(ROBLOX_USER_ID)

    if friends_count is not None:
        previous_state["friends_count"] = friends_count
        print(f"Initial friends count: {friends_count}")

    if followers_count is not None:
        previous_state["followers_count"] = followers_count
        print(f"Initial followers count: {followers_count}")

    if presence:
        previous_state["online_status"] = presence.get("userPresenceType", 0)
        previous_state["game_id"] = presence.get("placeId")
        if presence.get("placeId"):
            game_name = get_game_details(presence.get("placeId"))
            previous_state["game_name"] = game_name
            print(f"Initial status: Online - Playing {game_name}")
        else:
            status_map = {0: "Offline", 1: "Online", 2: "In Game", 3: "In Studio"}
            print(f"Initial status: {status_map.get(previous_state['online_status'], 'Unknown')}")

    print("")
    print("Monitoring started. Press Ctrl+C to stop.")
    print("=" * 60)

    # Main monitoring loop
    try:
        while True:
            time.sleep(CHECK_INTERVAL)

            # Check friends
            if DETAILED_FRIENDS_TRACKING:
                # Detailed tracking - show who was added/removed
                current_friends_dict = get_friends_list(ROBLOX_USER_ID)
                if current_friends_dict is not None and previous_state["friends_dict"] is not None:
                    previous_ids = set(previous_state["friends_dict"].keys())
                    current_ids = set(current_friends_dict.keys())

                    # Find added friends
                    added_ids = current_ids - previous_ids
                    if added_ids:
                        added_names = [current_friends_dict[fid] for fid in added_ids]
                        if len(added_names) == 1:
                            message = f"**{username}** added a new friend: **{added_names[0]}**"
                        else:
                            names_list = ", ".join([f"**{name}**" for name in added_names])
                            message = f"**{username}** added {len(added_names)} new friends: {names_list}"
                        send_discord_notification(message)

                    # Find removed friends
                    removed_ids = previous_ids - current_ids
                    if removed_ids:
                        removed_names = [previous_state["friends_dict"][fid] for fid in removed_ids]
                        if len(removed_names) == 1:
                            message = f"**{username}** removed a friend: **{removed_names[0]}**"
                        else:
                            names_list = ", ".join([f"**{name}**" for name in removed_names])
                            message = f"**{username}** removed {len(removed_names)} friends: {names_list}"
                        send_discord_notification(message)

                    # Update the friends dictionary
                    if added_ids or removed_ids:
                        previous_state["friends_dict"] = current_friends_dict
            else:
                # Count-only tracking - fallback mode
                current_friends = get_friends_count(ROBLOX_USER_ID)
                if current_friends is not None and previous_state["friends_count"] is not None:
                    if current_friends != previous_state["friends_count"]:
                        diff = current_friends - previous_state["friends_count"]
                        change = f"+{diff}" if diff > 0 else str(diff)
                        message = f"**{username}** friends count changed: {previous_state['friends_count']} → {current_friends} ({change})"
                        send_discord_notification(message)
                        previous_state["friends_count"] = current_friends

            # Check followers count
            current_followers = get_followers_count(ROBLOX_USER_ID)
            if current_followers is not None and previous_state["followers_count"] is not None:
                if current_followers != previous_state["followers_count"]:
                    diff = current_followers - previous_state["followers_count"]
                    change = f"+{diff}" if diff > 0 else str(diff)
                    message = f"**{username}** followers count changed: {previous_state['followers_count']} → {current_followers} ({change})"
                    send_discord_notification(message)
                    previous_state["followers_count"] = current_followers

            # Check presence (online status and game)
            current_presence = get_user_presence(ROBLOX_USER_ID)
            if current_presence:
                current_status = current_presence.get("userPresenceType", 0)
                current_game_id = current_presence.get("placeId")

                # Check online status change
                if previous_state["online_status"] is not None:
                    if current_status != previous_state["online_status"]:
                        status_map = {0: "Offline", 1: "Online", 2: "In Game", 3: "In Studio"}
                        message = f"**{username}** status changed: {status_map.get(previous_state['online_status'], 'Unknown')} → {status_map.get(current_status, 'Unknown')}"
                        send_discord_notification(message)
                        previous_state["online_status"] = current_status

                # Check game change
                if current_game_id != previous_state["game_id"]:
                    if current_game_id:
                        current_game_name = get_game_details(current_game_id)
                        if previous_state["game_id"]:
                            message = f"**{username}** switched games: {previous_state['game_name']} → {current_game_name}"
                        else:
                            message = f"**{username}** started playing: {current_game_name}"
                        send_discord_notification(message)
                        previous_state["game_name"] = current_game_name
                    else:
                        if previous_state["game_id"]:
                            message = f"**{username}** stopped playing: {previous_state['game_name']}"
                            send_discord_notification(message)
                            previous_state["game_name"] = None

                    previous_state["game_id"] = current_game_id

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checked - No changes detected")

    except KeyboardInterrupt:
        print("")
        print("=" * 60)
        print("Monitor stopped by user.")
        print("=" * 60)

# ===========================
# MAIN EXECUTION
# ===========================

if __name__ == "__main__":
    # Validate configuration
    if ROBLOX_USER_ID == "YOUR_ROBLOX_USER_ID":
        print("✗ Please configure ROBLOX_USER_ID in the script")
        exit(1)

    if DISCORD_WEBHOOK_URL == "YOUR_DISCORD_WEBHOOK_URL":
        print("✗ Please configure DISCORD_WEBHOOK_URL in the script")
        exit(1)

    monitor_user()
