import ML_logic as logic
import random
import matplotlib.pyplot as plt
import os
import time
from joblib import Parallel, delayed

# --- 1. SETUP (Main Process Only) ---
# We define paths here so workers know where to look if needed
logic.load_weights("kli_words.txt", logic.LISTS_DIR)
word_list_path = os.path.join(logic.LISTS_DIR, "word_list.txt")
possible_list_path = os.path.join(logic.LISTS_DIR, "possible_words.txt")

# Read files once into memory to pass to workers (faster than re-reading files)
with open(word_list_path, 'r') as f:
    MASTER_ANSWERS = [line.strip().lower() for line in f]
with open(possible_list_path, 'r') as f:
    MASTER_GUESSES = [line.strip().lower() for line in f]

# --- 2. THE WORKER FUNCTION ---
# This runs on a separate CPU core.
def evaluate_scalar(scalar, num_games=2331):
    # Important: Set the global variable for THIS process
    logic.PROB_SCALAR = scalar
    scores = []
    
    # Run the mini-simulation
    for i in range(num_games):
        if num_games == 2331:
            target = MASTER_ANSWERS[i]
        else:
            target = random.choice(MASTER_ANSWERS)
        current = list(MASTER_ANSWERS)
        best_guess = "raise" # Hardcoded opener
        
        turn = 1
        while turn <= 6:
            if best_guess == target:
                scores.append(turn)
                break
            
            # Logic Update
            pat = logic.get_pattern(best_guess, target)
            current = logic.update(best_guess, pat, current)
            
            if not current: break
            if len(current) == 1:
                scores.append(turn + 1)
                break
            
            best_guess = logic.entropy(current, MASTER_GUESSES)
            turn += 1
            if turn > 6: scores.append(7) # Penalty

    # Return the scalar and its result to the main process
    avg_score = sum(scores) / len(scores) if scores else 7.0
    return (scalar, avg_score)

# --- 3. MAIN EXECUTION ---
def run_tuning_sweep():
    # Define Scalars to Test
    #test_scalars = [1.0, 2.0, 3.0, 4.0, 5.0, 5.88, 7.0, 9.0, 12.0, 15.0]
    test_scalars = [1.70,1.71,1.72,1.73,1.74,1.75]
    
    print(f"Starting parallel sweep on {len(test_scalars)} scalars using all CPU cores...")
    start_time = time.time()

    # --- PARALLEL EXECUTION ---
    # n_jobs=-1 means "Use all available CPUs"
    # This spawns independent processes that run 'evaluate_scalar'
    results_list = Parallel(n_jobs=-1)(
        delayed(evaluate_scalar)(s) for s in test_scalars
    )
    
    end_time = time.time()
    
    # Sort results by scalar value for cleaner plotting/printing
    results_list.sort(key=lambda x: x[0])
    
    # Unpack for plotting
    x_vals = [r[0] for r in results_list]
    y_vals = [r[1] for r in results_list]

    # Print Table
    print(f"\n{'SCALAR':<10} | {'AVG SCORE':<10}")
    print("-" * 25)
    for s, avg in results_list:
        print(f"{s:<10} | {avg:.4f}")
    
    print(f"\nTotal Time: {end_time - start_time:.2f} seconds")

    # --- VISUALIZATION ---
    plt.figure(figsize=(10, 6))
    plt.plot(x_vals, y_vals, marker='o', linestyle='-', color='b')
    
    # Highlight the winner
    best_tuple = min(results_list, key=lambda x: x[1])
    best_s = best_tuple[0]
    best_val = best_tuple[1]
    
    plt.plot(best_s, best_val, 'ro', markersize=12)
    plt.text(best_s, best_val + 0.005, f" Winner: {best_s}\n({best_val:.4f})", 
             ha='center', va='bottom', fontweight='bold', color='darkred')

    plt.title("Hyperparameter Tuning: Optimal Probability Scalar")
    plt.xlabel("Scalar Value (Multiplier for P)")
    plt.ylabel("Average Guesses (Lower is Better)")
    plt.grid(True, alpha=0.3)
    plt.show()

if __name__ == "__main__":
    run_tuning_sweep()
