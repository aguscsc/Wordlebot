import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
enhanced_shannon_dir = os.path.join(project_root, "enhanced_shannon")

if enhanced_shannon_dir not in sys.path:
    sys.path.append(enhanced_shannon_dir)

import kli_logic


def diagnose_bot():
    print("--- DIAGNOSTIC MODE ---")

    # 1. Load your Answer List
    word_path = os.path.join(kli_logic.LISTS_DIR, "word_list.txt")
    try:
        with open(word_path, "r") as f:
            answers = [line.strip().lower() for line in f]
    except FileNotFoundError:
        print("Error: word_list.txt not found.")
        return

    # 2. Load Weights
    kli_logic.load_weights("kli_words.txt", kli_logic.LISTS_DIR)

    # 3. Check for "Invisible" or "Trash" Answers
    missing = 0
    trash_zone = 0  # Score < 0.1
    mid_zone = 0  # Score 0.1 - 0.5
    good_zone = 0  # Score > 0.5

    trash_examples = []

    for word in answers:
        mass = kli_logic.get_word_mass(word)

        # Check if it's the default epsilon (missing from file)
        if mass == 0.00001:
            missing += 1
            # missin_wordy = word
        elif mass < 0.1:
            trash_zone += 1
            if len(trash_examples) < 5:
                trash_examples.append(f"{word} ({mass:.4f})")
        elif mass < 0.5:
            mid_zone += 1
        else:
            good_zone += 1

    total = len(answers)

    print(f"\nAnalyzing {total} Answer Words:")
    print(
        f"MISSING from freq list: {missing}  ({missing / total:.1%})  <- MAJOR DANGER"
    )
    print(
        f"TRASH ZONE (< 0.1):     {trash_zone}  ({trash_zone / total:.1%})  <- Bot ignores these"
    )
    print(f"MID ZONE (0.1 - 0.5):   {mid_zone}   ({mid_zone / total:.1%})")
    print(f"GOOD ZONE (> 0.5):      {good_zone}  ({good_zone / total:.1%})")

    if trash_zone > 0:
        print(f"Examples of ignored words: {trash_examples}")

    # Recommendation
    if missing > 0:
        print("\n[!] CRITICAL FIX: Your frequency file is missing valid answers.")
        print(
            "    You need a better 'most_used_words.txt' or you need to append your word_list to it."
        )
    elif trash_zone > (total * 0.2):
        print("\n[!] TUNING FIX: You are ignoring too many valid answers.")
        print("    Decrease CENTER (e.g. to 5.0) or Increase WIDTH (to 2.0).")
    else:
        print(
            "\n[+] STATUS: Distribution looks healthy. The issue might be the Simulation Randomness."
        )


if __name__ == "__main__":
    diagnose_bot()
