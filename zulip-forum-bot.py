import re
import sys
import unicodedata

import zulip

# Either email addresses (string) or user_id (integer).  Email addresses will
# be converted to user_id:s on startup.
ALLOW_USERS = {
    '*',
    }

ALLOW_EMOJIS = {
    'check_mark',
    'question',
    }

ALLOW_STREAMS = {
    'forum'
    }

#EMOJI_MAP = {
#    'tada': 'check_mark',
#    }

#def handle_message(event):
#    # https://zulip.com/api/get-events#message
#    print('MESSAGE', event)

def handle_reaction(event):
    print('REACTION', event)
    # https://zulip.com/api/get-events#reaction-add
    if event['op'] != 'add':
        return
    user_id = event['user_id']
    if not (user_id in ALLOW_USERS or '*' in ALLOW_USERS):
        return

    emoji_name = event['emoji_name']
    emoji_code = event['emoji_code']
    emoji = chr(int(emoji_code, 16))
    if not (emoji_name in ALLOW_EMOJIS or '*' in ALLOW_EMOJIS):
        return
    if event['reaction_type'] != 'unicode_emoji':
        return

    # Get reacted-to message
    # https://zulip.com/api/get-messages
    message_id = event['message_id']
    msgs = client.get_messages({'anchor': message_id, 'num_before': 1, 'num_after': 1})
    msg = msgs['messages'][0]
    # Filter out private messages
    if msg['type'] != 'stream':
        return
    stream_id = msg['stream_id']
    # Check if allowed streams
    if stream_id not in ALLOW_STREAMS: # integer IDs added here at startup
        return

    old_topic = msg['subject']  # someday, this field may change
    #emoji = EMOJI_MAP.get(emoji, emoji)
    if unicodedata.category(old_topic[0]) == 'So':
        new_topic = emoji + old_topic[1:]
    else:
        new_topic = emoji + old_topic

    # By default change topic for entire thread.  If it is scissors, cut the
    # thread into a new one.
    propagate_mode = 'change_all'
    if emoji_name == 'scissors':
        propagate_mode = 'change_later'

    # Change topic
    # https://zulip.com/api/update-message
    # PATCH
    msg = {
        'message_id': message_id,
        'topic': new_topic,
        'propagate_mode': propagate_mode,
        'send_notification_to_old_thread': False,
        'send_notification_to_new_thread': False,
        }
    client.update_message(msg)

def event_callback(event):
    print(event['type'])
    #if event['type'] == 'message':
    #    handle_message(event)
    if event['type'] == 'reaction':
        handle_reaction(event)

client = zulip.Client(config_file=sys.argv[1])

import configparser
config = configparser.ConfigParser()
config.read(sys.argv[1])
if 'forum' in config:
    fconfig = config['forum']
    if 'users' in fconfig:
        ALLOW_USERS = set(x.lower() for x in re.split(r'[, ]+', fconfig['users']))
    if 'streams' in fconfig:
        ALLOW_STREAMS = set(x.lower() for x in re.split(r'[, ]+', fconfig['streams']))
    if 'emojis' in fconfig:
        ALLOW_EMOJIS = set(x.lower() for x in re.split(r'[, ]+', fconfig['emojis']))

# Unfortunately API doesn't conveniently have a way to the stream name from
# stream_id, and stream_id is returned with the messages.  Look up the
# stream_ids for each stream_name once at the start.
ALLOW_STREAMS = set(x.lower() if isinstance(x, str) else x
                    for x in ALLOW_STREAMS)
for sdata in client.get_streams()['streams']:
    if sdata['name'].lower() in ALLOW_STREAMS:
        ALLOW_STREAMS.add(sdata['stream_id'])

# Now we have to get user_id:s the same way.
for user in client.get_members({"client_gravatar": True})['members']:
    if user['email'].lower() in ALLOW_USERS:
        ALLOW_USERS.add(user['user_id'])
# This method does not work until Zulip 4.0:
#for user_email in ALLOW_USERS:
#    if not isinstance(user_email, str):
#        continue
#    ret = client.call_endpoint(url="/users/%s"%(user_email.replace('/', '')),
#        method="GET",
#        )
#    print(ret)
#    if ret['result'] != 'success':
#        print("User not found: %s"%(user_email, ))
#        continue
#    ALLOW_USERS.add(ret['user']['user_id'])

print(ALLOW_USERS)
print(ALLOW_STREAMS)
print(ALLOW_EMOJIS)

# Begin main callback loop
print("starting")
client.call_on_each_event(event_callback, ['message', 'reaction'])
