import random
import csv
import math
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
enhanced_shannon_dir = os.path.join(project_root, "enhanced_shannon")

if enhanced_shannon_dir not in sys.path:
    sys.path.append(enhanced_shannon_dir)

import kli_logic as logic

# CONFIGURATION
OUTPUT_FILE = "bot_decision_data.csv"


def run_data_generation():
    # 1. Setup
    print("Loading dictionary...")
    logic.load_weights("kli_words.txt", logic.LISTS_DIR)
    word_list = os.path.join(logic.LISTS_DIR, "word_list.txt")
    possible_list = os.path.join(logic.LISTS_DIR, "possible_words.txt")

    with open(word_list, "r") as f:
        master_answers = [line.strip().lower() for line in f]
    with open(possible_list, "r") as f:
        guesses = [line.strip().lower() for line in f]

    runs = int(input("input how many games: "))
    print(f"Simulating {runs} games to build XAI dataset...")

    # 2. Prepare CSV Writer
    # We capture the "State" (Context) and the "Action" (Metrics of the chosen word)
    headers = [
        "game_id",
        "turn",
        "candidates_left",
        "chosen_word",
        "entropy_score",  # Feature A
        "prob_score",  # Feature B
        "combined_score",  # The Bot's internal ranking
        "is_winner",  # TARGET 1 (Immediate Success)
        "total_game_steps",  # TARGET 2 (Long-term Success)
    ]

    data_rows = []

    for game_id in range(runs):
        if runs == 2331:
            answer = master_answers[game_id]
        else:
            answer = random.choice(master_answers)
        current_answers = list(master_answers)

        # Track the game history to save later
        game_moves = []

        # Hardcoded Turn 1 (We don't analyze this because it's static)
        best_guess = "slate"

        turn = 1
        while turn <= 6:
            # Check result
            pattern = logic.get_pattern(best_guess, answer)

            if pattern == (2, 2, 2, 2, 2):
                # Game Over - Win
                # Update all moves in this game with the final result
                for move in game_moves:
                    move["total_game_steps"] = turn
                    move["is_winner"] = move["chosen_word"] == best_guess
                    data_rows.append(move)
                break

            # Update Candidates
            current_answers = logic.update(best_guess, pattern, current_answers)
            if not current_answers:
                break

            # --- THE "SPYING" PART ---
            # We need to calculate the metrics for the NEXT guess
            # This logic mimics 'logic_score.py' but extracts the numbers

            turn += 1

            # 1. Logic for Endgame (Greedy)
            if len(current_answers) <= 2:
                best_guess = max(current_answers, key=logic.get_word_mass)
                ent_val = 0
                prob_val = logic.get_word_mass(best_guess)  # Raw mass proxy
            else:
                # 2. Logic for Midgame (The Score Formula)
                # We have to re-run the entropy loop to get the specific values
                # for the winner. This is slow but necessary for data generation.

                best_guess = "none"
                max_score = -1
                stats = (0, 0)  # (ent, prob)

                total_mass = sum(logic.get_word_mass(w) for w in current_answers)
                candidate_probs = {
                    w: logic.get_word_mass(w) / total_mass for w in current_answers
                }

                # Check all guesses to find the winner again and capture its stats
                # (We optimize by only checking valid candidates + top guesses to save time)
                search_space = current_answers if len(current_answers) < 20 else guesses

                for guess_word in search_space:
                    # ... Copy of logic_score.py calculation ...
                    patterns_counts = {}
                    for a in current_answers:
                        pat = logic.get_pattern(guess_word, a)
                        patterns_counts[pat] = (
                            patterns_counts.get(pat, 0.0) + candidate_probs[a]
                        )

                    ent = 0
                    for p in patterns_counts.values():
                        if p > 0:
                            ent += p * (-math.log2(p))

                    prob = candidate_probs.get(guess_word, 0.0)
                    score = ent + prob

                    if score > max_score:
                        max_score = score
                        best_guess = guess_word
                        stats = (ent, prob)

            # Record the move
            game_moves.append(
                {
                    "game_id": game_id,
                    "turn": turn,
                    "candidates_left": len(current_answers),
                    "chosen_word": best_guess,
                    "entropy_score": stats[0],
                    "prob_score": stats[1],
                    "combined_score": stats[0] + stats[1],
                    "is_winner": False,  # Placeholder
                    "total_game_steps": 7,  # Placeholder
                }
            )

        if (game_id + 1) % 10 == 0:
            print(f"Simulated {game_id + 1} games...")

    # 3. Save to CSV
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data_rows)

    print(f"Done! Dataset saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    run_data_generation()
