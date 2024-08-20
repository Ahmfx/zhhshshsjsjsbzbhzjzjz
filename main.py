import requests
import threading
from queue import Queue
from random import choice
from telethon import TelegramClient, events

# Function to generate random usernames
def usernames():
    k = ''.join(choice('qwertyuiopasdfghjklzxcvbnm') for i in range(1))
    n = ''.join(choice('qwertyuiopasdfghjklzxcvbnm1234567890') for i in range(1))
    c = ''.join(choice('qwertyuiopasdfghjklzxcvbnm1234567890') for i in range(1))
    z = ''.join(choice('qwertyuiopasdfghjklzxcvbnm1234567890') for i in range(1))
    g = ''.join(choice('qwertyuiopasdfghjklzxcvbnm1234567890') for i in range(1))
    _ = ''.join("_")
    e = ''.join(choice('qwertyuiopasdfghjklzxcvbnm') for i in range(1))
    u1 = k + c + e + e + e
    u2 = k + z + z + z + n
    u3 = k + k + k + n + c
    u4 = k + k + k + _ + n
    u5 = k + _ + k + n + n
    u6 = k + k + _ + n + n
    u7 = k + k + n + _ + n
    u8 = k + _ + n + k + n
    u9 = k + n + _ + k + n
    u10 = k + n + k + _ + n
    u11 = k + n + n + k + n + k
    u12 = k + k + k + n + n + n
    u13 = n + k + k + k + n + k
    u14 = n + k + k + k + k + n
    u15 = k + n + n + n + k + k
    u16 = k + k + k + k + n + n
    s = u1, u2, u3, u4, u5, u6, u7, u8, u9, u10, u11, u12, u13, u14, u15, u16
    return choice(s)

# Function to check username availability with proxy support
def check_username(username, proxy=None):
    url = f"https://fragment.com/api/v1/usernames/{username}"
    proxies = {"http": proxy, "https": proxy} if proxy else None
    response = requests.get(url, proxies=proxies)
    
    if response.status_code == 200:
        data = response.json()
        return data['available']
    elif response.status_code == 429:  # Handle flood status
        return 'flood'
    else:
        return None

# Function to reserve username with proxy support
def reserve_username(username, token, proxy=None):
    url = f"https://fragment.com/api/v1/usernames/{username}/reserve"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    proxies = {"http": proxy, "https": proxy} if proxy else None
    response = requests.post(url, headers=headers, proxies=proxies)
    
    return response.status_code == 200

# Thread function to check and reserve username
def check_and_reserve(queue, token, client, proxy, notify_id):
    while not queue.empty():
        username = queue.get()
        available = check_username(username, proxy)
        
        if available is None:
            client.send_message(notify_id, f'Failed to check the username {username}. Please try again later.')
        elif available == 'flood':
            client.send_message(notify_id, f'The username {username} is currently in flood status. Please try again later.')
        elif available:
            client.send_message(notify_id, f"The username '{username}' is available.")
            success = reserve_username(username, token, proxy)
            if success:
                client.send_message(notify_id, f"The username '{username}' has been successfully reserved.")
                client.send_message('arageDoctor', f"The username '{username}' has been successfully reserved.")
            else:
                client.send_message(notify_id, f"Failed to reserve the username '{username}'. Please try again later.")
        else:
            client.send_message(notify_id, f"The username '{username}' is taken.")
        queue.task_done()

# Function to pin a username in flood status
def pin_username(username, token, client, proxy, notify_id, attempts):
    for _ in range(attempts):
        available = check_username(username, proxy)
        if available == 'flood':
            success = reserve_username(username, token, proxy)
            if success:
                client.send_message(notify_id, f"The username '{username}' has been successfully reserved after flood status.")
                client.send_message('arageDoctor', f"The username '{username}' has been successfully reserved after flood status.")
                break
        else:
            client.send_message(notify_id, f"The username '{username}' is not in flood status or is already taken.")
            break

# Telegram command handler to check and reserve username
async def start(event):
    await event.respond('Welcome! Send /check to check availability or /reserve <token> <proxy> <notify_username> to reserve.')

async def check(event):
    username = usernames()
    proxy = event.message.text.split()[1] if len(event.message.text.split()) > 1 else None
    available = check_username(username, proxy)
    
    if available is None:
        await event.respond('Failed to check the username. Please try again later.')
    elif available == 'flood':
        await event.respond(f'The username {username} is currently in flood status. Please try again later.')
    elif available:
        await event.respond(f"The username '{username}' is available.")
    else:
        await event.respond(f"The username '{username}' is taken.")

async def reserve(event):
    args = event.message.text.split()
    token = args[1]
    proxy = args[2] if len(args) > 2 else None
    notify_username = args[3] if len(args) > 3 else event.sender.username
    
    queue = Queue()
    for _ in range(30):  # Generate 30 random usernames
        queue.put(usernames())
    
    for _ in range(30):  # Create 30 threads
        thread = threading.Thread(target=check_and_reserve, args=(queue, token, client, proxy, notify_username))
        thread.start()

async def pin(event):
    args = event.message.text.split()
    username = args[1]
    token = args[2]
    attempts = int(args[3])
    proxy = args[4] if len(args) > 4 else None
    notify_username = args[5] if len(args) > 5 else event.sender.username
    
    thread = threading.Thread(target=pin_username, args=(username, token, client, proxy, notify_username, attempts))
    thread.start()

async def status(event):
    await event.respond('The bot is running and ready to check and reserve usernames.')

# Initialize the Telegram client
api_id = '28006651'
api_hash = 'cc087eb52f8ec7819703ecd28f600e07'
bot_token = '7512172162:AAHo_Qq1OIsV5b1WkScWDWreyIonNblN9lM'

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Register event handlers
client.add_event_handler(start, events.NewMessage(pattern='/start'))
client.add_event_handler(check, events.NewMessage(pattern='/check'))
client.add_event_handler(reserve, events.NewMessage(pattern='/reserve'))
client.add_event_handler(pin, events.NewMessage(pattern='/pin'))
client.add_event_handler(status, events.NewMessage(pattern='/فحص'))

# Start the client
client.run_until_disconnected()
