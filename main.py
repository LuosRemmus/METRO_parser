from selenium import webdriver
from bs4 import BeautifulSoup
import time
import os
import json


RESULT = []


def get_source_html(url: str, directory: str):
    driver = webdriver.Chrome() # executable_path="chromedriver.exe"

    driver.maximize_window()

    try:
        driver.get(url=url)
        time.sleep(3)
        if "/category/" in url:
            file_name = url.replace("https://online.metro-cc.ru/category/ovoshchi-i-frukty/ovoshchi?page=", "")[0]
        else:
            file_name = url.replace("https://online.metro-cc.ru/products/", "")
        
        with open(f"{directory}/{file_name}.html", "w") as page:
            page.write(driver.page_source)

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def get_items(file_name: str):
    with open(f"source_pages/{file_name}", 'r') as file:
        source = file.read()

    soup = BeautifulSoup(source, 'html.parser')

    for i in soup.find_all('a', class_='product-card-photo__link reset-link'):
        yield f"https://online.metro-cc.ru{i.get('href')}"


def get_info(file_name: str):
    with open(f"item_pages/{file_name}", 'r') as file:
        source = file.read()

    soup = BeautifulSoup(source, 'html.parser')
    
    try:
        title = soup.find('h1').text.strip()
    except AttributeError as ae:
        print("[ERROR] Во время получения названия произошла ошибка",ae)
        title = 'Без названия'
    try:
        prices = soup.find_all('span', class_='product-price__sum')
    
    
        try:
            full_price = float(prices[0].text.strip().replace(" д", ""))
        except AttributeError as ae:
            print("[ERROR] Во время получения полной цены товара произошла ошибка",ae)
            full_price = 0.0
        
        try:
            discount_price = float(prices[1].text.strip().replace(" д", ""))
        except AttributeError as ae:
            print("[ERROR] Во время получения цены товара со скидкой произошла ошибка",ae)
            discount_price = full_price
    
    except IndexError:
        full_price, discount_price = 0.0, 0.0
    
    try:
        brand = soup.find('ul', class_='product-attributes__list style--product-page-short-list').find('li').find('a').text.strip()
    except AttributeError as ae:
        print("[ERROR] Во время получения ... произошла ошибка",ae)
        brand = "Без бренда"
    
    try:
        article_number = soup.find('p', itemprop='productID').text.strip().split()[1]
    except AttributeError as ae:
        print("[ERROR] Во время получения ... произошла ошибка", ae)
        article_number = ''

    result = {
        "title": title, 
        "full_price": full_price, 
        "discount_price": discount_price, 
        "brand": brand, 
        "article_number": article_number,
        "product_link": f"https://online.metro-cc.ru/products/{file_name}"
    }

    RESULT.append(result)
    print(f"Товар по ссылке {result['product_link']} обработан.")
    

def main():
    start = time.time()
    pages = 5
    for i in range(1, pages + 1):
        # get_source_html(url=f"https://online.metro-cc.ru/category/ovoshchi-i-frukty/ovoshchi?page={i}&in_stock=1", "source_pages")
        links = get_items(f"{i}.html")

        for link in links:
            # get_source_html(url=link, directory="item_pages")
            pass
    for i in os.listdir("./item_pages"):
        get_info(i)

    with open("result.json", "a") as file:
        json.dump(RESULT, file)

    print(time.time()-start)


if __name__ == '__main__':
    main()
