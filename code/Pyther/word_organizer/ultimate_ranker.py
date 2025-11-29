import math
import os

# --- CONFIGURATION ---
# The exact curve that got you 3.47
CENTER = 4.5
WIDTH = 2.0

INPUT_ENTROPY = "ranked_word_list.txt"  # Format: "word 5.85"
INPUT_FREQ = "kli_words.txt"  # Format: "word 123456"
OUTPUT_FILE = "ultimate_rank.txt"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
dir1 = os.path.join(PROJECT_ROOT, "lists")
input_path1 = os.path.join(dir1, INPUT_ENTROPY)
input_path2 = os.path.join(dir1, INPUT_FREQ)


def get_sigmoid_score(count):
    """
    Converts raw count to 0.0-1.0 score using your calibrated curve.
    """
    if count <= 0:
        count = 1
    log_count = math.log10(count)
    return 1 / (1 + math.exp(-(log_count - CENTER) / WIDTH))


def main():
    print("--- GENERATING ULTIMATE RANK ---")

    # 1. Load Frequency Scores (The "Priors")
    freq_map = {}
    try:
        with open(input_path2, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 2:
                    continue
                word = parts[0].lower()
                try:
                    count = int(parts[1])
                    freq_map[word] = get_sigmoid_score(count)
                except ValueError:
                    continue
        print(f"Loaded {len(freq_map)} frequency weights.")
    except FileNotFoundError:
        print(f"Error: Could not find {input_path2}")
        return

    # 2. Load Entropy Scores & Calculate Ultimate Score
    ultimate_list = []

    try:
        with open(input_path1, "r") as f:
            for line in f:
                # Skip empty lines
                if ":" not in line:
                    continue

                try:
                    # Split into ["1. raise", "5.8772 bits"]
                    left, right = line.split(":")

                    # Clean the word side: Remove "1." and whitespace
                    # "1. raise" -> "raise"
                    word = left.split(".")[1].strip().lower()

                    # Clean the number side: Remove "bits" and whitespace
                    # "5.8772 bits" -> 5.8772
                    entropy_val = float(right.replace("bits", "").strip())

                    # Get Mass (Score Addition Logic)
                    prob_score = freq_map.get(
                        word, 0.45
                    )  # Default to 0.45 (C=4.5 baseline)

                    # Score = Entropy + Probability
                    final_score = entropy_val + prob_score

                    ultimate_list.append(
                        {
                            "word": word,
                            "entropy": entropy_val,
                            "prob": prob_score,
                            "final": final_score,
                        }
                    )
                except (IndexError, ValueError):
                    print(f"Skipping malformed line: {line.strip()}")
                    continue

        print(f"Processed {len(ultimate_list)} ranked words.")

    except FileNotFoundError:
        print(f"Error: Could not find {input_path1}")
        return

    # 3. Sort by Final Score (Highest First)
    ultimate_list.sort(key=lambda x: x["final"], reverse=True)
    # 4. Save to Output
    with open(OUTPUT_FILE, "w") as f:
        f.write(f"{'WORD':<10} | {'FINAL':<8} | {'ENTROPY':<8} | {'PROB MASS'}\n")
        f.write("-" * 45 + "\n")

        for item in ultimate_list:
            f.write(
                f"{item['word']:<10} | {item['final']:.4f}   | {item['entropy']:.4f}   | {item['prob']:.4f}\n"
            )

    # 5. Preview Top 10
    print("\n--- TOP 10 WORDS ---")
    print(f"{'WORD':<10} | {'FINAL':<8} | {'ENTROPY':<8} | {'PROB'}")
    for item in ultimate_list[:10]:
        print(
            f"{item['word']:<10} | {item['final']:.4f}   | {item['entropy']:.4f}   | {item['prob']:.4f}"
        )

    print(f"\nSaved full list to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
