import discord
from discord.ext import commands
from flask import Flask, jsonify
from flask_cors import CORS
import threading
import json
import os

DISCORD_TOKEN = os.getenv('token')

# Set up the Flask web server
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# File paths
LATMESSAGE_FILE = 'latmessage.json'
MESSAGES_FILE = 'messages.json'


def load_json(filename):
    """Load JSON data from a file."""
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    return {}


def save_json(filename, data):
    """Save JSON data to a file."""
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)


# Initialize latest message
latest_message = load_json(LATMESSAGE_FILE)


@app.route('/latestnew', methods=['GET'])
def get_latest_message():
    return jsonify(latest_message)


def run_flask():
    app.run(host='0.0.0.0', port=3000)


# Set up the Discord bot
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True  # Enable the message content intent

bot = commands.Bot(command_prefix='!', intents=intents)

# Replace with your target channel ID
TARGET_CHANNEL_ID = 1129108219533480028


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


@bot.event
async def on_message(message):
    global latest_message

    # Check if the message is from the bot itself
    if message.author == bot.user:
        return

    # Check if the message is from the specified channel
    if message.channel.id == TARGET_CHANNEL_ID:
        # Update the latest message
        latest_message = {
            'content': message.content,
            'author': str(message.author),
            'timestamp': str(message.created_at)
        }
        save_json(LATMESSAGE_FILE, latest_message)

        # Append to all messages history
        all_messages = load_json(MESSAGES_FILE)
        if not isinstance(all_messages, list):
            all_messages = [
            ]  # Initialize as an empty list if not already a list

        all_messages.append({
            'content': message.content,
            'author': str(message.author),
            'timestamp': str(message.created_at)
        })
        save_json(MESSAGES_FILE, all_messages)

    # Ensure other commands and events can still be processed
    await bot.process_commands(message)


bot_token = DISCORD_TOKEN


def start_discord_bot():
    bot.run(bot_token)


# Start both the Flask web server and Discord bot
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    start_discord_bot()
