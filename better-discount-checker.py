#!/usr/bin/env python3
import requests
import json
import re
import os
import sys

if not os.environ.get('COOKIE') ==  "":
    cookie = os.environ.get('COOKIE')
else:
    print("Please set the COOKIE environment mariable to your gog-al token")
    sys.exit(1)

if cookie.startswith("gog-al=") and len(cookie) == 157:
    pass
elif not "=" in cookie and len(cookie) == 150:
    cookie = "gog-al=" + cookie
else:
    print("Problem parsing gog-al variable ): ", cookie)
    sys.exit(2)

def _getCountryCode(cookie,):
    url = 'https://www.gog.com/csrf-cookie'
    headers = {'Cookie': cookie}
    r = requests.get(url, headers=headers)
    return r.cookies.get('gog_lc')[:2]


def _getPage(cookie, page):
    url = f'https://www.gog.com/account/settings/orders/data?canceled=0&completed=1&in_progress=1&not_redeemed=1&page={page}&pending=1&redeemed=1'
    headers = {'Cookie': cookie}
    r = requests.get(url, headers=headers)
    orders = json.loads(r.text)
    return orders

def _checkPage(page):
    for order in page["orders"]:
        if order['paymentMethod'] != 'Free Order' and order['moneybackGuarantee']:
            for product in order['products']:
                if not product['isRefunded']:
                    id = int(product['id'])
                    paid = int(product['price']['amount'].replace('.', ''))
                    currency = product['cashValue']['code']

                    if currency not in purchasesDict:
                        purchasesDict[currency] = {}

                    purchasesDict[currency][id] = paid, product['title']
        elif order['paymentMethod'] != 'Free Order':
            return True

def _makeRequest(params):
    requestUrl = f"{baseUrl}?ids={params['ids']}&currency={params['currency']}&countryCode={params['countryCode']}"
    response = requests.get(requestUrl)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get response: {response.status_code}")

baseUrl = 'https://api.gog.com/products/prices'
purchasesDict = {}
countryCode = _getCountryCode(cookie)
firstPage = _getPage(cookie, 1)
pageCount = firstPage['totalPages']

if not _checkPage(firstPage):
    for pageNumber in range(2, pageCount + 1):
        page = _getPage(cookie, pageNumber)
        if _checkPage(page):
            break

# Make requests for each currency
for currency, idsDict in purchasesDict.items():
    ids = list(idsDict.keys())
    # Split the IDs into chunks of 99 because of api limits
    for i in range(0, len(ids), 99):
        idsChunk = ids[i:i + 99]
        idsStr = "%2C".join(map(str, idsChunk))
        params = {'ids': idsStr, 'currency': currency, 'countryCode': countryCode}
        response = _makeRequest(params)

        for item in response['_embedded']['items']:
            id = item['_embedded']['product']['id']
            currentPrice = int(re.sub(r'\D', '', item['_embedded']['prices'][0]['finalPrice']))
            try:
                if purchasesDict[currency][id][0] > currentPrice:
                    print ('\nGOOD NEWS!', purchasesDict[currency][id][1], 'is cheaper :)\n')
            except:
                print ("Error! Product id: ", id)