#!/usr/bin/env python3
from bs4 import BeautifulSoup
import requests
import json
import re

cookie = ''

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
    done = False
    for order in page["orders"]:
        if order['paymentMethod'] == 'Free Order':
#            print ("FREE ORDER")
             pass
        elif order['moneybackGuarantee']:
            for product in order['products']:
                id = product['id']
                paid = int(product['price']['amount'].replace('.', ''))
                currency = product['cashValue']['code']
                r = requests.get(f'https://api.gog.com/products/{id}/prices?countryCode={countryCode}&currency={currency}')
                try:
                    currentPrice = int(re.sub(r'\D', '', json.loads(r.text)['_embedded']['prices'][0]['finalPrice']))
                    if paid <= currentPrice:
#                        print ("No Problems: ", product['title'])
                         pass
                    elif not product['isRefunded']:
                        print ('\nOH! NO! "', product['title'], '" is cheaper\n')
                except:
                    print ("Error! Product id: ", id)
        else:
            done = True
            return done

    return done

countryCode = _get_countrycode(cookie)
pageCount = _get_page(cookie)['totalPages']
for pageNumber in range(1, pageCount + 1):
    page = _get_page(cookie, pageNumber)
    if _check_page(page):
        break
