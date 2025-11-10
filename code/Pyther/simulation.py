import logic
import random
import time

def run_simulation(runs, master_answers, guess_list, strategy_func):
    """
    Runs a Wordle simulation for a given number of 'runs' using a
    specific 'strategy_func' (like logic.entropy or logic.find_top4).
    """
    scores = []
    
    for i in range(runs):
        # MAKE A COPY of the answer list for this run so it doesnt shrink for next run.
        current_answers = list(master_answers)
        
        # choose answer
        if runs == len(master_answers):
            # If running "ALL", just pick the word at index i
            answer = master_answers[i]
        else:
            # random 
            answer = random.choice(master_answers)
            
        print(f"\n--- Run {i+1}/{runs}: Guessing '{answer}' ---")
        
        # Start with the best-known first guess
        best_guess = "raise"
        
        # Start guess count at 1
        j = 1
        
        while(j <= 6): 
            pattern = logic.get_pattern(best_guess, answer)
            
            # Check for an IMMEDIATE win first.
            if pattern == (2, 2, 2, 2, 2):
                print(f"Won in {j} guesses!")
                scores.append(j)
                break # Exit the 'while' loop for this run
                
            # If not a win, update the list and continue
            current_answers = logic.update(best_guess, pattern, current_answers)
            
            #  Check for "solved by deduction"
            if len(current_answers) == 1:
                j += 1 # Add the final guess
                print(f"Won in {j} guesses! (Solved by deduction)")
                scores.append(j)
                break # Exit the 'while' loop
            elif len(current_answers) == 0:
                print(f"Error! Bot failed to find '{answer}'. No words left.")
                scores.append(7) # Add a 'fail' score
                break

            # 
            # Use the 'strategy_func' that was passed in
            best_guess = strategy_func(current_answers, guess_list)
            j += 1
            
            if j > 6:
                print(f"Failed! Bot did not guess '{answer}' in 6 tries.")
                scores.append(7) # Add a 'fail' score
                break

    # Calculate and return the average score
    if not scores: # Avoid division by zero
        return 0
        
    avg_score = sum(scores) / len(scores)
    return avg_score

# --- Main ---
def main():
    start = time.time()
    try:
        with open("word_list.txt", 'r') as f:
            master_answers = [line.strip().lower() for line in f]
        with open("possible_words.txt", 'r') as f:
            guess_list = [line.strip().lower() for line in f]
    except FileNotFoundError:
        print("Error: 'word_list.txt' or 'possible_words.txt' not found.")
        return

    total_answer_count = len(master_answers)

    while(1):
        runs_input = input(f"How many runs? (Type 'ALL' for all {total_answer_count} answers): ")
        
        if runs_input.lower() == "all":
            runs = total_answer_count 
            break
        try:
            runs = int(runs_input)
            if runs > total_answer_count:
                print(f"Max runs is {total_answer_count}. Setting to max.")
                runs = total_answer_count
            break
        except Exception as e:
            print("Not an int.")
            
    print("\n--- Running Top 1 (Pure Entropy) Strategy ---")
    score_top1 = run_simulation(runs, master_answers, guess_list, logic.entropy)
    
    #print("\n--- Running Top 4 (Hard Mode) Strategy ---")
    #score_top4 = run_simulation(runs, master_answers, guess_list, logic.find_top4) 
    end = time.time()
    print("\n--- Final Results ---")
    print(f"Avg. Score (Top 1 Strategy): {score_top1:.4f}")
    #print(f"Avg. Score (Top 4 Strategy): {score_top4:.4f}")
    running_time = end - start
    print(f"it took {running_time:.4f} seconds")
if __name__ == "__main__":
    main()
