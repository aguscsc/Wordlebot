from math import log2
from logic import get_pattern
# --- information calc ---
def entropy_calc(answers, guess):
    scores = []
    best_guess = "none"
    current_answers = len(answers)
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
    return scores

def main():
    with open("word_list.txt", 'r') as f:
        answers = [line.strip().lower() for line in f]

    with open("possible_words.txt", 'r') as f:
        guess = [line.strip().lower() for line in f]

    rank = entropy_calc(answers, guess)
    rank.sort(key=lambda pair: pair[1], reverse=True)
    while(1):
         top = input("how many words should I display?: ")
         if top.lower() == "all":
            top = 2309
            break
         try:
             top = int(top)
             break
         except Exception as e:
             print("it has to be an integer")
    if top == 2309:
        output_filename = "ranked_word_list.txt"
    try:
        with open(output_filename, "w") as f:
            for i, (word, score) in enumerate(rank):
                # Format the string, adding a newline character '\n'
                line = f"{i+1}. {word}: {score:.4f} bits\n"
                f.write(line)
        print(f"Successfully saved full ranking to '{output_filename}'")
    except Exception as e:
        print(f"Error saving file: {e}")
    

    for i in range(top):
        word, entropy = rank[i]
        print(f"{i+1}.{word}: {entropy:.4f} bits")

if __name__ == "__main__":
    main()
