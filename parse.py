from bs4 import BeautifulSoup
import json
import sys
import traceback
import unicodedata


def normalize(text):
  return unicodedata.normalize('NFKD', text)


def parse_file(html_file):
  soup = BeautifulSoup(html_file, 'lxml')
  for product in soup.select('.product-item__wrap'):
    try:
      info = {}

      names = product.select('.product__name')
      if len(names) == 1:
        info['name'] = normalize(names[0].text)
      sizes = product.select('.product__size')
      if len(sizes) == 1:
        info['size'] = normalize(sizes[0].text)
      prices = product.select('.product__price .price')
      if len(prices) == 1:
        info['price'] = normalize(prices[0].text)
      cart_codes = product.select('.js-key-product-cart-code')
      if len(cart_codes) == 1:
        info['cart_code'] = normalize(cart_codes[0]['value'])
      product_page_paths = product.select('a.product-card-anchor');
      if len(product_page_paths) == 1:
        info['product_page_path'] = normalize(product_page_paths[0]['href'])

      yield info
    except Exception:
      traceback.print_exc()


if __name__ == '__main__':
  for path in sys.stdin:
    try:
      with open(path.strip()) as html_file:
        for product in parse_file(html_file):
          json.dump(product, sys.stdout)
          sys.stdout.write('\n')
    except Exception:
      traceback.print_exc()
