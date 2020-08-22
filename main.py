#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telebot
from telebot import types
import config
from string import Template
from db import user_dict

TOKEN = config.token
bot = telebot.TeleBot(token=TOKEN)


class User:
    def __init__(self, city):
        self.city = city
        keys = ['user_name', 'user_id', 'gun', 'price', 'payment', 'trade_link']

        for key in keys:
            self.key = None


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn1 = types.KeyboardButton('Да!')
    btn2 = types.KeyboardButton('Нет :(')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, config.start_text, reply_markup=markup)


@bot.message_handler(content_types=['text'])
def any_text(message):
    if message.text == 'Да!':
        chat_id = message.chat.id
        user = user_dict[chat_id] = User(message.text)
        user.user_id = str(message.chat.id)
        user.user_name = message.from_user.username
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, 'Прекарсно, отпрвь мне название оружия и его скин, который ты хочешь продать',reply_markup=markup)
        bot.register_next_step_handler(message, price)
        print(message.text)
    elif message.text == 'Нет :(':
        bot.send_message(message.chat.id, 'Ну, тогда пока :(')
        print(message.text)


def price(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    user.gun = message.text
    bot.send_message(message.chat.id, 'Хорошо, сколько ты хочешь получить за этот(эти) скин(ы)?')
    bot.register_next_step_handler(message, payment_method)


def payment_method(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    user.price = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn1 = types.KeyboardButton('QIWI')
    btn2 = types.KeyboardButton('SBERBANK')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, 'Мы почти закончили, куды вы хотите получить деньги, после совершения сделки?',
                     reply_markup=markup)
    bot.register_next_step_handler(message, trade_link)


def trade_link(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    user.payment = message.text
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, 'Это последний пункт, отправь мне свою трейд ссылку ;)', reply_markup=markup)
    bot.register_next_step_handler(message, end_step)


def end_step(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    user_name = message.from_user.username
    user.trade_link = message.text
    bot.send_message(message.chat.id, 'На этом все, ваша заявка зарегестрирована и отправленна администратору, '
                                      'ожидайте его ответа!')
    if user_name is None:
        bot.send_message(message.chat.id, 'К сожалению, у вас не указано имя пользователя, по этому администратор не '
                                          'сможет с вами связаться. :(\n'
                                          'Отправьте ему (@SkyZen3) данный номер: ' + str(message.chat.id))
    bot.send_message(config.admin_id, getRegData(user))



def getRegData(user):
    t = Template('@$user_name: id $user_id\n'
                 'Продает: $gun\n'
                 'Хочет получить: $price\n'
                 'Способ оплаты: $pay_met\n'
                 'Трейд-ссылка: $trade_link')
    return t.substitute({
        'user_name': user.user_name,
        'user_id': user.user_id,
        'gun': user.gun,
        'price': user.price,
        'pay_met': user.payment,
        'trade_link': user.trade_link
    })


if __name__ == '__main__':
    bot.polling(none_stop=True)
