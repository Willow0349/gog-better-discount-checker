#!/usr/bin/env python3
import requests
import json
import re
import os

cookie = os.environ.get('COOKIE')

def _get_countrycode(cookie,):
    url = 'https://www.gog.com/csrf-cookie'
    headers = {'Cookie': cookie}
    r = requests.get(url, headers=headers)
    return r.cookies.get('gog_lc')[:2]


def _get_page(cookie, page = 1):
    url = f'https://www.gog.com/account/settings/orders/data?canceled=0&completed=1&in_progress=1&not_redeemed=1&page={page}&pending=1&redeemed=1'
    headers = {'Cookie': cookie}
    r = requests.get(url, headers=headers)
    orders = json.loads(r.text)
    return orders

def _check_page(page):
    for order in page["orders"]:
        if order['paymentMethod'] == 'Free Order':
#            print ("FREE ORDER")
             pass
        elif order['moneybackGuarantee']:
            for product in order['products']:
                if not product['isRefunded']:
                    id = int(product['id'])
                    paid = int(product['price']['amount'].replace('.', ''))
                    currency = product['cashValue']['code']

                    if currency not in purchases_dict:
                        purchases_dict[currency] = {}

                    purchases_dict[currency][id] = paid, product['title']

def make_request(params):
    request_url = f"{base_url}?ids={params['ids']}&currency={params['currency']}&countryCode={params['countryCode']}"
    print(f"Request URL: {request_url}")  # Print the request URL
    response = requests.get(request_url)  # Use the full URL directly
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get response: {response.status_code}")

base_url = 'https://api.gog.com/products/prices'
purchases_dict = {}
countryCode = _get_countrycode(cookie)
pageCount = _get_page(cookie)['totalPages']
for pageNumber in range(1, pageCount + 1):
    page = _get_page(cookie, pageNumber)
    _check_page(page)

# Make requests for each currency
for currency, ids_dict in purchases_dict.items():
    ids = list(ids_dict.keys())
    # Split the IDs into chunks of 99 because of api limits
    for i in range(0, len(ids), 99):
        ids_chunk = ids[i:i + 99]
        ids_str = "%2C".join(map(str, ids_chunk))
        params = {'ids': ids_str, 'currency': currency, 'countryCode': countryCode}
        response = make_request(params)

        for item in response['_embedded']['items']:
            id = item['_embedded']['product']['id']
            currentPrice = int(re.sub(r'\D', '', item['_embedded']['prices'][0]['finalPrice']))
            try:
                if purchases_dict[currency][id][0] <= currentPrice:
                    print ("No Problems: ", id)
                    pass
                else:
                    print ('\nOH! NO! "', purchases_dict[currency][id][1], '" is cheaper\n')
            except:
                print ("Error! Product id: ", id)