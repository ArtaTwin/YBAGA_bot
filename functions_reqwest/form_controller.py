from telebot   import TeleBot, types, apihelper

import secret
from .handlers.audience_module import Audience
from .handlers.reporter_error import report_error

__all__ = ['form', 'callback_inline']


bot = TeleBot(secret.TOKEN)
audience = Audience(r"data/audience.json")

def markup_generator(sub_id):
    markup = types.InlineKeyboardMarkup()
    audience.reload()
    for i, SubscriptionsOfSubId in enumerate(audience.get_SubscriptionsOfSubId(sub_id)):
        state, subscription_is_available = SubscriptionsOfSubId
        markup.add(
            types.InlineKeyboardButton(
                state+(" ✅" if subscription_is_available else ""),
                callback_data=str(
                    (i, subscription_is_available, sub_id)
                )
            )
        )
    #phoro_subscription = sub_id in audience["send map"]
    #markup.add(types.InlineKeyboardButton("🗺 Надсилати мапу "+ ('✅' if phoro_subscription else ''), callback_data=str(("M", phoro_subscription, sub_id)) ))
    markup.add(types.InlineKeyboardButton("Зберегти налаштування ⚙️", callback_data=str(("C", 0, sub_id)) )) #save and close
    return markup

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

        bot.reply_to(
            message.reply_to_message,
            f'Надсилати повідомлення до каналу \'<b>{info_about_replying_chat.title}</b>\', коли тривога буде в:',
            parse_mode='html',
            reply_markup=markup_generator(info_about_replying_chat.id)
        )
    else:
        bot.send_message(message.chat.id, 'Надсилати повідомлення, коли тривога буде в:', reply_markup=markup_generator(message.chat.id))

def callback_form(call):
    try:
        if uncustomizer_chek(call.message.chat.id, call.from_user.id):
            bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Взаємодіяти з цією формою може тільки автор групи або адмінітратор")
            time.sleep(1)
            return

        global audience
        code, subscription_is_available, sub_id = eval(call.data)

        if isinstance(code, int):
            cmrk = call.message.reply_markup.keyboard[code][0] #OPTIMIZE: link. But I cannot create a link by cmrk.text
            if subscription_is_available:
                cmrk.text = cmrk.text[:-2] # state - ???
                audience.del_SubId(cmrk.text, sub_id)
            else:
                audience.add_SubId(cmrk.text, sub_id)
                cmrk.text += " ✅"

            cmrk.callback_data= str(
                (code, not subscription_is_available, sub_id)
            )

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Надсилати повідомлення, коли тривога буде у:", reply_markup=call.message.reply_markup)
            return

        elif code=="C": #close
            audience.save()
            subscriptions_of_user = audience.find_SubId(sub_id)

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
            return

        else:
            raise ValueError(f"Unidentified value: {code=}")

    except Exception as e:
        report_error(repr(e))
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Відбувся збій.\nПовторіть спробу, будь ласка')
