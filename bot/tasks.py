from .localbitcoin_api import LocalBitcoin
from datetime import datetime
from time import mktime, sleep
from .models import LocalUser, Ad
from re import sub
from celery.task import task


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


def queryset_to_list(queryset):
    return [result[0] for result in list(queryset)]


def fetch_ads_from_invisible_logins(invisible_logins, client):
    invisible_logins_string = ",".join(invisible_logins)
    params = {
        'ads': invisible_logins_string
    }
    return client.sendRequest(endpoint='/api/ad-get/',
                              params=params,
                              method='get')


def fetch_ad_from_trade_id(trade_id, client):
    return client.sendRequest(endpoint='/api/ad-get/{}/'.format(trade_id),
                              params='',
                              method='get')['data']['ad_list'][0]


def convert_date_to_timestamp(date):
    if type(date) is str:
        date = sub(r'T', ' ', date)
    else:
        date = str(date)
    return mktime(datetime.strptime(date, '%Y-%m-%d %H:%M:%S+00:00').timetuple())


def fetch_all_ads_json(direction, online_provider, invisible_trade_ids, client):
    all_ads = client.sendRequest(endpoint='/{}-bitcoins-online/RUB/{}/.json'.format(direction, online_provider),
                                 params='',
                                 method='get')
    for id in invisible_trade_ids:
        all_ads['data']['ad_list'].append(fetch_ad_from_trade_id(id, client))
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
    return list(filter(lambda ad: int(ad['data']['max_amount']) > min_amount_filter, all_ads))


def filter_ads_by_delta_amount(all_ads, delta_amount_filter):
    return list(filter(lambda ad: (int(ad['data']['max_amount']) - int(ad['data']['min_amount'])) > delta_amount_filter,
                       all_ads))


def filter_ads_by_login_black_list(all_ads, blacklist):
    return list(filter(lambda ad: ad['data']['profile']['username'] not in blacklist, all_ads))


def get_filtered_ads(all_ads, ad):
    if ad.is_top_fifteen:
        all_ads = all_ads[:15]
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
    ad.save()


def rollback_ad_price(ad, price_rollback):
    ad.price_equation -= price_rollback
    ad.save()


def fetch_dashboard_open_trades(client):
    return client.sendRequest(endpoint='/api/dashboard/',
                              params='',
                              method='get')


def fetch_dashboard_released_trades(client):
    return client.sendRequest(endpoint='/api/dashboard/released',
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


def update_ad_bot(ad_id):
    ad = Ad.objects.get(id=ad_id)
    client = LocalBitcoin(ad.user.hmac_key,
                          ad.user.hmac_secret,
                          debug=False)
    all_ads_json = fetch_all_ads_json(ad.direction, ad.online_provider, ad.get_invisible_trade_ids_as_list(), client)
    sorted_ads = sort_ads_by_price(all_ads_json, ad.direction)
    ad.current_ad_position = get_own_ad_current_position(ad.ad_id, sorted_ads)
    ad.save()
    filtered_ads = get_filtered_ads(sorted_ads, ad)
    update_ad_price(filtered_ads, ad)
    edit_ad(ad, client)


def run_all_dashboards_processing():
    while True:
        all_user_ids_list = queryset_to_list(LocalUser.objects.values_id('id'))
        for user_id in all_user_ids_list:
            update_task_dashboard(user_id)


def update_task_dashboard(user_id):
    user = LocalUser.objects.get(id=user_id)
    client = LocalBitcoin(user.hmac_key,
                          user.hmac_secret,
                          debug=False)

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


def run_all_ads_bots_asynchronous():
    all_ad_ids_list = queryset_to_list(Ad.objects.values_list('id'))
    update_task_ad.apply_async(all_ad_ids_list)


@task
def update_task_ad(ad_id):
    ad = Ad.objects.filter(id=ad_id)
    while True:
        while ad.is_updated:
            ad.current_step = 1
            while ad.current_step < ad.steps_quantity:
                update_ad_bot(ad.ad_id)
                ad.current_step += 1
                ad.save()
            rollback_ad_price(ad, ad.price_rollback)
            sleep(ad.rollback_time)
        sleep(60)


if __name__ == '__main__':
    pass
