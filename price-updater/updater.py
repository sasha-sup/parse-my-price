import gspread
import time
from datetime import datetime
import os
import requests
import config
import sys
from logger import logger
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor


def get_price(url, url_class):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            for clas in url_class:
                price_element = soup.find("span", class_=clas)
                if price_element:
                    coin = url.split("/")[-1].capitalize()
                    price = price_element.text.strip().replace("$", "")
                    return coin, price
    except Exception as e:
        logger.error(
            f"Error in get_price for {coin}: {e}",
            extra={"tags": {"Cripto-Price-Updater": "fetch-price"}},
        )
    return None, None


def boost_my_price(urls, url_class):
    results = {}
    with ThreadPoolExecutor(
        max_workers=10
    ) as executor:  # 10 workers you will get a result for 0.74 sec!
        futures = [executor.submit(get_price, url, url_class) for url in urls]
        for future in futures:
            coin, price = future.result()
            if coin and price:
                results[coin] = price
    return results


def write_prices_to_file(prices):
    dir_name = "./artifacts"
    file_name = "crypto_prices.txt"
    os.makedirs(dir_name, exist_ok=True)
    file_path = os.path.join(dir_name, file_name)
    dt_string = datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S %Z")
    with open(file_path, "w") as file:
        file.write(f"{dt_string}\n")
        for coin, price in sorted(prices.items()):
            file.write(f"{coin} : {price}\n")
    logger.info(
        f"Successfully wrote data to {file_path}",
        extra={"tags": {"Cripto-Price-Updater": "file-writer"}},
    )


def write_prices_to_sheet(data, sheet_name, worksheet_name):
    try:
        # https://docs.gspread.org/en/latest/oauth2.html
        os.makedirs("./sa", exist_ok=True)
        gc = gspread.service_account(filename="./sa/service_account.json")
        sh = gc.open(sheet_name)
        ws = sh.worksheet(worksheet_name)
        dt_string = datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S %Z")
        ws.update_cell(1, 1, dt_string)
        cell_range = f"A2:B{len(data) + 1}"
        values = [[coin, price] for coin, price in data.items()]
        ws.update(range_name=cell_range, values=values, value_input_option="RAW")
        logger.info(
            f"Successfully wrote data to {sheet_name} --> {worksheet_name}",
            extra={"tags": {"Cripto-Price-Updater": "sheet-writer"}},
        )
    except Exception as e:
        logger.error(
            f"Error occurred while writing data to {sheet_name} --> {worksheet_name}: {e}",
            extra={"tags": {"Cripto-Price-Updater": "sheet-writer"}},
        )


def main():
    prices = boost_my_price(config.URLS, config.URL_CLASS)
    write_prices_to_file(prices)
    write_prices_to_sheet(prices, "Finance-list", "CryptoPrices")
    sys.exit()


if __name__ == "__main__":
    main()
