from localbitcoin_api import LocalBitcoin
from datetime import datetime
import time
from .models import LocalUser, Ad, CurrentInfo
import json


start_time = time.time()


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
        'details-phone_number': ad.phone_number, # Специальное поле при Payment method: QIWI (QIWI)
        'visible': ad.is_visible
    }
    client.sendRequest(endpoint='/api/ad/{}/'.format(ad.ad_id),
                       params=params,
                       method='post')


"""
def fetch_ads_from_invisible_logins(invisible_logins, client):
    invisible_logins_string = ",".join(invisible_logins)
    params = {
        'ads': invisible_logins_string
    }
    print(invisible_logins_string)
    return client.sendRequest(endpoint='/api/ad-get/',
                              params=params,
                              method='get')
"""


def fetch_ad_from_trade_id(trade_id, client):
    return client.sendRequest(endpoint='/api/ad-get/{}/'.format(trade_id),
                       params='',
                       method='post')


def convert_date_to_timestamp(date):
    return time.mktime(datetime.strptime(date, '%Y-%m-%dT%H:%M:%S+00:00').timetuple())


def fetch_all_ads_json(direction, online_provider, invisible_trade_ids, client):
    all_ads = client.sendRequest(endpoint='/{}-bitcoins-online/RUB/{}/.json'.format(direction, online_provider),
                                 params='',
                                 method='get')
    for id in invisible_trade_ids:
        all_ads['data']['ad_list'].append(fetch_ad_from_trade_id(id, client))
    return all_ads


def sort_ads_by_price(all_ads, direction):
    if direction == 'sell':
        return sorted(all_ads, key=lambda ad: ad['data']['ad_list']['data']['temp_price'], reverse=True)
    elif direction == 'buy':
        return sorted(all_ads, key=lambda ad: ad['data']['ad_list']['data']['temp_price'])


def get_own_ad_current_position(own_ad_id, all_ads):
    ad_position = [position for position,ad_id in enumerate(all_ads) if ad_id == own_ad_id]
    if ad_position:
        return ad_position[0] + 1
    else:
        return 0


def filter_ads_by_time(all_ads, ad_creation_time_filter):
    return list(filter(lambda ad: convert_date_to_timestamp(ad['data']['created_at']) < float(ad_creation_time_filter), all_ads['data']['ad_list']))


def filter_ads_by_amount(all_ads, min_amount_filter):
    return list(filter(lambda ad: int(ad['data']['max_amount']) > min_amount_filter , all_ads))


def filter_ads_by_delta_amount(all_ads, delta_amount_filter):
    return list(filter(lambda ad: (int(ad['data']['max_amount']) - int(ad['data']['min_amount'])) > delta_amount_filter, all_ads))


def filter_ads_by_login_black_list(all_ads, blacklist):
    return list(filter(lambda ad: ad['data']['profile']['username'] not in blacklist, all_ads))


def get_filtered_ads(all_ads, ad):
    if ad['is_top_fifteen']:
        all_ads['data']['ad_list'] = all_ads['data']['ad_list'][:15]
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

#@task
def update_task(ad_id):
    ad = Ad.objects.filter(id=ad_id)
    client = LocalBitcoin(ad.user.hmac_key,
                          ad.user.hmac_secret,
                          debug=False)
    all_ads_json = fetch_all_ads_json(ad.direction, ad.online_provider, ad.get_invisible_trade_ids_as_list(), client)
    sorted_ads = sort_ads_by_price(all_ads_json, ad.direction)
    ad_meta = CurrentInfo.objects.filter(ad=ad)
    ad_meta.current_ad_position = get_own_ad_current_position(ad.ad_id, sorted_ads)
    ad_meta.save()
    filtered_ads = get_filtered_ads(sorted_ads, ad)
    update_ad_price(filtered_ads, ad)
    edit_ad(ad, client)


if __name__ == '__main__':
    update_task(1)
    print("--- %s seconds ---" % (time.time() - start_time))
    #print(json.dumps(all_ads_json, ensure_ascii=False, sort_keys=True, indent=1))
    #for ad in filtered_ads:
    #    print(json.dumps(ad, ensure_ascii=False, sort_keys=True, indent=1))