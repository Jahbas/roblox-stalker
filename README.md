#  Roblox-Stalker

A Python script that monitors Roblox user activity and sends real-time Discord webhook notifications when changes are detected.

## ✨ Features

- **Friends Tracking**: Monitors friend additions and removals with usernames (up to 200 friends due to Roblox API limitations)
- **Followers Count**: Tracks follower count changes with +/- differences
- **Online Status**: Detects when users go online/offline or enter Roblox Studio
- **Game Activity**: Monitors what game the user is playing and detects game switches
- **Discord Notifications**: Sends embedded messages with optional user pings
- **Automatic Fallback**: Switches to count-only tracking if detailed tracking fails

## 📋 Requirements

- Python 3.7+
- `requests` library

## 🚀 Installation

1. Clone this repository:
```bash
git clone https://github.com/vmmie/roblox-stalker.git
cd roblox-stalker
```

2. Install dependencies:
```bash
pip install requests
```

## ⚙️ Configuration

Open `main.py` and configure the following variables:

```python
ROBLOX_USER_ID = "1234567890"  # Target Roblox user ID
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/..."  # Your webhook URL
DISCORD_USER_ID_TO_PING = "YOUR_DISCORD_USER_ID"  # Discord user ID to ping (optional)
CHECK_INTERVAL = 60  # Seconds between checks
DETAILED_FRIENDS_TRACKING = True  # Set to False for count-only tracking
```

### Getting Required Information

**Roblox User ID:**
- Visit the user's profile: `https://www.roblox.com/users/[USER_ID]/profile`
- Copy the numeric ID from the URL

**Discord Webhook URL:**
- Server Settings → Integrations → Webhooks → Create Webhook
- Copy the webhook URL

**Discord User ID:**
- Enable Developer Mode (User Settings → Advanced)
- Right-click your username → Copy User ID

## 🎯 Usage

Run the script:
```bash
python main.py
```

Stop monitoring with `Ctrl+C`.

## 📊 Example Notifications

- `vmset added a new friend: vmsways`
- `vmset followers count changed: 150 → 155 (+5)`
- `vmset status changed: Offline → Online`
- `vmset started playing: Blade Ball!`
- `vmset switched games: Blade Ball → Random Condo Game`

## ⚠️ Known Limitations

- Username data may not always be available (shows `User_ID` as fallback)
- Rate limiting may occur with very frequent checks

## 🔧 Troubleshooting

**"User_ID" shown instead of names:**
- This happens when the Roblox API doesn't return username data
- Set `DETAILED_FRIENDS_TRACKING = False` to use count-only tracking

**Friends tracking not working:**
- Ensure the user's profile is public
- Try increasing `CHECK_INTERVAL` to avoid rate limits
- Enable count-only mode as fallback

## 📝 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

---

**Note:** This project uses public Roblox APIs and respects rate limits. Always use responsibly and in accordance with Roblox's Terms of Service.
