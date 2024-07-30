import time
from telebot   import TeleBot, util, apihelper, types

import secret
from handlers.Audience_meneger import Audience
from handlers.error_handler import make_warning

__all__ = ['form', 'callback_inline']


bot = TeleBot(secret.TOKEN)
audience = Audience(r"data/audience.json")

def markup_generator(sub_id):
    SubscriptionsOfSubId= audience.get_subscriptions(sub_id)
    keys_audience= tuple(audience)

    if len(audience) > len(SubscriptionsOfSubId)*2:
        buttons= [
            [state, {'callback_data': f"{i}, {sub_id}"}]
            for i, state in enumerate(audience)
        ]

        for state in SubscriptionsOfSubId:
            index= keys_audience.index(state)
            buttons[index][0]+= " ✅"

    else:
        buttons= [
                [state+ " ✅", {'callback_data': f"{i}, {sub_id}"}]
                for i, state in enumerate(audience)
            ]

        for state in audience:
            if state in SubscriptionsOfSubId:
                continue
            index= keys_audience.index(state)
            buttons[index][0]= state

    buttons.append( ("Зберегти ⚙️", {'callback_data': f"\'S\', {sub_id}"}) )

    buttons.append(
        ("Всі "+("❌" if SubscriptionsOfSubId else "✅"),
        {'callback_data': f"\'A\', {sub_id}"})
    )

    markup = types.InlineKeyboardMarkup(row_width=2)
    for i in range(len(buttons)//2):
        markup.add(
            types.InlineKeyboardButton(buttons[i*2][0], callback_data=buttons[i*2][1]['callback_data']),
            types.InlineKeyboardButton(buttons[i*2+1][0], callback_data=buttons[i*2+1][1]['callback_data'])
        )

    return markup
    #return util.quick_markup(dict(buttons))

def uncustomizer_chek(chat_id, user_id):
    if chat_id == user_id: #chat.type  == "private"
        return False
    else:
        return not (
            user_id in map(
                lambda admin: admin.user.id,
                bot.get_chat_administrators(chat_id)
            )
            or
            user_id == 1087968824 # anonymous id = 1087968824. Additional information: https://t.me/GroupAnonymousBot
        )


def form(message, security_level=None):
    if uncustomizer_chek(message.chat.id, message.from_user.id):
        bot.send_message(message.chat.id,
            'Налаштувати надсилання повідомлень про початок або відбій тривоги може тільки <b>автор групи</b> або <b>адмініcтратор</b>. І бот повинен мати права адмінстратора',
            parse_mode='html'
        )
        return

    if message.reply_to_message:
        info_about_replying_chat = message.reply_to_message.forward_from_chat

        if info_about_replying_chat == None or info_about_replying_chat.type != 'channel':
            bot.send_message(
                message.chat.id,
                "Налаштовувати сповіщення таким чином можна тільки для каналів\n<b><a href='https://t.me/SupYb/24'>Інструкція налаштування для каналів</a></b>",
                parse_mode='html'
            )
            return

        try:
            bot.get_chat(info_about_replying_chat.id)
        except apihelper.ApiTelegramException:
            bot.send_message(
                message.chat.id,
                "Бот не знаходится у каналі\n<b><a href='https://t.me/SupYb/24'>Інструкція налаштування для каналів</a></b>",
                parse_mode='html'
            )
            return

        if uncustomizer_chek(info_about_replying_chat.id, message.from_user.id):
            bot.send_message(
                message.chat.id,
                "Ви не є адмінстартором цього каналу\n<b><a href='https://t.me/SupYb/24'>Інструкція налаштування для каналів</a></b>",
                parse_mode='html'
            )
            return

        audience.reload()
        bot.reply_to(
            message.reply_to_message,
            f'Надсилати повідомлення до каналу \'<b>{info_about_replying_chat.title}</b>\', коли тривога буде в:',
            parse_mode='html',
            reply_markup=markup_generator(info_about_replying_chat.id)
        )
    else:
        audience.reload()
        bot.send_message(message.chat.id, 'Надсилати повідомлення, коли тривога буде в:', reply_markup=markup_generator(message.chat.id))

def callback_form(call):
    if uncustomizer_chek(call.message.chat.id, call.from_user.id):
        time.sleep(1)
        bot.answer_callback_query(callback_query_id=call.id, show_alert=True,
            text="Взаємодіяти з цією формою може тільки автор групи або адмінітратор"
        )
        return

    code, sub_id = eval(call.data)

    if isinstance(code, int):
        state= tuple(audience)[code]
        subscribers= audience[state]

        if call.message.reply_markup.keyboard[code//2][code%2].text[-1] == "✅":
            if sub_id in subscribers:
                subscribers.remove(sub_id)
            bot.answer_callback_query(callback_query_id=call.id, text=state+" ❌")

        else:
            if sub_id not in subscribers:
                subscribers.append(sub_id)
            bot.answer_callback_query(callback_query_id=call.id, text=state+" ✅")

        try:
            bot.edit_message_text(chat_id=call.message.chat.id,
                message_id=call.message.message_id, text="Надсилати повідомлення, коли тривога буде у:",
                reply_markup=markup_generator(sub_id)
            )
        except apihelper.ApiTelegramException:
            time.sleep(0.5)


    elif code=="S": #Save
        audience.save()
        subscriptions_of_user = audience.get_subscriptions(sub_id)

        if subscriptions_of_user:
            str_subscriptions_of_user = "\n".join(
                [
                    f" {k}. {state}"
                    for k, state in enumerate(subscriptions_of_user,start=1)
                ]
            )
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
            text="Повідомлення будуть надходити, коли змінюватиметься ситуація в:\n"+str_subscriptions_of_user,
            reply_markup=None)
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
            text="Повідомлення не будуть надходити",
            reply_markup=None)

    elif code=="A":
        time.sleep(1)
        if audience.get_subscriptions(sub_id):
            audience.del_SubId(sub_id)
        else:
            for state in audience:
                audience[state].append(sub_id)

        audience.save()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Надсилати повідомлення, коли тривога буде у:", reply_markup=markup_generator(sub_id))


    else:
        raise ValueError(f"Unidentified value: {code}")
