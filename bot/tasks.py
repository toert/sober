from .localbitcoin_api import LocalBitcoin
from datetime import datetime
from time import mktime, sleep, time
from .models import Ad, LocalUser
from re import sub
from celery.task import task
from os import getenv
import requests


def edit_ad(ad, client):
    params = {
        'price_equation': ad.price_equation,
        'lat': 58,
        'lon': 61,
        'city': 'Moscow',
        'location_string': 'Moscow',
        'countrycode': 'RU',
        'currency': ad.currency,
        'account_info': ad.account_info,
        'bank_name': ad.currency,
        'msg': ad.msg,
        'sms_verification_required': False,
        'track_max_amount': False,
        'require_trusted_by_advertiser': False,
        'require_identification': False,
        'online_provider': ad.online_provider,
        'max_amount': ad.current_amount,
        'details-phone_number': ad.phone_number,  # Специальное поле при Payment method: QIWI (QIWI)
        'visible': ad.is_visible
    }
    client.sendRequest(endpoint='/api/ad/{}/'.format(ad.ad_id),
                       params=params,
                       method='post')


def fetch_ads_from_trade_id(invisible_logins, client):
    return client.get_ads(invisible_logins)


def convert_date_to_timestamp(date):
    if type(date) is str:
        date = sub(r'T', ' ', date)
    else:
        date = str(date)
    return mktime(datetime.strptime(date, '%Y-%m-%d %H:%M:%S+00:00').timetuple())


def fetch_all_ads_json(direction, online_provider, invisible_trade_ids, client):
    import random
    sleep(random.randint(0,10) / 10)
    all_ads = requests.get('https://localbitcoins.net/{}-bitcoins-online/RUB/{}/.json'.format(direction, online_provider))
    print(all_ads.text[:50])
    all_ads = all_ads.json()

    if not invisible_trade_ids == []:
        print(all_ads)
        all_ads['data']['ad_list'].append(fetch_ads_from_trade_id(invisible_trade_ids, client))
    return all_ads


def sort_ads_by_price(all_ads, direction):
    if direction == 'sell':
        return sorted(all_ads['data']['ad_list'], key=lambda ad: float(ad['data']['temp_price']), reverse=True)
    elif direction == 'buy':
        return sorted(all_ads['data']['ad_list'], key=lambda ad: float(ad['data']['temp_price']))


def get_own_ad_current_position(own_ad_id, all_ads):
    ad_position = [position for position, ad_id in enumerate(all_ads) if ad_id == own_ad_id]
    if ad_position:
        return ad_position[0] + 1
    else:
        return -1


def filter_ads_by_time(all_ads, ad_creation_time_filter):
    return list(filter(lambda ad: convert_date_to_timestamp(ad['data']['created_at']) < convert_date_to_timestamp(
        ad_creation_time_filter), all_ads))


def filter_ads_by_amount(all_ads, min_amount_filter):
    return list(filter(lambda ad: int(ad['data']['max_amount_available']) > min_amount_filter, all_ads))


def filter_ads_by_delta_amount(all_ads, delta_amount_filter):
    return list(filter(lambda ad: (int(ad['data']['max_amount_available']) - int(ad['data']['min_amount'])) > delta_amount_filter,
                       all_ads))


def filter_ads_by_login_black_list(all_ads, blacklist):
    return list(filter(lambda ad: ad['data']['profile']['username'] not in blacklist, all_ads))


def get_filtered_ads(all_ads, ad):
    filtered_ads = filter_ads_by_time(all_ads, ad.ad_creation_time_filter)
    filtered_ads = filter_ads_by_login_black_list(filtered_ads, ad.ignored_logins)
    filtered_ads = filter_ads_by_amount(filtered_ads, ad.min_amount_filter)
    filtered_ads = filter_ads_by_delta_amount(filtered_ads, ad.delta_amount_filter)
    return filtered_ads


def calculate_best_price_for_sell(all_ads):
    maximum_price = max(all_ads, key=lambda ad: float(ad['data']['temp_price']))
    return maximum_price['data']['temp_price']


def calculate_best_price_for_buy(all_ads):
    minimum_price = min(all_ads, key=lambda ad: float(ad['data']['temp_price']))
    return minimum_price['data']['temp_price']


def update_ad_price(filtered_ads, ad):
    if ad.direction == 'buy':
        new_price = float(calculate_best_price_for_buy(filtered_ads)) - ad.step
        if ad.price_limit == ad.min_price:
            if new_price > ad.min_price:
                ad.price_equation = new_price
            else:
                ad.price_equation = ad.min_price
        else:
            if new_price <= ad.price_limit:
                ad.current_amount = ad.amount_limit
                if new_price > ad.min_price:
                    ad.price_equation = new_price
                else:
                    ad.price_equation = ad.min_price
            else:
                ad.current_amount = ad.max_amount
                ad.price_equation = new_price
    elif ad.direction == 'sell':
        new_price = float(calculate_best_price_for_sell(filtered_ads)) + ad.step
        if ad.price_limit == ad.max_price:
            if new_price < ad.max_price:
                ad.price_equation = new_price
            else:
                ad.price_equation = ad.max_price
        else:
            if new_price >= ad.price_limit:
                ad.current_amount = ad.amount_limit
                if new_price < ad.max_price:
                    ad.price_equation = new_price
                else:
                    ad.price_equation = ad.max_price
            else:
                ad.current_amount = ad.max_amount
                ad.price_equation = new_price


