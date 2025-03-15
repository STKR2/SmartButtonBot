import telebot
from telebot import types
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
admin_id = int(os.getenv("ADMIN_ID"))

temp_button = {}
buttons = []
start_message = "اضغط /admin للتحكم ."

def send_welcome(message):
    markup = types.InlineKeyboardMarkup()

    
    positions = {
        'top-left': [],
        'top-center': [],
        'top-right': [],
        'center-left': [],
        'center-center': [],
        'center-right': [],
        'bottom-left': [],
        'bottom-center': [],
        'bottom-right': []
    }

    for button in buttons:
        if button['type'] == 'link':
            btn = types.InlineKeyboardButton(button['name'], url=button['content'])
        else:
            btn = types.InlineKeyboardButton(button['name'], callback_data=button['content'])

        positions[button['position']].append(btn)

    if positions['top-left']:
        markup.row(*positions['top-left'])
    if positions['top-center']:
        markup.row(*positions['top-center'])
    if positions['top-right']:
        markup.row(*positions['top-right'])
    if positions['center-left']:
        markup.row(*positions['center-left'])
    if positions['center-center']:
        markup.row(*positions['center-center'])
    if positions['center-right']:
        markup.row(*positions['center-right'])
    if positions['bottom-left']:
        markup.row(*positions['bottom-left'])
    if positions['bottom-center']:
        markup.row(*positions['bottom-center'])
    if positions['bottom-right']:
        markup.row(*positions['bottom-right'])

    bot.send_message(message.chat.id, start_message, reply_markup=markup)

@bot.message_handler(commands=['start'])
def start_command(message):
    send_welcome(message)

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == admin_id:
        markup = types.InlineKeyboardMarkup(row_width=1)
        add_button = types.InlineKeyboardButton("اضف زر", callback_data="add_button")
        delete_button = types.InlineKeyboardButton("حذف زر", callback_data="delete_button")
        set_start_message = types.InlineKeyboardButton("ضع كليشة ستارت", callback_data="set_start_message")
        markup.add(add_button)
        markup.add(delete_button, set_start_message)

        bot.send_message(message.chat.id, "ok .", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "ماعندك صلاحية .")
        
@bot.callback_query_handler(func=lambda call: call.data == "set_start_message")
def ask_start_message(call):
    if call.from_user.id == admin_id:
        bot.send_message(call.message.chat.id, "أرسل رسالة ستارت الجديدة :")
        bot.register_next_step_handler(call.message, set_start_message)

def set_start_message(message):
    global start_message
    start_message = message.text
    bot.send_message(message.chat.id, "تم !")

@bot.callback_query_handler(func=lambda call: call.data == "add_button")
def ask_button_name(call):
    if call.from_user.id == admin_id:
        bot.send_message(call.message.chat.id, "أرسل اسم الزر:")
        bot.register_next_step_handler(call.message, get_button_name)

def get_button_name(message):
    temp_button['name'] = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("رابط", callback_data="button_type_link"))
    markup.add(types.InlineKeyboardButton("كلام", callback_data="button_type_text"))
    bot.send_message(message.chat.id, "اختار نوع الزر:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["button_type_link", "button_type_text"])
def ask_button_content(call):
    if call.from_user.id == admin_id:
        if call.data == "button_type_link":
            temp_button['type'] = 'link'
            bot.send_message(call.message.chat.id, "أرسل الرابط:")
        else:
            temp_button['type'] = 'text'
            bot.send_message(call.message.chat.id, "أرسل النص:")
        bot.register_next_step_handler(call.message, get_button_content)

def get_button_content(message):
    temp_button['content'] = message.text
    markup = types.InlineKeyboardMarkup(row_width=2)
    

    markup.add(
        types.InlineKeyboardButton("أعلى في المنتصف", callback_data="button_position_top-center"),
        types.InlineKeyboardButton("أسفل في المنتصف", callback_data="button_position_bottom-center")
    )
    markup.add(
        types.InlineKeyboardButton("أعلى يسار", callback_data="button_position_top-left"),
        types.InlineKeyboardButton("أعلى يمين", callback_data="button_position_top-right")
    )
    markup.add(
        types.InlineKeyboardButton("وسط يسار", callback_data="button_position_center-left"),
        types.InlineKeyboardButton("وسط يمين", callback_data="button_position_center-right")
    )
    markup.add(
        types.InlineKeyboardButton("وسط في المنتصف", callback_data="button_position_center-center")
    )
    markup.add(
        types.InlineKeyboardButton("أسفل يسار", callback_data="button_position_bottom-left"),
        types.InlineKeyboardButton("أسفل يمين", callback_data="button_position_bottom-right")
    )

    bot.send_message(message.chat.id, "اختار مكان الزر:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("button_position_"))
def finalize_button(call):
    if call.from_user.id == admin_id:
        position = call.data.split('_')[-1]
        temp_button['position'] = position
        buttons.append(temp_button.copy())
        bot.send_message(call.message.chat.id, "تم إضافة الزر بنجاح !")      
        send_welcome(call.message)

@bot.callback_query_handler(func=lambda call: call.data == "delete_button")
def ask_button_name_delete(call):
    if call.from_user.id == admin_id:
        bot.send_message(call.message.chat.id, "أرسل اسم الزر الذي تريد حذفه:")
        bot.register_next_step_handler(call.message, delete_button)

def delete_button(message):
    global buttons
    button_name = message.text
    buttons = [btn for btn in buttons if btn['name'] != button_name]
    bot.send_message(message.chat.id, f"تم حذف الزر '{button_name}' بنجاح !")
    send_welcome(message)

@bot.callback_query_handler(func=lambda call: True)
def handle_button_click(call):
    if call.data in [button['content'] for button in buttons if button['type'] == 'text']:
        bot.send_message(call.message.chat.id, f"{call.data}")

bot.polling()
