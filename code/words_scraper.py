import requests
from bs4 import BeautifulSoup as bt

# wordl
URL = "https://wordraiders.com/wordle-words/"

try:
    #added user agent to simulate a windows pc
    user = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(URL, headers = user)

    #check errors
    response.raise_for_status()
    #parse the html
    soup = bt(response.text, 'html.parser')

    #find words
    words = soup.find_all('li', class_="single-word common-word")
    #print(words)
    #word list
    word_list = []
    
# Loop through each <li> element we found
    for element in words:
        
        # 1. Find the <sub> tag (the part with the points)
        sub_tag = element.find('sub')
        
        # 2. Check if it exists, and if so, remove it
        if sub_tag:
            sub_tag.decompose() # This destroys the <sub> tag
            
        # 3. Now, get the text. The <sub> text is gone!
        word = element.get_text(strip=True).lower()
        
        # 4. Save the clean word
        if len(word) == 5:
            word_list.append(word)
    if not word_list:
        print("failed to retrieve words")
    else:
        #save words
        file = "wordle_list.txt"
        with open(file, 'w') as f:
            for word in word_list:
                f.write(f"{word}\n")
#exceptions 
except requests.exceptions.HTTPError as err:
    print(f"HTTP error occurred: {err}")
except requests.exceptions.RequestException as e:
    print(f"An error occurred while fetching the page: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
