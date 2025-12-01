import ML_logic as logic
import time
import os
from joblib import Parallel, delayed

# --- CONFIGURATION ---
OPTIMAL_SCALAR = 2.0  # Put your best scalar here (e.g. 9.0)

# The "Titans" of Wordle to test against each other
CANDIDATES = [
    "raise", "slate", "crate", "irate", "trace", "salet", 
    "reast", "crane", "roate", "soare", "stare", "alert"
]

# --- SETUP ---
# Load data once in the main process
logic.load_weights("kli_words.txt", logic.LISTS_DIR)
word_list_path = os.path.join(logic.LISTS_DIR, "word_list.txt")
possible_list_path = os.path.join(logic.LISTS_DIR, "possible_words.txt")

with open(word_list_path, 'r') as f:
    MASTER_ANSWERS = [line.strip().lower() for line in f]
with open(possible_list_path, 'r') as f:
    MASTER_GUESSES = [line.strip().lower() for line in f]

# --- WORKER FUNCTION ---
def evaluate_opener(opener):
    # Set the logic to your optimized state
    logic.PROB_SCALAR = OPTIMAL_SCALAR
    
    total_guesses = 0
    fails = 0
    
    # Run deterministic simulation for ALL answers
    for target in MASTER_ANSWERS:
        current = list(MASTER_ANSWERS)
        best_guess = opener # FORCE THE OPENER
        
        turn = 1
        while turn <= 6:
            if best_guess == target:
                total_guesses += turn
                break
            
            # Logic Update
            pat = logic.get_pattern(best_guess, target)
            current = logic.update(best_guess, pat, current)
            
            if not current: 
                total_guesses += 7
                fails += 1
                break
            if len(current) == 1:
                total_guesses += (turn + 1)
                break
            
            # Mid-game Logic
            best_guess = logic.entropy(current, MASTER_GUESSES)
            turn += 1
            if turn > 6: 
                total_guesses += 7
                fails += 1

    avg = total_guesses / len(MASTER_ANSWERS)
    return (opener, avg, fails)

# --- MAIN ---
def main():
    print(f"--- BENCHMARKING OPENERS (Scalar={OPTIMAL_SCALAR}) ---")
    print(f"Testing {len(CANDIDATES)} openers against {len(MASTER_ANSWERS)} answers...")
    
    start = time.time()

    # Run in parallel
    results = Parallel(n_jobs=-1)(
        delayed(evaluate_opener)(word) for word in CANDIDATES
    )
    
    end = time.time()
    
    # Sort by Score (Lowest is Best)
    results.sort(key=lambda x: x[1])
    
    print("\n" + "="*45)
    print(f"{'RANK':<4} | {'OPENER':<10} | {'AVG SCORE':<10} | {'FAILS'}")
    print("-" * 45)
    
    for i, (word, avg, fail) in enumerate(results):
        prefix = "👑 " if i == 0 else "   "
        print(f"{prefix}{i+1:<3} | {word:<10} | {avg:.4f}     | {fail}")
        
    print("="*45)
    print(f"Total Time: {end - start:.2f} seconds")

if __name__ == "__main__":
    main()
