import os
import logging
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from listeners import register_listeners
from termcolor import colored

# Load environment variables
load_dotenv()

# Verify environment variables
REQUIRED_VARS = ["SLACK_BOT_TOKEN", "SLACK_APP_TOKEN", "TRELLO_API_KEY", "TRELLO_TOKEN", "TRELLO_API_SECRET", "BOARD_ID"]

# Check if all required variables are present
missing_vars = [var for var in REQUIRED_VARS if not os.getenv(var)]
if missing_vars:
    print(colored(f"Error: Missing environment variables: {', '.join(missing_vars)}", "red"))
    exit(1)

# Debug: Print loaded variables (safely)
print(colored("\nEnvironment variables loaded:", "cyan"))
for var in REQUIRED_VARS:
    value = os.getenv(var)
    masked_value = value[:4] + "..." if value else "Not set"
    print(colored(f"{var}: {masked_value}", "white"))

# Initialization
app = App(token=os.getenv("SLACK_BOT_TOKEN"))
logging.basicConfig(level=logging.DEBUG)

# Register Listeners
register_listeners(app)

# Start Bolt app
if __name__ == "__main__":
    try:
        print(colored("\nStarting Slack bot...", "cyan"))
        handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
        handler.start()
    except Exception as e:
        print(colored(f"Error starting app: {str(e)}", "red"))
