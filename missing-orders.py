#!/usr/bin/env python3
import requests
from requests.adapters import HTTPAdapter
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

def _getPages(cookie, session):
    pageNumber = 1
    totalPages = 1
    orders = {"orders": []}
    while pageNumber <= totalPages:
        url = f'https://www.gog.com/account/settings/orders/data?canceled=1&completed=1&in_progress=1&not_redeemed=1&page={pageNumber}&pending=1&redeemed=1'
        headers = {'Cookie': cookie}
        r = session.get(url, headers=headers)
        page = json.loads(r.text)
        pageNumber += 1
        totalPages = page["totalPages"]
        orders["orders"].extend(page.get("orders", []))
    #print(json.dumps(orders))
    return orders

def _getReceipt(orders, cookie, session):
    for item in orders["orders"]:
        if "receiptLink" in item and item["status"] != "refund":
            #print(json.dumps(item))
            #print(item["publicId"])
            #print(item["receiptLink"])
            url = f'https://www.gog.com{item["receiptLink"]}'

            # Folder to save the HTML files
            output_folder = "receipts"
            os.makedirs(output_folder, exist_ok=True)

            page_id = item["publicId"]
            link = f'https://www.gog.com{item["receiptLink"]}'
            output_file = os.path.join(output_folder, f"{page_id}.html")

            if os.path.exists(output_file):
                #print(f"Already exists: {output_file}")
                continue

            try:
                print(f"Saving ordier id: {page_id}")
                headers = {'Cookie': cookie}
                response = session.get(link, headers=headers, timeout=10)
                response.raise_for_status()

                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                #print(f"Saved to: {output_file}")
            except Exception as e:
                print(f"Error fetching {link}: {e}")
        elif item["status"] == "refund":
            #print("Refunded")
            pass

def _missingOrders(orders):
    orderIds = {entry["publicId"] for entry in orders["orders"]}

    savedReceipts = os.listdir("receipts")
    savedIds = {filename[:-5] for filename in savedReceipts if filename.endswith(".html")}

    missingIds = savedIds - orderIds

    if missingIds:
        for id in missingIds:
            print(f"❌ Error: Found receipt '{id}.html' with no matching order ID in JSON")
    else:
        print("✅ All saved order IDs in JSON.")

session = requests.Session()
adapter = HTTPAdapter(pool_connections=10, pool_maxsize=10)
session.mount('https://', adapter)

orders = _getPages(cookie, session)
_getReceipt(orders, cookie, session)

session.close()

_missingOrders(orders)