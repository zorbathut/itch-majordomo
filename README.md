# Itch Majordomo

This is a small utility function that allows you to edit the names of Itch-Butler-uploaded files. It's essentially an out-of-band fix for https://github.com/itchio/butler/issues/129.

It is extremely ugly because it uses web scraping to work. Perhaps someday it will stop working! Perhaps Butler will then support the desired feature. Perhaps it will not. The tea leaves tell me nothing; the future is a mystery, shrouded in darkness.

## Installation

```bash
pip install itch-majordomo
```

Note: This relies on Selenium to work. I vaguely recall that Selenium has other requirements. Maybe this won't work on a system without a GUI? I dunno, man. Send me a pull request if these installation instructions require more info.

## Quick Start

```python
from itch_majordomo import ItchMajordomo

# Initialize with your game ID and authentication cookie
with ItchMajordomo("your-game-id", "your-cookie") as majordomo:
    # Update display names for your builds
    majordomo.update_display_names({
        "hypercube-linux.zip": "hypercube-v0.2.3-linux.zip",
        "hypercube-windows.zip": "hypercube-v0.2.3-windows.zip"
    })
```

## Authentication

You'll need two pieces of information:
1. Your game's ID (found in the URL when editing your game)
2. Your itch.io authentication cookie

To get your authentication cookie:
1. Log into itch.io
2. Open your browser's developer tools (usually F12)
3. Go to the Application/Storage tab
4. Look for Cookies > itch.io
5. Copy the value of the 'itchio' cookie

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

This tool is not limited to just updating display names; I'm happy to add support for whatever weird thing you want that isn't supported by Butler.
