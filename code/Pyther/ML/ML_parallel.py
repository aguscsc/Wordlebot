#import ML_logic as logic
import beam as logic
import random
import time
import os
from joblib import Parallel, delayed
from tqdm import tqdm  

def play_single_game(target_word, master_answers, guess_list, strategy_func):
    """
    Juega UNA sola partida de Wordle y retorna el puntaje (número de intentos).
    Si falla, retorna 7.
    """
    # Create a fresh copy of answers for this run
    current_answers = list(master_answers)
    
    # Start with the mathematically best opener
    #best_guesses = ["raise", "slate", "irate", "crate"]
    #best_guess = random.choice(best_guesses)
    best_guess = "slate"

    j = 1
    while j <= 6:
        pattern = logic.get_pattern(best_guess, target_word)

        # 1. Check for Win
        if pattern == (2, 2, 2, 2, 2):
            return j # Won

        # 2. Update List
        current_answers = logic.update(best_guess, pattern, current_answers)

        # 3. Check for Deduction Win
        if len(current_answers) == 1:
            return j + 1 # Won by deduction
        elif len(current_answers) == 0:
            return 7 # Error/Fail

        # 4. Calculate Next Guess using KLI/Entropy Logic
        # Pasamos guess_list para que pueda elegir palabras fuera de las candidatas
        best_guess = strategy_func(current_answers, guess_list)

        j += 1
    
    return 7 # Failed (did not guess in 6 tries)

# --- Main ---
def main():
    start = time.time()

    # 1. Load Files
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
    LISTS_DIR = os.path.join(PROJECT_ROOT, "lists")
    word_list = os.path.join(LISTS_DIR, "word_list.txt")
    possible_list = os.path.join(LISTS_DIR, "possible_words.txt")

    try:
        with open(word_list, "r") as f:
            master_answers = [line.strip().lower() for line in f]
        with open(possible_list, "r") as f:
            guess_list = [line.strip().lower() for line in f]
    except FileNotFoundError:
        print("Error: Files not found.")
        return

    # 2. Load Frequency Weights
    print("Loading frequency data...")
    logic.load_weights("kli_words.txt") #, logic.LISTS_DIR)

    total_answer_count = len(master_answers)

    # 3. Get User Input
    while True:
        runs_input = input(f"How many runs? (Type 'ALL' for {total_answer_count}): ")
        if runs_input.lower() == "all":
            runs = total_answer_count
            # Si es ALL, usamos la lista ordenada tal cual
            targets = master_answers 
            break
        try:
            runs = int(runs_input)
            runs = min(runs, total_answer_count)
            # Si es un subconjunto, elegimos al azar
            targets = random.sample(master_answers, runs) 
            break
        except ValueError:
            print("Please enter a number.")

    print(f"\n--- Running KLI Strategy for {runs} games on multiple cores ---")
    
    # 4. PARALLEL EXECUTION
    # n_jobs=-1 usa todos los núcleos disponibles de tu CPU.
    # tqdm crea una barra de progreso visual.
    scores = Parallel(n_jobs=-1)(
        delayed(play_single_game)(
            target, 
            master_answers, 
            guess_list, 
            logic.entropy
        ) for target in tqdm(targets, desc="Simulating")
    )

    # 5. Calculate Stats
    if not scores:
        print("No games played.")
        return

    avg_score = sum(scores) / len(scores)
    
    # Count fails (score 7 means fail usually in Wordle benchmarks)
    fails = scores.count(7)
    
    end = time.time()

    print("\n" + "=" * 30)
    print(f"FINAL AVERAGE SCORE: {avg_score:.4f}")
    print(f"Fails (did not guess): {fails}/{runs}")
    print(f"Time Taken: {end - start:.2f} seconds")
    print("=" * 30)

if __name__ == "__main__":
    main()
    os._exit(0)
