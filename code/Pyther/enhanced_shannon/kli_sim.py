import kli_logic as logic  # Importing your new KLI logic
import random
import time
import os


def run_simulation(runs, master_answers, guess_list, strategy_func):
    """
    Runs a Wordle simulation using the Probability Mass (KLI) strategy.
    """
    scores = []

    for i in range(runs):
        # Create a fresh copy of answers for this run
        current_answers = list(master_answers)

        # Pick the answer
        if runs == len(master_answers):
            answer = master_answers[i]
        else:
            answer = random.choice(master_answers)

        print(f"\n--- Run {i + 1}/{runs}: Guessing '{answer}' ---")

        # Start with the mathematically best opener for this dictionary
        # "salet" is often preferred for KLI/Mass, "raise" for Entropy.
        best_guesses = ["raise", "slate", "irate", "crate"]
        best_guess = random.choice(best_guesses)

        j = 1
        while j <= 6:
            pattern = logic.get_pattern(best_guess, answer)

            # 1. Check for Win
            if pattern == (2, 2, 2, 2, 2):
                print(f"Won in {j} guesses! (Guessed '{best_guess}')")
                scores.append(j)
                break

            # 2. Update List
            current_answers = logic.update(best_guess, pattern, current_answers)

            # 3. Check for Deduction Win
            if len(current_answers) == 1:
                j += 1
                print(
                    f"Won in {j} guesses! (Solved by deduction: '{current_answers[0]}')"
                )
                scores.append(j)
                break
            elif len(current_answers) == 0:
                print(f"Error! Bot failed to find '{answer}'.")
                scores.append(7)
                break

            # 4. Calculate Next Guess using KLI Logic
            # Note: We pass 'guess_list' so it can pick words not in the remaining answers
            best_guess = strategy_func(current_answers, guess_list)

            print(
                f"Guess {j}: {best_guess} (Remaining candidates: {len(current_answers)})"
            )

            j += 1
            if j > 6:
                print(f"Failed! Bot did not guess '{answer}' in 6 tries.")
                scores.append(7)
                break

    if not scores:
        return 0
    return sum(scores) / len(scores)


# --- Main ---
def main():
    start = time.time()

    # 1. Load Files

    # --- PATH SETUP ---
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
        print("Error: 'word_list.txt' or 'possible_words.txt' not found.")
        return

    # 2. IMPORTANT: Load the Frequency Weights for KLI
    print("Loading frequency data...")
    logic.load_weights("kli_words.txt", LISTS_DIR)

    total_answer_count = len(master_answers)

    # 3. Get User Input
    while True:
        runs_input = input(f"How many runs? (Type 'ALL' for {total_answer_count}): ")
        if runs_input.lower() == "all":
            runs = total_answer_count
            break
        try:
            runs = int(runs_input)
            runs = min(runs, total_answer_count)
            break
        except ValueError:
            print("Please enter a number.")

    print(f"\n--- Running KLI (Probability Mass) Strategy for {runs} games ---")

    # Run the sim using logic.entropy (which is now your KLI version)
    score = run_simulation(runs, master_answers, guess_list, logic.entropy)

    end = time.time()

    print("\n" + "=" * 30)
    print(f"FINAL AVERAGE SCORE: {score:.4f}")
    print(f"Time Taken: {end - start:.2f} seconds")
    print("=" * 30)


if __name__ == "__main__":
    main()
