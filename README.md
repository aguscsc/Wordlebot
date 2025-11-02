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
### Determine information per word 
Each letter can be grey, green or yellow. Having 5 letters this gives us 243 possible combinations, **BUT** it is important to consider that due to the nature of the game there are five pattterns that can't happen.

- YGGGG
- GYGGG
- GGYGG
- GGGYG
- GGGGY

This is because having a green letter means that the letter is located at the correct slot, therefore no other letter can take its place. Taking this in consideration a yellow letter can't exist if there isn't yellow or grey present, because it needs a place to go.

Finally, the number of possible casses is given by:

$3^5-5=238$


For each word in the word list we have to check each case and determine how much information gives. Then, rank the avg information obtained per word so we can pinpoint the best guess at the moment.

First a "pattern" is defined to identify each possible case, where $0=grey$,$1=yellow$ and $2=green$. Then, this can be used to define an entropy function, in which all possible patterns for a certain guess will be grouped to determine how likely is each pattern to occur. Now, having the probability of each pattern for a certain guess, Shannon's entropy can be calculated as:

$\[E[x]=p\cdot -log_2(p)\]$ where $p = (times a pattern appears) / (possible answers)$

Once the entropy for each guess is calculated, it is possible to rank each guess. This process can be iterated until the answer is reached.

There's a special case in this approach, when there are only 2 options left a lot of words will be classified as the highest entropy since there are only two options, meaning that the word only has to provide 1 bit of information to be the best guess. Although this approach works, it "wastes" one guess on going from 2 words to one. To solve this, a new crieria is applied, the bot picks one of the answers and goes for it on a 50/50. This effectively reduced the number of guesses from 4 to 3 in some cases.

This can be checked running the script [logic.py](/code/logic.py). (there are two methods which will be tested further in this README).

### Simulation
For this section, two ways of implementing entropy to the best guess were applied, one were the bot always chose the highest entropy option and one where the bot chose one of the top 4.

Both methods were ran through the 2331 possible answers in which the bot always got to the answer, giving the following results.

![results_all_answers](/pics/top1vstop4.png)

It is notable to mention that given the cirscumstances, the top 4 strategy could perform better than the top 1 strategy, for example, the next picture only simulated 50 random cases.

![results_anecdotally](/pics/top1top450.png)

This is only mentioned anecdotically since neither of the strategies showed clear dominance in lower number of games. 


Additionally, a rank of the best opening words was made using the [ranking.py](/code/ranking.py) script, this ranking can be found in the file [ranked_word_list.txt](/code/ranked_word_list.txt).

Here's the first 20:

| Rank | Word | Entropy (Bits) |
| :--- | :--- | :--- |
| 1. | `raise` | 5.8772 |
| 2. | `slate` | 5.8585 |
| 3. | `irate` | 5.8305 |
| 4. | `crate` | 5.8304 |
| 5. | `trace` | 5.8272 |
| 6. | `arise` | 5.8172 |
| 7. | `stare` | 5.8088 |
| 8. | `snare` | 5.7731 |
| 9. | `arose` | 5.7648 |
| 10. | `least` | 5.7539 |
| 11. | `stale` | 5.7429 |
| 12. | `alert` | 5.7421 |
| 13. | `crane` | 5.7381 |
| 14. | `saner` | 5.7364 |
| 15. | `alter` | 5.7127 |
| 16. | `later` | 5.7081 |
| 17. | `react` | 5.6916 |
| 18. | `leant` | 5.6859 |
| 19. | `trade` | 5.6797 |
| 20. | `learn` | 5.6556 |

---
# How to use (TODO)

## ✅ TODO  
- [ ] gui maybe
- [ ] applications outside wordle
---
