# -*- coding: utf-8 -*-
import os
import time
import re
from slackclient import SlackClient
import random
import logging
from get_paladar_menu import get_paladar_menu
from llista_menjar import FoodManager

SHRUG = '¯\_(ツ)_/¯'

FOOD = FoodManager()

RANDOM_RESPONSES = [
    'In the forest you met a redhead woman. Now you know nothing. You returned home empty handed.', 
    'You\'ve stepped into a pile of dung. Now you stink. Nothing else happened.',
    'It was a really nice and sunny day, so you sat under a tree and enjoyed the weather...',
    'It was a cool and refreshing night, so you made a campfire out in the woods.',
    'As you were strolling through the forest, you noticed a group of people building a giant wall on a small meadow. Their leader, an orange man with crazy hair, looked dangerous, so you decided to head back to your home'
]

COMMANDS = {
    'menu': get_paladar_menu,
    'list': FOOD.create_list,
    'done': FOOD.end_list,
}

BOT_NAME = 'MORT DE GANA'

RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response
    default_response = '{} {}'.format(
        random.choice(RANDOM_RESPONSES), SHRUG
    )
    default_response = SHRUG

    # Finds and executes the given command, filling in response
    response = None
    response_function = COMMANDS.get(command.split()[0])
    if response_function:
        response = response_function(channel, ' '.join(command.split()[1:]))
    if not response and FOOD.status(channel):
        response = FOOD.add_to_list(channel, ' '.join(command.split()[0:]))

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response,
        username=BOT_NAME
    )


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        logging.basicConfig()
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
