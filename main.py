import csv
import requests
import collections
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('wb')
ParseResult = collections.namedtuple(
	'ParseResult',
	(
		'brand_name',
		'goods_name',
		'url'
	),
)

HEADERS = (
	'Бренд',
	'Товар',
	'Ссылка'
)

class Client:

	def __init__(self):
		self.session = requests.Session()
		self.session.header = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
			'Accept-language':'ru'
		}
		self.result = []

	def load_page(self,page: int = None):
		url = 'https://www.wildberries.ru/catalog/obuv/zhenskaya/tapochki'
		res = self.session.get(url)
		res.raise_for_status()
		return res.text

	def parse_page(self, text: str):
		soup = BeautifulSoup(text, 'lxml')
		container = soup.select('div.dtList.i-dtList.j-card-item')
		for block in container:
			self.parse_block(block=block)

	def parse_block(self, block):


		url_block = block.select_one('a.ref_goods_n_p.j-open-full-product-card')
		if not url_block:
			logger.error('no url_block')
			return
		url = url_block.get('href')
		if not url:
			logger.error('no href')

		name_block = block.select_one('div.dtlist-inner-brand-name')
		brand_name = name_block.select_one('strong.brand-name')
		goods_name = name_block.select_one('span.goods-name')
		brand_name = brand_name.text.replace('/','').strip()
		goods_name = goods_name.text.strip()

		self.result.append(ParseResult(
			url=url,
			brand_name = brand_name,
			goods_name = goods_name
		))

		logger.debug('%s, %s, %s', url, brand_name, goods_name)
		logger.debug('='*100)

	def save_result(self):
		path = 'wildberries.csv'
		with open(path, 'w') as f:
			writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
			writer.writerow(HEADERS)
			for item in self.result:
				writer.writerow(item)

	def run(self):
		text = self.load_page()
		self.parse_page(text=text)
		logger.info(f"получили {len(self.result)} элементов")
		self.save_result()

if __name__ == '__main__':
	parser = Client()
	parser.run()
