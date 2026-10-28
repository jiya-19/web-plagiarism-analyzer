# import requests

# url = "https://html.duckduckgo.com/html/?q=%22machine+learning+is+a+method+of+artificial+intelligence%22"

# r = requests.get(
#     url,
#     headers={
#         "User-Agent": "Mozilla/5.0"
#     },
#     timeout=15
# )

# print("STATUS:", r.status_code)
# print("LENGTH:", len(r.text))
# print("RESULT LINKS:", r.text.count("result__a"))
# print(r.url)

# from bs4 import BeautifulSoup

# soup = BeautifulSoup(r.text, "html.parser")

# for x in soup.select("a.result__a")[:5]:
#     print(x.get_text(" ", strip=True))
#     print(x.get("href"))
#     print()

import requests

url = "https://www.bing.com/search?q=%22machine+learning+is+a+method+of+artificial+intelligence%22"

r = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=15
)

print("STATUS:", r.status_code)
print("LENGTH:", len(r.text))
print("BING:", "bing.com" in r.text.lower())

from bs4 import BeautifulSoup

soup = BeautifulSoup(r.text, "html.parser")

links = soup.select("li.b_algo h2 a")

print("RESULTS:", len(links))

for x in links[:5]:
    print(x.get_text(" ", strip=True))
    print(x.get("href"))
    print()