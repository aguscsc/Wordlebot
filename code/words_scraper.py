from bs4 import BeautifulSoup as bt
import time 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# /--- selenium setup ---/

# starts a fierfox session
driver = webdriver.Firefox()

# wordl
URL = "https://wordraiders.com/wordle-words/"
driver.get(URL)

# the show more button needs to be pressed 4 times so it shows all words on the list
num_clicks = 4

# clicking
for i in range(num_clicks):
    try:
        # find class show-more cta-btn 
        button = driver.find_element(By.CSS_SELECTOR, ".show-more.cta-btn")

        #click it
        button.click()

        #timeout so it loads
        time.sleep(2)
    # if the button is not found
    except NoSuchElementException:
        print("button wasn't found")
    except Exception as e:
        print("error while clicking")

print("all words are loaded")

#get the raw html
page_html = driver.page_source

#close the browser
driver.quit()

# parse the raw html
soup = bt(page_html, 'html.parser')
# filter the html to get only the words class and sub class 
words = soup.find_all('li', class_="single-word common-word")

word_list = []

for element in words:
    # find sub tag
    sub = element.find('sub')
    # erase sub tag 
    if sub:
        sub.decompose()
    # gets the visible content of <li>
    word = element.get_text(strip = True).lower()
    
    # append word to the list
    if len(word):
        word_list.append(word)


if not word_list:
    print("failed to create list")
else:
    file = "word_list.txt"
    with open(file, 'w') as f:
        for word in word_list:
            f.write(f"{word}\n")
