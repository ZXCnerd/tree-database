import telebot
import json
import datetime
from colorama import *

init(autoreset=True)

TOKEN = open('.TOKEN').readline().strip()
bot = telebot.TeleBot(TOKEN)

# List of admin user IDs
ADMINS = [5183966807, 5123126840, 6878830888, 5862526446]

# Хранение данных о деревьях в JSON файле
def load_trees():
    try:
        with open('trees.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_trees(trees):
    with open('trees.json', 'w') as file:
        json.dump(trees, file)

def load_unofficial_trees():
    try:
        with open('trees_unofficial.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_unofficial_trees(trees):
    with open('trees_unofficial.json', 'w') as file:
        json.dump(trees, file)

def load_user_stats():
    try:
        with open('user_stats.json', 'r') as file:
            user_stats = json.load(file)
            print("User stats loaded:", user_stats)
            return user_stats
    except FileNotFoundError:
        print("user_stats.json not found, initializing empty stats.")
        return {}

def save_user_stats(user_stats):
    with open('user_stats.json', 'w') as file:
        json.dump(user_stats, file)
        print("User stats saved:", user_stats)

trees = load_trees()
unofficial_trees = load_unofficial_trees()
user_stats = load_user_stats()

@bot.message_handler(commands=['start', 'help'])
def send_help(message):
    help_message = (
        "Доступные команды:\n"
        "/list — список деревьев.\n"
        "/add — добавить новое дерево.\n"
        "/info [tree] — информация о дереве с названием [tree].\n"
        "/search [query] — поиск деревьев по названию.\n"
        "/unofficial_list — список неподтвержденных деревьев.\n"
        "/approve [tree] — одобрить дерево из списка неподтвержденных.\n"
        "/backup — создать резервную копию списка деревьев.\n"
        "/backup_unofficial — создать резервную копию списка неподтвержденных деревьев.\n"
        "/remove [tree] — удалить дерево (доступно только для администраторов).\n"
        "/stats — статистика бота.\n"
        "/my_stats — ваша статистика.\n"
        "/test — тестовая команда для вывода имени пользователя."
    )
    bot.reply_to(message, help_message)
    print(Fore.CYAN + 't.me/' + str(message.from_user.username), message.text, ' ' * 10,
          Fore.RED + f'[{datetime.datetime.now()}]')

@bot.message_handler(commands=['list'])
def list_trees(message):
    tree_list = "\n".join(trees.keys()) or "Нет доступных деревьев."
    bot.reply_to(message, f"Список деревьев:\n{tree_list}")
    print(Fore.CYAN + 't.me/' + str(message.from_user.username), message.text, ' ' * 10,
          Fore.RED + f'[{datetime.datetime.now()}]')

@bot.message_handler(commands=['add'])
def add_tree(message):
    bot.reply_to(message, "Введите название нового дерева:")
    bot.register_next_step_handler(message, process_tree_name)

@bot.message_handler(commands=['remove'])
def remove_tree(message):
    if message.from_user.id in ADMINS:
        tree_name = message.text.split(' ', 1)[1] if len(message.text.split(' ')) > 1 else None
        if tree_name and tree_name in trees:
            trees.pop(tree_name)
            bot.reply_to(message, f"Успешно удалено дерево {tree_name}")
            save_trees(trees)
        else:
            bot.reply_to(message, "Дерево не найдено.")
    else:
        bot.reply_to(message, "Эта команда доступна только для администраторов.")
    print(Fore.CYAN + 't.me/' + str(message.from_user.username), message.text, ' ' * 10,
          Fore.RED + f'[{datetime.datetime.now()}]')

def process_tree_name(message):
    tree_name = message.text.replace(' ', '_').replace('\n', '_')
    if tree_name in trees or tree_name in unofficial_trees:
        bot.reply_to(message, "Это дерево уже существует. Попробуйте другое название.")
        return

    bot.reply_to(message, "Введите описание нового дерева:")
    bot.register_next_step_handler(message, process_tree_description, tree_name)

    print(Fore.CYAN + 't.me/' + str(message.from_user.username), message.text, ' ' * 10,
          Fore.RED + f'[{datetime.datetime.now()}]')

def process_tree_description(message, tree_name):
    tree_description = message.text
    if message.from_user.id in ADMINS:
        trees[tree_name] = tree_description  # Сохраняем новое дерево в основном списке
        save_trees(trees)
        bot.reply_to(message, f"Дерево '{tree_name}' успешно добавлено с описанием: {tree_description}")
    else:
        unofficial_trees[tree_name] = tree_description  # Сохраняем новое дерево в неподтвержденном списке
        save_unofficial_trees(unofficial_trees)
        bot.reply_to(message, f"Дерево '{tree_name}' добавлено в список неподтвержденных.")

    # Обновляем статистику пользователя
    user_id = message.from_user.id
    if user_id not in user_stats:
        user_stats[user_id] = {'trees_added': 0}
    user_stats[user_id]['trees_added'] += 1
    save_user_stats(user_stats)
    print("User stats updated:", user_stats)

    print(Fore.CYAN + 't.me/' + str(message.from_user.username), message.text, ' ' * 10,
          Fore.RED + f'[{datetime.datetime.now()}]')

@bot.message_handler(commands=['info'])
def tree_info(message):
    tree_name = message.text.split(' ', 1)[1] if len(message.text.split(' ')) > 1 else None
    if tree_name and tree_name in trees:
        info = trees[tree_name]
        bot.reply_to(message, f"Информация о {tree_name}:\n{info}")
    else:
        bot.reply_to(message, "Дерево не найдено.")

    print(Fore.CYAN + 't.me/' + str(message.from_user.username), message.text, ' ' * 10,
          Fore.RED + f'[{datetime.datetime.now()}]')

@bot.message_handler(commands=['backup'])
def backup(message):
    if message.from_user.id in ADMINS:
        with open('trees.json', 'r') as file:
            content = file.read()
        with open('trees_backup.json', 'w') as backup_file:
            backup_file.write(content)
        bot.reply_to(message, "Резервная копия списка деревьев создана.")
        print('Резервные данные сохранены')
    else:
        bot.reply_to(message, "Нет доступа.")
        print(message.from_user.id, 'пытается создать бекап')

    print(Fore.CYAN + 't.me/' + str(message.from_user.username), message.text, ' ' * 10,
          Fore.RED + f'[{datetime.datetime.now()}]')

@bot.message_handler(commands=['backup_unofficial'])
def backup_unofficial(message):
    if message.from_user.id in ADMINS:
        with open('trees_unofficial.json', 'r') as file:
            content = file.read()
        with open('trees_unofficial_backup.json', 'w') as backup_file:
            backup_file.write(content)
        bot.reply_to(message, "Резервная копия списка неподтвержденных деревьев создана.")
        print('Резервные данные неподтвержденных деревьев сохранены')
    else:
        bot.reply_to(message, "Нет доступа.")
        print(message.from_user.id, 'пытается создать бекап неподтвержденных деревьев')

    print(Fore.CYAN + 't.me/' + str(message.from_user.username), message.text, ' ' * 10,
          Fore.RED + f'[{datetime.datetime.now()}]')

@bot.message_handler(commands=['unofficial_list'])
def list_unofficial_trees(message):
    unofficial_tree_list = "\n".join([f"{name}: {desc}" for name, desc in unofficial_trees.items()]) or "Нет неподтвержденных деревьев."
    bot.reply_to(message, f"Список неподтвержденных деревьев:\n{unofficial_tree_list}")
    print(Fore.CYAN + 't.me/' + str(message.from_user.username), message.text, ' ' * 10,
          Fore.RED + f'[{datetime.datetime.now()}]')

@bot.message_handler(commands=['approve'])
def approve_tree(message):
    if message.from_user.id in ADMINS:
        tree_name = message.text.split(' ', 1)[1] if len(message.text.split(' ')) > 1 else None
        if tree_name and tree_name in unofficial_trees:
            trees[tree_name] = unofficial_trees.pop(tree_name)
            save_trees(trees)
            save_unofficial_trees(unofficial_trees)
            bot.reply_to(message, f"Дерево '{tree_name}' успешно одобрено и добавлено в список.")
        else:
            bot.reply_to(message, "Дерево не найдено в неподтвержденных.")
    else:
        bot.reply_to(message, "Нет доступа.")
        print(message.from_user.id, 'пытается одобрить дерево')

    print(Fore.CYAN + 't.me/' + str(message.from_user.username), message.text, ' ' * 10,
          Fore.RED + f'[{datetime.datetime.now()}]')

@bot.message_handler(commands=['search'])
def search_trees(message):
    query = message.text.split(' ', 1)[1] if len(message.text.split(' ')) > 1 else None
    if query:
        query = query.lower()
        results = [tree for tree in trees.keys() if query in tree.lower()]
        if results:
            result_message = "\n".join(results)
            bot.reply_to(message, f"Найденные деревья:\n{result_message}")
        else:
            bot.reply_to(message, "Ничего не найдено.")
    else:
        bot.reply_to(message, "Введите запрос для поиска.")

    print(Fore.CYAN + 't.me/' + str(message.from_user.username), message.text, ' ' * 10,
          Fore.RED + f'[{datetime.datetime.now()}]')

@bot.message_handler(commands=['stats'])
def stats(message):
    total_trees = len(trees)
    unofficial_trees_count = len(unofficial_trees)
    stats_message = (
        f"Статистика бота:\n"
        f"Всего деревьев: {total_trees}\n"
        f"Неподтвержденных деревьев: {unofficial_trees_count}"
    )
    bot.reply_to(message, stats_message)
    print(Fore.CYAN + 't.me/' + str(message.from_user.username), message.text, ' ' * 10,
          Fore.RED + f'[{datetime.datetime.now()}]')

@bot.message_handler(commands=['my_stats'])
def my_stats(message):
    user_id = str(message.from_user.id)
    if user_stats.get(user_id, 0):
        trees_added = user_stats[user_id]['trees_added']
        stats_message = f"Ваши добавленные деревья: {trees_added}"
    else:
        stats_message = "Вы еще не добавляли деревьев."
    bot.reply_to(message, stats_message)
    print(Fore.CYAN + 't.me/' + str(message.from_user.username), message.text, ' ' * 10,
          Fore.RED + f'[{datetime.datetime.now()}]')

@bot.message_handler(commands=['test'])
def test(message):
    bot.reply_to(message, str(message.from_user.username))

@bot.message_handler(content_types='text')
def message_detect(message):
    print(Fore.CYAN + 't.me/' + str(message.from_user.username), message.text, ' ' * 10,
          Fore.RED + f'[{datetime.datetime.now()}]')

bot.infinity_polling()
