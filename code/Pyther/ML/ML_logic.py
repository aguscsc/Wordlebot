import math
from math import log2
import os


# --- 1. CONFIGURATION: THE GENTLE CURVE ---
# We use 4.5/2.0 to ensure rare words get a score ~0.45 instead of 0.1.
# This prevents the bot from "ignoring" rare answers in your random simulation.
CENTER = 4.5
WIDTH = 2.0

PROB_SCALAR = 2.0
# --- FREQUENCY LOADER ---
WORD_WEIGHTS = {}
LOADED = False


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
LISTS_DIR = os.path.join(PROJECT_ROOT, "lists")


def load_weights(filepath, LISTS_DIR):
    global WORD_WEIGHTS, LOADED
    file = os.path.join(LISTS_DIR, filepath)
    try:
        with open(file, "r") as f:
            for line in f:
                parts = line.split()
                if len(parts) < 2:
                    continue
                word = parts[0].strip().lower()
                try:
                    count = int(parts[1])
                except:
                    count = 1

                if count <= 0:
                    count = 1
                # The Sigmoid Calculation (0.0 to 1.0)
                score = 1 / (1 + math.exp(-(math.log10(count) - CENTER) / WIDTH))
                WORD_WEIGHTS[word] = score
        LOADED = True
        print(f"Logic Score: Loaded weights with C={CENTER}, W={WIDTH}")
    except FileNotFoundError:
        print("Freq file not found.")


def get_word_mass(word):
    if not LOADED:
        load_weights("kli_words.txt", LISTS_DIR)
    # Return 0.00001 for unknown words so they aren't totally zero
    return WORD_WEIGHTS.get(word, 0.00001)


# --- STANDARD PATTERN LOGIC ---
def get_pattern(guess, answer):
    pattern = [0] * 5
    answer_letters = list(answer)
    # Green Pass
    for i in range(5):
        if guess[i] == answer[i]:
            pattern[i] = 2
            answer_letters[i] = None
    # Yellow Pass
    for i in range(5):
        if pattern[i] == 2:
            continue
        if guess[i] in answer_letters:
            pattern[i] = 1
            answer_letters.remove(guess[i])
    return tuple(pattern)


# --- THE OPTIMAL STRATEGY: SCORE ADDITION ---
def entropy(answers, guess_list):
    # 1. ENDGAME SHORTCUT (Greedy)
    # If 2 words left, don't simulate. Pick the heaviest one.
    n = len(answers)
    if n <= 2:
        return max(answers, key=get_word_mass)

    # DYNAMIC WEIGHTS (Derived from ML Analysis)
    if n > 100:
        # Early Game
        W_ENT = 0.4298
        W_PROB = 0.5702
    elif n > 10:
        # Mid Game
        W_ENT = 0.6460
        W_PROB = 0.3540
    else:
        # End Game
        W_ENT = 0.6798
        W_PROB = 0.3202

    best_guess = "none"
    max_score = -1

    # Pre-calculate Total Mass (to normalize probabilities)
    total_mass = sum(get_word_mass(w) for w in answers)

    # Safety check
    if total_mass == 0:
        return answers[0]

    # Pre-calculate the "Win Probability" P(w) for every candidate in 'answers'
    # This turns the raw mass (e.g. 0.9) into a true probability (e.g. 0.4 or 40%)
    candidate_probs = {w: get_word_mass(w) / total_mass for w in answers}

    for guess_word in guess_list:
        patterns_counts = {}

        # We assume the answer comes from 'answers', so we weigh patterns by Mass
        for answer in answers:
            pattern = get_pattern(guess_word, answer)

            # Weighted Entropy Logic:
            # We add the PROBABILITY of the answer being true
            p_mass = candidate_probs[answer]
            patterns_counts[pattern] = patterns_counts.get(pattern, 0.0) + p_mass

        # --- A. CALCULATE ENTROPY ---
        entropy_val = 0
        for p in patterns_counts.values():
            if p > 0:
                entropy_val += p * (-log2(p))

        # --- B. CALCULATE SCORE ---
        # Formula: Score = Entropy + P(Win)
        # 1. Start with the Information Gain (Entropy)
        # 2. Add the Probability that this guess ends the game NOW.
        p_win = candidate_probs.get(guess_word, 0.0)

        # (The "Safety Valve"):
        # If a guess gives almost ZERO info (entropy < 1.0), punish it
        # unless it is nearly GUARANTEED to be the winner (p_win > 0.8).
        total_score = (W_ENT*entropy_val) + (W_PROB*p_win*PROB_SCALAR)

        if total_score > max_score:
            max_score = total_score
            best_guess = guess_word

    return best_guess


# --- update list ---
def update(best_guess, pattern, answers):
    new_answers = [word for word in answers if get_pattern(best_guess, word) == pattern]
    return new_answers


# --- calculate actual bits of information per guess ---
# (Updated to use mass for consistency, optional)
def get_bits(answers, total_initial_mass=None):
    # This is just for display, standard log2(1/p) works fine
    return -log2(1.0 / len(answers)) if len(answers) > 0 else 0


# --- Main (For testing directly) ---
def main(answers, guess, total_answers):
    # Ensure weights are loaded
    load_weights("kli_words.txt", LISTS_DIR)

    best_guess = input("Enter your first word (e.g., raise): ")
    while 1:
        numbers = input("Pattern (grey=0, yellow=1, green=2): ")
        try:
            pattern = tuple(map(int, numbers))
        except ValueError:
            print("Invalid input.")
            continue

        answers = update(best_guess, pattern, answers)

        print(f"{len(answers)} words remain.")
        if len(answers) < 15:
            print(f"Remaining: {answers}")

        if len(answers) <= 1:
            if len(answers) == 1:
                print(f"The word is: {answers[0]}")
            break

        best_guess = entropy(answers, guess)
        print(f"Recommended Guess: {best_guess}")


if __name__ == "__main__":
    # --- PATH SETUP ---

    word_list = os.path.join(LISTS_DIR, "word_list.txt")
    possible_list = os.path.join(LISTS_DIR, "possible_words.txt")
    try:
        with open(word_list, "r") as f:
            answers = [line.strip().lower() for line in f]
        with open(possible_list, "r") as f:
            guess = [line.strip().lower() for line in f]

        # Pre-load weights
        load_weights("kli_words.txt", LISTS_DIR)

        main(answers, guess, len(answers))
    except FileNotFoundError:
        print(
            "Error: Ensure word_list.txt, possible_words.txt, and kli_words.txt exist."
        )

