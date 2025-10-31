from math import log2
# --- Loading files ---

with open("word_list.txt", 'r') as f:
    answers = [line.strip().lower() for line in f]

with open("possible_words.txt", 'r') as f:
    guess = [line.strip().lower() for line in f]



# --- get pattern ---
def get_pattern(guess, answer):
    pattern = [0]*5
    answer_list = list(answer)
    for a in range(5): 
        if guess[a]==answer[a]:
            pattern[a]=2
            answer_list[a]='1'
    answer = "".join(answer_list)
    
    for i in range(5):    
        for b in range(5):
            if guess[i]==answer[b]:
                pattern[i]=1
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
    best_guess =entropy()
    numbers = input("pattern please (grey=0, yellow=1, green=2): ")
    pattern = tuple(map(int, numbers))
    answers = update(best_guess, pattern, answers)
    if len(answers)==1:
        break
print(f"the correct word is {answers}")



