import requests #Used to send http requests 
from bs4 import BeautifulSoup


url = "https://www.amazon.ca"
response = requests.get(url) #make get request to website to get content of the webpage

soup = BeautifulSoup(response.text, 'html.parser')
datas = soup.find_all('span', class_='text')
for data in datas:
    print(datas.text)

# print(soup)