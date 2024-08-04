import telebot
import requests
import threading
import time
from datetime import datetime

bot_token = 'YOUR_TOKEN'
bot = telebot.TeleBot(bot_token)
github_repo = 'OWNER/REPONAME'
#admin_id = 'TELEGRAM ADMIN FOR DEBUGGING LOGS'
users = set()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    users.add(message.chat.id)
    bot.reply_to(message, "Hello, you are now subscribed to bootcamp_appointment repository updates.")


def get_latest_commit_data():
    url = f'https://api.github.com/repos/{github_repo}/branches'
    response = requests.get(url)

    if response.status_code != 200:
        print("Failed to fetch branches:", response.status_code)
        return None

    branches = response.json()
    last_commit_date = None
    commit_message = None

    for branch in branches:
        branch_name = branch['name']
        branch_url = f'https://api.github.com/repos/{github_repo}/commits/{branch_name}'
        branch_response = requests.get(branch_url)

        if branch_response.status_code == 200:
            commit = branch_response.json()
            commit_date_str = commit['commit']['committer']['date']
            commit_date = datetime.strptime(commit_date_str, '%Y-%m-%dT%H:%M:%SZ')

            if last_commit_date is None or commit_date > last_commit_date:
                last_commit_date = commit_date
                commit_message = commit['commit']['message']
        else:
            print(f"Failed to fetch commits for branch {branch_name}: {branch_response.status_code}")

    return commit_message


def check_repo():
    latest_commit_message = get_latest_commit_data()

    while True:
        new_commit_message = get_latest_commit_data()

        if new_commit_message != latest_commit_message:
            latest_commit_message = new_commit_message

            for user_id in users:
                bot.send_message(user_id, f"New commit: {latest_commit_message}")
                time.sleep(1)

        time.sleep(10)


threading.Thread(target=check_repo, daemon=True).start()
bot.infinity_polling()
