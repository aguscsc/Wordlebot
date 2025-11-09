from math import log2
import random
import time
# --- get pattern ---
def get_pattern(guess, answer):
    pattern = [0] * 5
    # Make a list to "use up" letters
    answer_letters = list(answer) 

    # First Pass: Find all GREENS (2)
    #    We must do this first.
    for i in range(5):
        if guess[i] == answer[i]:
            pattern[i] = 2
            # "Use up" this letter so it can't be matched again
            answer_letters[i] = None 

    # 3. Second Pass: Find all YELLOWS (1)
    for i in range(5):
        # Skip if this position is already green
        if pattern[i] == 2:
            continue
            
        # Check if the guess letter is ANYWHERE in the
        # remaining (not None) answer letters
        if guess[i] in answer_letters:
            pattern[i] = 1
            # "Use up" this letter so it can't be used for
            # another yellow for this same guess letter
            answer_letters.remove(guess[i])

    # Return as an immutable tuple
    return tuple(pattern)

# --- information calc ---
#entropy finds the best guess
def entropy(answers, guess):
    max_entropy = 0
    best_guess = "none"
    current_answers = len(answers)
    if current_answers == 2:
        for guess_word in guess:
            if get_pattern(guess_word, answers[0]) == (2,2,2,2,2):
                bullseye = guess_word
                print(f"50/50 the word is {bullseye}")
                return bullseye
    for guess_word in guess:

        #here i store how many times i enounter the patterns 0=grey 1=yellow 2=green
        patterns_group = {}

        #run every possible answer from the list
        for answer in answers:

            #get the pattern
            pattern = get_pattern(guess_word,answer)

            #add pattern to the group
            patterns_group[pattern] = patterns_group.get(pattern,0) + 1


        entropy = 0

        for group_size in patterns_group.values():

            #probability of this pattern
            p = group_size / current_answers

            #information = -log2(p)
            #shannons entropy = sum(information * p)
            entropy += p*(-log2(p))

        #print(f"{guess_word} gives {entropy} bits of information")
        if entropy > max_entropy:

            max_entropy = entropy
            best_guess = guess_word

    print(f"the best guess is {best_guess}, giving {max_entropy} bits of information on avg")
    return best_guess

#this function takes the top 4 guesses and chooses one at random
def find_top4(answers, guess):
    scores = []
    best_guess = "none"
    current_answers = len(answers)
    if current_answers == 2:
        for guess_word in guess:
            if get_pattern(guess_word, answers[0]) == (2,2,2,2,2):
                bullseye = guess_word
                print(f"50/50 the word is {bullseye}")
                return bullseye
    for guess_word in guess:
        rank = guess_word
        #here i store how many times i enounter the patterns 0=grey 1=yellow 2=green
        patterns_group = {}

        #run every possible answer from the list
        for answer in answers:

            #get the pattern
            pattern = get_pattern(guess_word,answer)

            #add pattern to the group
            patterns_group[pattern] = patterns_group.get(pattern,0) + 1


        entropy = 0

        for group_size in patterns_group.values():

            #probability of this pattern
            p = group_size / current_answers

            #information = -log2(p)
            #shannons entropy = sum(information * p)
            entropy += p*(-log2(p))
        scores.append((guess_word, entropy))
    scores.sort(key=lambda pair: pair[1], reverse=True)

    best_guess_idx = random.randint(0,3)
    best_guess, info = scores[best_guess_idx]
    for i in range(4):
        print(scores[i])
    print(f"the best guess is {best_guess}, giving {info} bits of information on avg")
    return best_guess
# --- debug pattern ---
def debug_pattern(best_guess, input):
    pattern = get_pattern(best_guess, input)
    print(pattern)

# --- update list ---
def update(best_guess,pattern,answers):
# Keep only the words that, when compared with the best_guess, produce the exact same pattern.
    new_answers = [word for word in answers if get_pattern(best_guess, word) == pattern] 
    return new_answers

# --- calculate actual bits of information per guess ---
def get_bits(answers):
    a = -log2(len(answers)/total_answers)
    return a
# --- Main ---
def main(answers, guess, total_answers):
    best_guess = entropy(answers, guess)
    print(best_guess)
if __name__ == "__main__":
    # --- Loading files ---

    start = time.perf_counter()    
    with open("word_list.txt", 'r') as f:
        answers = [line.strip().lower() for line in f]

    with open("possible_words.txt", 'r') as f:
        guess = [line.strip().lower() for line in f]


    total_answers = len(answers)
    main(answers, guess,total_answers)
    end = time.perf_counter()

    time = end - start
    print(f"it took {time:.4f} second")