def rollback_ad_price(ad, price_rollback):
    ad.price_equation -= float(price_rollback)
    ad.save()


def fetch_dashboard_open_trades(client):
    return client.sendRequest(endpoint='/api/dashboard/',
                              params='',
                              method='get')


def fetch_dashboard_released_trades(client):
    return client.sendRequest(endpoint='/api/dashboard/released/',
                              params='',
                              method='get')


def fetch_msg_history(client, trade_contact_id):
    return client.sendRequest(endpoint='/api/contact_messages/{}/'.format(trade_contact_id),
                              params='',
                              method='get')


def check_trade_condition(trade_msg_history, start_msg, finish_msg):
    for msg in trade_msg_history['message_list']:
        if msg['msg'] == finish_msg:
            return 'already_finished'
        elif msg['msg'] == start_msg:
            return 'already_started'


def send_msg(client, trade_contact_id, msg):
    params = {
        'msg': msg
    }
    return client.sendRequest(endpoint='/api/contact_message_post/{}/'.format(trade_contact_id),
                              params=params,
                              method='post')


def queryset_to_list(queryset):
    return [object for object in queryset]


def update_dashboard(user):
    client = LocalBitcoin(user.hmac_key,
                          user.hmac_secret,
                          user.proxy)
    open_trades = fetch_dashboard_open_trades(client)
    for trade in open_trades['data']['contact_list']:
        trade_msg_history = fetch_msg_history(client, trade['data']['contact_id'])
        trade_last_three_symbols = str(trade['data']['contact_id'])[:-3]
        ad = Ad.objects.get(id=trade['data']['advertisement']['id'])
        if check_trade_condition(trade_msg_history, ad.start_msg, ad.finish_msg) != 'already_started':
            msg = '{}\nКомментарий: {}'.format(ad.start_msg, trade_last_three_symbols)
            send_msg(client, trade['data']['contact_id'], msg)
    released_trades = fetch_dashboard_released_trades(client)
    for trade in released_trades['data']['contact_list']:
        trade_msg_history = fetch_msg_history(client, trade['data']['contact_id'])
        ad = Ad.objects.get(id=trade['data']['advertisement']['id'])
        if check_trade_condition(trade_msg_history, ad.start_msg, ad.finish_msg) != 'already_finished':
            send_msg(client, trade['data']['contact_id'], ad.finish_msg)


def update_ad_bot(ad, client):
    start_time = time.time()
    all_ads_json = fetch_all_ads_json(ad.direction, ad.online_provider, ad.get_invisible_trade_ids_as_list(), client)
    print("Получил стакан {} за {} секунд".format(ad.ad_id, time.time() - start_time))
    if ad.is_top_fifteen:
        all_ads_json['data']['ad_list'] = all_ads_json['data']['ad_list'][:15]
    ad.current_ad_position = get_own_ad_current_position(ad.ad_id, all_ads_json)
    sorted_ads = sort_ads_by_price(all_ads_json, ad.direction)
    filtered_ads = get_filtered_ads(sorted_ads, ad)
    update_ad_price(filtered_ads, ad)
    start_time = time.time()
    edit_ad(ad, client)
    print("Изменил {} за {} секунд".format(ad.ad_id, time.time() - start_time))
    return ad


@task
def update_list_of_all_ads():
    print('Список всех объявлений: {}'.format(queryset_to_list(Ad.objects.all())))
    for ad in Ad.objects.all():
        print('{}, я вызываю тебя!'.format(ad.ad_id))
        update_ad.delay(ad)


@task
def update_ad(ad):
    print('Начал работать с {}'.format(ad.ad_id))
    client = LocalBitcoin(ad.user.localuser.hmac_key,
                          ad.user.localuser.hmac_secret,
                          ad.user.localuser.proxy)
    delay = float(getenv('delay'))*60
    start_time = time()
    while time() - start_time < delay:
        if ad.is_updated:
            ad.current_step = 1
            while ad.current_step < ad.steps_quantity and time() - start_time < delay:
                start_time = time.time()
                old_price = ad.price_equation
                ad = update_ad_bot(ad, client)
                if not float(ad.price_equation) == float(old_price):
                    ad.current_step += 1
                ad.save()
                print("Закончил обновлять {} за {} секунд" .format(ad.ad_id, time.time() - start_time))
            print('{} пошел спать'.format(ad.ad_id))
            rollback_ad_price(ad, ad.price_rollback)
            edit_ad(ad, client)
            sleep(ad.rollback_time)
        elif time() - start_time < delay:
            sleep(60)


@task
def update_dashboard_task():
    print('Пошел проверять дашборды')
    for user in queryset_to_list(LocalUser.objects.all()):
        update_dashboard(user)
        print('----- Проверил дашборд пользователя {} -----'.format(user.login))
