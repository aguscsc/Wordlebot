import kli_logic as logic
import random
import time
import os
import sys
from joblib import Parallel, delayed
from tqdm import tqdm  # pip install tqdm

# --- 1. WORKER FUNCTION (Runs on a separate core) ---
def play_single_game(target_word, master_answers, guess_list, strategy_func):
    """
    Plays ONE game against a specific target word.
    Returns the number of guesses used (or 7 if failed).
    """
    # Create a fresh copy of answers for this run
    current_answers = list(master_answers)
    
    # Start with a randomized best opener
    best_guess = "slate" 
    
    j = 1
    while j <= 6:
        pattern = logic.get_pattern(best_guess, target_word)
        
        # Check Win
        if pattern == (2, 2, 2, 2, 2):
            return j
            
        # Update List
        current_answers = logic.update(best_guess, pattern, current_answers)
        
        # Deduction Win
        if len(current_answers) == 1:
            return j + 1
        elif len(current_answers) == 0:
            return 7 # Error
            
        # Calculate Next Guess
        best_guess = strategy_func(current_answers, guess_list)
        j += 1
        
    return 7 # Failed

# --- 2. MAIN DRIVER ---
def main():
    start = time.time()

    # --- PATH SETUP ---
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
    LISTS_DIR = os.path.join(PROJECT_ROOT, "lists")
    
    try:
        path_answers = os.path.join(LISTS_DIR, "word_list.txt")
        path_guesses = os.path.join(LISTS_DIR, "possible_words.txt")
        
        with open(path_answers, "r") as f:
            master_answers = [line.strip().lower() for line in f]
        with open(path_guesses, "r") as f:
            guess_list = [line.strip().lower() for line in f]
    except FileNotFoundError:
        print(f"Error: Could not find list files in {LISTS_DIR}")
        return

    # Load Weights (Shared by all workers in memory)
    print("Loading frequency data...")
    logic.load_weights("kli_words.txt", LISTS_DIR)

    total_answer_count = len(master_answers)

    # Get User Input
    while True:
        runs_input = input(f"How many runs? (Type 'ALL' for {total_answer_count}): ")
        if runs_input.lower() == "all":
            runs = total_answer_count
            targets = master_answers # Deterministic: Run strictly in order
            break
        try:
            runs = int(runs_input)
            runs = min(runs, total_answer_count)
            # Random sample if not running ALL
            targets = random.sample(master_answers, runs) 
            break
        except ValueError:
            print("Please enter a number.")

    print(f"\n--- Running Parallel Simulation for {runs} games ---")
    
    # --- PARALLEL EXECUTION ---
    # n_jobs=-1 uses all available CPU cores
    results = Parallel(n_jobs=-1)(
        delayed(play_single_game)(
            target, 
            master_answers, 
            guess_list, 
            logic.entropy
        ) for target in tqdm(targets, desc="Simulating")
    )
    
    # Force result to list to satisfy linters and enable math
    scores = list(results)

    # --- RESULTS ---
    if not scores:
        print("No games played.")
        return

    avg_score = sum(scores) / len(scores)
    fails = scores.count(7)
    end = time.time()

    print("\n" + "=" * 30)
    print(f"FINAL AVERAGE SCORE: {avg_score:.4f}")
    print(f"Fails: {fails}/{runs}")
    print(f"Time Taken: {end - start:.2f} seconds")
    print("=" * 30)

if __name__ == "__main__":
    try:
        main()
        # Clean exit to stop ResourceTracker errors
        sys.exit(0)
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")
        sys.exit(0)
