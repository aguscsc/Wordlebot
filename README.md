# Wordlebot
This repository contains the development of a bot that plays wordle as a personal project.
## Acknowledgements

The core algorithm and information theory approach for this Wordle solver were heavily inspired by 3Blue1Brown's video, "[Solving Wordle using information theory](https://www.youtube.com/watch?v=v68zYyaEmEA)".(Highly recommend watching it, really fun video)

The accompanying repository can be found [here]([https://github.com/3b1b/videos/tree/master/2022/wordle](https://github.com/3b1b/videos/tree/master/_2022/wordle)).
# Roadmap

- 1). get list of words
- 2). determine the possible bits of information you can get from it based on each possible case
- 3). get the flatest distribution possible, meaning that every case is almost equiprobable
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

This is because having a green letter means that the letter is located at the correct slot, therefore no other letter can take its place. Taking this into consideration a yellow letter can't exist if there isn't yellow or grey present, because it needs a place to go.

Finally, the number of possible cases is given by:

$3^5-5=238$


For each word in the word list we have to check each case and determine how much information gives. Then, rank the avg information obtained per word so we can pinpoint the best guess at the moment.

First a "pattern" is defined to identify each possible case, where $0=grey$,$1=yellow$ and $2=green$. Then, this can be used to define an entropy function, in which all possible patterns for a certain guess will be grouped to determine how likely is each pattern to occur. Now, having the probability of each pattern for a certain guess, Shannon's entropy can be calculated as:

$\[E[x]=\sum_{i=1}^{n} p_i\cdot -log_2(p_i)\]$ where $p = (times a pattern appears) / (possible answers)$

Once the entropy for each guess is calculated, it is possible to rank each guess. This process can be iterated until the answer is reached.

There's a special case in this approach, when there are only 2 options left a lot of words will be classified as the highest entropy since there are only two options, meaning that the word only has to provide 1 bit of information to be the best guess. Although this approach works, it "wastes" one guess on going from 2 words to one. To solve this, a new criteria is applied, the bot picks one of the answers and goes for it on a 50/50. This effectively reduced the number of guesses from 4 to 3 in some cases, avg guesses per word went down from $~3.67$ to $~3.56$ with this.

This can be checked running the script [logic.py](/code/logic.py). (there are two methods which will be tested further in this README).

![logic](/pics/logic.png)

### Simulation
For this section, two ways of implementing entropy to the best guess were applied, one were the bot always chose the highest entropy option and one where the bot chose one of the top 4.

Both methods were ran through the 2331 possible answers in which the bot always got to the answer, giving the following results.

![results_all_answers](/pics/top1vstop4.png)

It is notable to mention that given the circumstances, the top 4 strategy could perform better than the top 1 strategy, for example, the next picture only simulated 50 random cases.

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
# How to use
## Clone repository
Clone the repository and cd into the code folder

```
git clone https://github.com/aguscsc/Wordlebot
cd code
```
Here you'll find scripts containing the main logic of this problem and a simulation to test it.

### logic.py
logic.py is made so you can interact with it, choosing your own opening word.
```
python logic.py
```
You'll be prompted to choose an opening and then provide the pattern formed with each guess

```
python logic.py 
enter your first word (you should start with the word raise, it gives ~5.87bits of information): raise
pattern please (grey=0, yellow=1, green=2): 01000
['about', 'local', 'black', 'today', 'total', 'human', 'adult', 'along', 'among', 'album', 'apply', 'woman', 'allow', 'thank', 'plant', 'alpha', 'coach', 'blank', 'plaza', 'adopt', 'vocal', 'float', 'focal', 'alloy', 'awful', 'tonga', 'adapt', 'loyal', 'aloud', 'clamp', 'cocoa', 'quota', 'champ', 'comma', 'gland', 'chalk', 'topaz', 'vodka', 'modal', 'bland', 'agony', 'annoy', 'cloak', 'nomad', 'chant', 'plank', 'polka', 'bylaw', 'llama', 'dogma', 'abbot', 'mocha', 'koala', 'flank', 'atoll', 'whack', 'tonal', 'junta', 'knack', 'aptly', 'tubal', 'octal', 'zonal', 'aloft', 'quack', 'flaky', 'flack', 'allot', 'afoot', 'amply', 'bloat', 'chaff', 'aloof', 'aback', 'clank', 'guava', 'clack', 'twang', 'aunty', 'foamy', 'allay', 'offal', 'guano', 'clang', 'afoul', 'loath', 'annul', 'loamy', 'gloat', 'aglow', 'gonad', 'pupal', 'uvula', 'qualm']
this answer gave you 4.632144437451229 bits of information, 94 words remain

the best guess is clout, giving 4.999748661056134 bits of information on avg
pattern please (grey=0, yellow=1, green=2): 00200
['among', 'agony']
this answer gave you 10.186733289128867 bits of information, 2 words remain

50/50 the word is among
pattern please (grey=0, yellow=1, green=2): 22222
['among']
this answer gave you 11.186733289128867 bits of information, 1 words remain

the correct word is ['among']
```

You can also change the strategy used changing the function used for best_guess

```
best_guess = entropy(answers, guess)
best_guess = find_top4(answers, guess)
```
### simulation.py
by running this script you'll be prompted to choose how many cases would you like to simulate. If you choose any number below 2331, cases will be random. If you choose "all", all 2331 cases will be tested on the two strategies. (**Be careful running this as it is not well optimized**)
```
python simulation.py 
How many runs? (Type 'ALL' for all 2331 answers): 
```
If you want to run the simulation for only one strategy, you just need to comment one of the following lines.

```
score_top1 = run_simulation(runs, master_answers, guess_list, logic.entropy)
score_top4 = run_simulation(runs, master_answers, guess_list, logic.find_top4)
```
## ✅ TODO  
- [ ] gui maybe
- [ ] applications outside wordle
- [ ] code optimization (rust version)
---
