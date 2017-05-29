from bot.localbitcoin_api import LocalBitcoin
from bot.models import LocalUser, Ad


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


def queryset_to_list(queryset):
    return [result[0] for result in list(queryset)]


def run():
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