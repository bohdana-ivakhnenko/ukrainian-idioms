from collections import defaultdict
import requests
from bs4 import BeautifulSoup
import json


def get_links_dict(source_link, tag="vkazivnyk"):
    page = BeautifulSoup(requests.get(source_link).content, features="html.parser")
    parts = page.find("div", {"id": tag}).find_all("a")
    links = {parts[num].text: parts[num]["href"] for num in range(len(parts))}
    return links


dict_link = "http://sum.in.ua"
root_link = "http://sum.in.ua/vkazivnyk"
letters_links = get_links_dict(root_link)
letter_comb_links = {}
words_links = defaultdict(dict)

for letter, link_letter in letters_links.items():
    letter_comb_links[letter] = get_links_dict(dict_link + link_letter)
    for letter_comb, link_comb in letter_comb_links[letter].items():
        if link_comb.startswith("/s"):
            words_links[letter][letter_comb] = link_comb
        else:
            structured_word_links = get_links_dict(dict_link + link_comb)
            words_links[letter].update(structured_word_links)

words_links["dict_link"]["main"] = dict_link
print(words_links)

with open("word_links_sum.json", "w", encoding="utf-8") as file:
    json.dump(words_links, file, ensure_ascii=False, indent=4)

with open("words_sum.json", "r", encoding="utf-8") as file:
    word_articles = json.loads(file.read())

with open("word_links_sum.json", "r", encoding="utf-8") as file:
    words_links = json.loads(file.read())

with open("idioms_articles_sum.json", "r", encoding="utf-8") as file:
    articles_with_idioms = json.loads(file.read())

for letter, words in list(words_links.items()):
    if letter in word_articles.keys():
        continue
    word_articles[letter] = defaultdict(dict)
    articles_with_idioms[letter] = defaultdict(dict)

    print("START", letter)

    try:
        for word, link in list(words.items()):
            print(word)
            response = requests.get(dict_link + link).content
            page = BeautifulSoup(response, features="html.parser")
            article = page.find_all("div", {"itemprop": "articleBody"})

            word_articles[letter][word] = [str(part) for part in article]
            idiom = [str(part) for part in article if "♦" in str(part)]
            if idiom:
                articles_with_idioms[letter][word] = idiom

    except ConnectionResetError:
        print("ERROR:", letter)

    with open("words_sum.json", "w", encoding="utf-8") as file:
        json.dump(word_articles, file, ensure_ascii=False, indent=4)

    with open("idioms_articles_sum.json", "w", encoding="utf-8") as file:
        json.dump(articles_with_idioms, file, ensure_ascii=False, indent=4)
