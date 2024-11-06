
import json
import os
from itch_majordomo import ItchMajordomo

def load_config(config_path="examples/config.json"):
    with open(config_path, 'r') as f:
        return json.load(f)

def main():
    config = load_config()

    with ItchMajordomo(config["game_id"], config["itchio_cookie"], headless=False) as majordomo:  # headless=False during dev
        majordomo.update_display_names(config["display_names"])

if __name__ == "__main__":
    main()