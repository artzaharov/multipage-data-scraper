import requests
import csv
from bs4 import BeautifulSoup
from time import sleep
import random


def get_links(url, page):
	headers = {
		'authority': 'sert-reestr.net',
		'accept': 'application/json, text/plain, */*',
		'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
		'content-type': 'application/json;charset=UTF-8',
		'origin': 'https://sert-reestr.net',
		'referer': 'https://sert-reestr.net/registry',
		'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
		'sec-ch-ua-mobile': '?0',
		'sec-ch-ua-platform': '"Windows"',
		'sec-fetch-dest': 'empty',
		'sec-fetch-mode': 'cors',
		'sec-fetch-site': 'same-origin',
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
	}

	json_data = {
		'params': {
			'queryParams': {
				'sort': [
					{
						'name': 'requestNum',
						'order': 'desc',
						'caseSensitive': True,
					},
				],
				'filters': [],
				'global_search': '',
				'per_page': 100,
				'page': page,
			},
			'page': page,
		},
	}

	response = requests.post(url, headers=headers, json=json_data).json()

	links = []
	for i in range(0, 100):
		links.append(response['GetRequestList'][i]['reqApplicantName']['url'])

	return links


def deCFEmail(fp):
	try:
		r = int(fp[:2], 16)
		email = ''.join([chr(int(fp[i:i + 2], 16) ^ r) for i in range(2, len(fp), 2)])
		return email
	except (ValueError):
		pass


def get_html(url):
	response = requests.get(url)
	return response.text


def get_data(html):
	data = []
	soup = BeautifulSoup(html, 'lxml')
	try:
		title = soup.find('h1', class_='text-center').text.strip().replace(';', ',')
	except Exception:
		title = ''
	data.append(title)

	try:
		em = soup.find('a', class_="__cf_email__").get('data-cfemail')
		email = deCFEmail(em)
	except Exception:
		email = ''
	data.append(email)

	try:
		dds = soup.find_all('dd', class_='ml-4')
		for dd in dds:
			data.append(dd.text.strip().replace(';', ','))
	except Exception:
		pass

	return data


def write_csv(data):
	with open('data.csv', 'a', encoding='utf-8', newline='') as f:
		writer = csv.writer(f, delimiter=';')
		writer.writerow(data)


def main():
	rec = 1
	url = 'https://sert-reestr.net/registry/main/fetch'
	for page in range(1, 160):
		links = get_links(url, page)
		for link in links:
			data = get_data(get_html(link))
			data.append(link)
			write_csv(data)
			print(rec, 'records parsed')
			rec += 1
		if rec % 100 == 0:
			print('--- pause ---')
			sleep(random.randrange(2, 4))


if __name__ == '__main__':
	main()
