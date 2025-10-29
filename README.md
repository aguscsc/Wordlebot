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
The list was obtained from [here](https://wordraiders.com/wordle-words/) using the [words_scraper.py](/code/words_scraper.py) script and saved in [here](/code/wordle_list.txt)
### Determine information per word (TODO)

# How to use (TODO)
