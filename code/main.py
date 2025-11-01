from math import log2
# --- Loading files ---

with open("word_list.txt", 'r') as f:
    answers = [line.strip().lower() for line in f]

with open("possible_words.txt", 'r') as f:
    guess = [line.strip().lower() for line in f]



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
def entropy():
    max_entropy = 0
    best_guess = "none"
    total_answers = len(answers)
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
            p = group_size / total_answers

            #information = -log2(p)
            #shannons entropy = sum(information * p)
            entropy += p*(-log2(p))

        #print(f"{guess_word} gives {entropy} bits of information")
        if entropy > max_entropy:

            max_entropy = entropy
            best_guess = guess_word

    print(f"the best guess is {best_guess}, giving {max_entropy} bits of information on avg")
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
# --- Main ---
while(1):
    best_guess = entropy()
    numbers = input("pattern please (grey=0, yellow=1, green=2): ")
    pattern = tuple(map(int, numbers))
    answers = update(best_guess, pattern, answers)
    if len(answers)<=1:
        break
    #best_guess = entropy()
print(f"the correct word is {answers}")



