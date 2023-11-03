import telegram
import json
from telethon.sync import TelegramClient
from telegram import Bot

TELEGRAM_BOT_TOKEN = '6159029946:AAGKDsOLrYifByB9-ZMuuO5tsigNWOF2sS4'

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
bot = Bot(token='TELEGRAM_BOT_TOKEN')

# Замените 'CHAT_ID' на идентификатор чата, который вас интересует
chat_username = 'nevzorovtvchat'

# Замените 'api_id' и 'api_hash' на ваши значения
api_id = '18920580'
api_hash = 'f94ba8acc61d1a5069a1e55a277295d1'

# Введите номер телефона и код для авторизации
phone_number = '+79278444153'
code = 'N1998n1998n'

list_members_premium = []
list_members_true_story = []

with TelegramClient('session_name', api_id, api_hash) as client:
    # Авторизуйтесь
    client.start(phone_number, code)

    # Получите идентификатор чата по никнейму
    chat = client.get_entity(chat_username)

    # Выведите информацию о чате
    print("Chat ID:", chat.id)
    print("Chat Title:", chat.title)

    # Получите список участников чата
    members = client.get_participants(chat)
    print("Members count:", len(members))

    for member in members:
        if member.premium:
            list_members_premium.append(member)

        if not member.stories_unavailable:
            # if member.premium:
            # print(f"Username: {member.username}, ID: {member.id}")
            # print(f'{stories_hidden} stories hidden')
            list_members_true_story.append(member)
    print("Total members premium:", len(list_members_premium))
    print("Total members true story:", len(list_members_true_story))

with open('list_members_true_story.txt', 'w', encoding='utf-8') as f:
    for member in list_members_true_story:
        if member.username != None:
            f.write(f"{member.username}\n")


# stories_hidden указывает на то, скрыты ли истории пользователя. Если значение этого атрибута равно True, это означает, что истории скрыты.
#
# stories_unavailable указывает на доступность историй пользователя. Если значение этого атрибута равно True, это означает, что истории недоступны.

# User(id=5533800528, ...) - Это объект пользователя Telegram с идентификатором 5533800528. Он содержит информацию о пользователе. Вот некоторые атрибуты этого объекта:
#
# is_self: Пользователь не является самим собой (False).
# first_name: Имя пользователя, в данном случае, "Марселлас".
# username: Никнейм пользователя, "marseller_money".
# status: Статус пользователя (UserStatusRecently()).
# lang_code: Код языка пользователя (пусто).
# phone: Номер телефона пользователя (пусто).
# User(id=460468191, ...) - Это другой объект пользователя Telegram с идентификатором 460468191. Он также содержит информацию о пользователе. Некоторые атрибуты этого объекта:
#
# is_self: Пользователь не является самим собой (False).
# first_name: Имя пользователя, "Андрюха".
# username: Никнейм пользователя, "id_egoyan".
# status: Статус пользователя (UserStatusRecently()).
# lang_code: Код языка пользователя, "ru".
# phone: Номер телефона пользователя (пусто).
# total=2 - Общее количество пользователей (или участников чата) в списке, которое равно 2.
