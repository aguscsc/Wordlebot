import logic
import random 

def main():


    with open("possible_words.txt", 'r') as f:
        guess = [line.strip().lower() for line in f]
    while(1):
        runs = input("how many runs should the bot do? (type ALL for all possilbe answers): ")
        if runs.lower() == ("ALL").lower():
            runs = 2330
            break 
        try:
            runs = int(runs)
            break
        except Exception as e:
            print("not an int")
    scores = []
    for i in range(runs):
        with open("word_list.txt", 'r') as f:
            list = [line.strip().lower() for line in f]
        best_guess = "raise"
        #choose the answer
        if runs == 2330:
            answer = list[i]
        else:
            answer_idx = random.randint(0,len(list))
            answer = list[answer_idx]

        print("the first guess is raise")
        print(f"the word to guess is {answer}\n")
        j = 1
        while(1):
            pattern = logic.get_pattern(best_guess, answer)
            list = logic.update(best_guess,pattern,list)
            print(list)
            if len(list) == 1: 
                j +=1
                scores.append(j)
                print(f"won, the word is {list}, it took {j} guesses\n")
                break     
            best_guess = logic.entropy(list, guess)
            j += 1

    avg_score = sum(scores)/len(scores)

    print(f"the avg number of guesses is {avg_score}")

if __name__ == "__main__":
    main()
