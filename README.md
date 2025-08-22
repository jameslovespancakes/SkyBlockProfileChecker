# SkyBlock Profile Checker

A minimal CLI tool for checking Hypixel SkyBlock profiles using the updated Hypixel API v2.

## Setup

1. **Install Python 3.9+** (if not already installed)

2. **Install dependencies:**
   ```bash
   pip install requests 2.31.0
   ```
   Or directly:
   ```bash
   pip install requests
   ```

## Usage

Run the script:
```bash
python skyblock_checker.py
```

### Debug Mode

For troubleshooting API issues, use debug mode:
```bash
python skyblock_checker.py --debug
```

To see the raw JSON response from the API:
```bash
python skyblock_checker.py --json
```

Combine both for maximum debugging information:
```bash
python skyblock_checker.py --debug --json
```

## API Key Configuration

You can provide your Hypixel API key in three ways:

1. **Interactive prompt** - Enter it when the script asks
2. **Environment variable** - Set `HYPIXEL_API_KEY` before running:
   ```bash
   set HYPIXEL_API_KEY=your-api-key-here
   python skyblock_checker.py
   ```
3. **Hardcode in script** - Edit `skyblock_checker.py` and set the `HYPIXEL_API_KEY` constant at the top

## Features

- **Updated API v2 Support** - Uses the latest Hypixel API endpoints
- **Comprehensive Debugging** - Debug mode shows detailed API request/response info
- **Username/UUID Support** - Converts Minecraft usernames to UUIDs automatically
- **Flexible Input** - Accepts both dashed and undashed UUID formats
- **Profile Details** - Shows SkyBlock level, coins, bank balance, game mode, and skill experience
- **Multi-Profile Display** - Shows all profiles with clear indication of selected profile
- **Error Handling** - Comprehensive error handling for API failures and rate limits
- **Performance** - Simple username caching for the current session

## Example Output

```
=== SkyBlock Profile Checker ===

Enter Minecraft username or UUID:
> Technoblade

Username resolved to UUID: b876ec32e396476ba1158438d83c67d4
Found 2 profile(s):
--------------------------------------------------

[Selected] Profile: Apple
  SkyBlock Level: 263 (experience: 26350)
  Purse: 1,234,567.89
  Bank: 50,000,000.00
  Skills (exp): mining=3500000, farming=2800000, combat=4200000

Profile: Banana
  SkyBlock Level: 45 (experience: 4500)
  Purse: 50,000.00
  Bank: 100,000.00
  Skills (exp): mining=150000, farming=200000
--------------------------------------------------
Done!
```

## Getting a Hypixel API Key

**New Method (Recommended):**
1. Visit the [Hypixel Developer Dashboard](https://developer.hypixel.net)
2. Create an application and get your API key
3. This method provides higher rate limits for production applications

**Legacy Method (Lower Rate Limits):**
1. Join Hypixel server in Minecraft
2. Run `/api new` command
3. Copy the generated API key from chat

**Note:** The Developer Dashboard method is strongly recommended as it provides higher rate limits and better support for applications.

## API Changes & Updates

**Latest Update (August 2024):**
- Updated to use Hypixel API v2 endpoints
- Fixed deprecated `/skyblock/profiles` endpoint
- Enhanced debugging capabilities with `--debug` and `--json` flags
- Added support for game mode display (Ironman, Stranded, etc.)

## Requirements

- Python 3.9+
- `requests` library (2.31.0+)
- Valid Hypixel API key from [Developer Dashboard](https://developer.hypixel.net)

## Troubleshooting

**Common Issues:**

1. **"This endpoint has been deprecated"** - The script now uses the updated v2 API endpoints
2. **404 Player not found** - Player may not have SkyBlock profiles or profiles are private
3. **403 Access denied** - Check your API key is valid and from the Developer Dashboard
4. **Rate limited (429)** - Wait a moment before retrying

**Debug Mode:**
Use `--debug` flag to see detailed API request/response information for troubleshooting.
