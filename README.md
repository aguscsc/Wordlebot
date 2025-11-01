# Wordlebot
This repository contains the development of a bot that plays wordle as a personal project.
## Acknowledgements

The core algorithm and information theory approach for this Wordle solver were heavily inspired by 3Blue1Brown's video, "[Solving Wordle using information theory](https://www.youtube.com/watch?v=v68zYyaEmEA)".(Hugely advice watching it, really fun video)

The accompanying repository can be found [here]([https://github.com/3b1b/videos/tree/master/2022/wordle](https://github.com/3b1b/videos/tree/master/_2022/wordle)).
# Roadmap

- 1). get list of words
- 2). determine the possible bits of information you can get from it based on each possible case
- 3). get the flatest distribution possible, meaning that every case is almos equiprobable
- 4). update after current guess

## steps
### Get list
The list was obtained from [here](https://wordraiders.com/wordle-words/) using the [words_scraper.py](/code/words_scraper.py) script and saved in [here](/code/word_list.txt)
### Determine information per word (TODO)
Each letter can be grey, green or yellow. Having 5 letters this gives us 243 possible combinations, **BUT** it is important to consider that due to the nature of the game there are five pattterns that can't happen.

- YGGGG
- GYGGG
- GGYGG
- GGGYG
- GGGGY

This is because having a green letter means that the letter is located at the correct slot, therefore no other letter can take its place. Taking this in consideration a yellow letter can't exist if there isn't yellow or grey present, because it needs a place to go.

Finally, the number of possible casses is given by:

$3^5-5=238$


For each word in the word list we have to check each case and determine how much information gives. Then, rank the avg information obtained per word so we can pinpoint the best guess at the moment
# How to use (TODO)

## ✅ TODO   
- [ ] Simulation
- [ ] Refine and rank entropy list
- [ ] gui maybe
- [ ] applications outside wordle
---
