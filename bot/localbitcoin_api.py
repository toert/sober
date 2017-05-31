import time
import hmac
import json
import hashlib
import requests
from urllib.parse import urlencode
from datetime import datetime



class LocalBitcoin:

    baseurl = 'https://localbitcoins.net'

    def __init__(self, hmac_auth_key, hmac_auth_secret, proxy=None, debug = False):
        self.hmac_auth_key = hmac_auth_key
        self.hmac_auth_secret = hmac_auth_secret
        self.proxy = proxy
        self.debug = debug

    def get_ads(self, id_list):
        url = '/api/ad-get/'
        comma_separated_str = str(id_list[0])
        for id in id_list[1:]:
            comma_separated_str += ',' + str(id)
        params = {'ads': comma_separated_str}
        # Convert parameters into list of tuples.
        # This makes request encoding to keep the order
        params = params.items()

        while True:

            nonce = int(time.time() * 1000)
            params_urlencoded = requests.models.RequestEncodingMixin._encode_params(params)
            message = str(nonce) + self.hmac_auth_key + url + params_urlencoded
            signature = hmac.new(self.hmac_auth_secret.encode('utf-8'), msg=message.encode('utf-8'), digestmod=hashlib.sha256).hexdigest().upper()

            headers = {
                "Apiauth-Key": self.hmac_auth_key,
                "Apiauth-Nonce": str(nonce),
                "Apiauth-Signature": signature,
            }
            if self.proxy:
                response = requests.get(self.baseurl + url, params=params, headers=headers, proxies=self.proxy)
            else:
                response = requests.get(self.baseurl + url, params=params, headers=headers)


                # If HMAC Nonce is already used, then wait a little and try again
            try:
                response_json = response.json()
                if response_json.get('error', {}).get('error_code') == '42':
                    time.sleep(0.1)
                    continue
            except:
                # No JSONic response, or interrupt, better just give up
                pass
            print(response.text)
            return response.json()


    def sendRequest(self, endpoint, params, method):

        params_encoded = ''
        if params != '':
            params_encoded = urlencode(params)
            if method == 'get':
              params_encoded = '?' + params_encoded

        now = datetime.utcnow()
        epoch = datetime.utcfromtimestamp(0)
        delta = now - epoch
        nonce = int(delta.total_seconds() * 1000)

        message = str(nonce) + self.hmac_auth_key + endpoint + params_encoded
        signature = hmac.new(self.hmac_auth_secret.encode('utf-8'),
                             msg = message.encode('utf-8'),
                             digestmod = hashlib.sha256).hexdigest().upper()

        headers = {}
        headers['Apiauth-key'] = self.hmac_auth_key
        headers['Apiauth-Nonce'] = str(nonce)
        headers['Apiauth-Signature'] = signature
        if method == 'get':
            if self.proxy:
                response = requests.get(self.baseurl + endpoint, headers = headers, params = params, proxies=self.proxy)
            else:
                response = requests.get(self.baseurl + endpoint, headers = headers, params = params)
        else:
            if self.proxy:
                response = requests.post(self.baseurl + endpoint, headers = headers, data = params, proxies=self.proxy)
            else:
                response = requests.post(self.baseurl + endpoint, headers = headers, data = params)


        if self.debug == True:
            print ('REQUEST: ' + self.baseurl + endpoint)
            print ('PARAMS: ' + str(params))
            print ('METHOD: ' + method)
            print ('RESPONSE: ' + response.text)

        return json.loads(response.text)


if __name__ == '__main__':
    proxy = "83.219.142.133:3128"
    proxies = {
        "http": 'http://{}'.format(proxy),
        "https": 'https://{}'.format(proxy),
        "ftp": 'ftp://{}'.format(proxy)
    }

    client = LocalBitcoin('a77ae8d32c1cce099a65388c0791b65d',
                          '8fbcd2c95f340b3d6fc43938b4e8bfc9ecabc57d0cb82ddefcf8f4accb047d03',
                         proxy=proxies)
    params = {
        'price_equation': '100000.3',
        'lat': 58,
        'lon': 61,
        'city': 'Moscow',
        'location_string': 'Moscow',
        'countrycode': 'RU',
        'currency': 'RUB',
        'account_info': 'TEST',
        'bank_name': 'Сбербанк',
        'msg': 'TEST',
        'sms_verification_required': False,
        'track_max_amount': False,
        'require_trusted_by_advertiser': False,
        'require_identification': False
    }
    print(client.get_ads([234523, 223444, 565564, 397416]))