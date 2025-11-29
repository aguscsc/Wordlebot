import matplotlib.pyplot as plt
import math
import os
import kli_logic as logic

FILENAME = "kli_words.txt"
CENTER = 4.5
WIDTH = 2.0


def calculate_score(count):
    if count <= 0:
        count = 1
    log_count = math.log10(count)
    return 1 / (1 + math.exp(-(log_count - CENTER) / WIDTH))


def main():
    # 1. Load the Data
    words_data = []

    # Check if file exists, if not try the other name

    target_file = os.path.join(logic.LISTS_DIR, FILENAME)
    if not os.path.exists(target_file):
        print(f"Error: Could not find {FILENAME}")
        return

    print(f"Reading from {target_file}...")

    with open(target_file, "r") as f:
        for line in f:
            parts = line.split()
            if len(parts) < 2:
                continue

            word = parts[0].strip().lower()
            try:
                count = int(parts[1])
            except ValueError:
                continue

            score = calculate_score(count)
            words_data.append((word, count, score))

    if not words_data:
        print("File was empty or invalid!")
        return

    # Sort by count for cleaner plotting
    words_data.sort(key=lambda x: x[1])

    # Unzip for plotting
    words, counts, scores = zip(*words_data)

    # 2. Setup the Plot
    plt.figure(figsize=(12, 7))

    # Plot all words as blue dots
    plt.scatter(counts, scores, color="blue", alpha=0.3, s=10, label="Word in List")

    # 3. Highlight Specific Strategy Words
    # These are words you likely care about. Let's see where they land.
    targets = [
        "about",
        "other",
        "crane",
        "raise",
        "salet",
        "slate",
        "trace",
        "fuzzy",
        "xylyl",
    ]

    found_targets = []
    for w, c, s in words_data:
        if w in targets:
            plt.plot(c, s, "ro", markersize=8)  # Red Dot
            plt.text(
                c, s + 0.02, w.upper(), ha="center", fontweight="bold", color="darkred"
            )
            found_targets.append(w)

    # 4. Draw the Threshold Lines
    plt.axhline(
        y=0.5, color="gray", linestyle="--", alpha=0.5, label="50% Mass Threshold"
    )
    plt.axvline(
        x=10**CENTER, color="green", linestyle=":", label=f"Center (10^{int(CENTER)})"
    )

    # 5. Formatting
    plt.xscale("log")  # Log scale is critical
    plt.xlabel("Word Frequency (Raw Count)")
    plt.ylabel("Sigmoid Score (Probability Mass)")
    plt.title(
        f"Actual Distribution of Your {len(words_data)} Words\n(Center={CENTER}, Width={WIDTH})"
    )
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.legend(loc="upper left")

    # Show stats
    print(f"Plotting {len(words_data)} words.")
    print(f"Top Score: {words_data[-1][0]} ({words_data[-1][2]:.4f})")
    print(f"Low Score: {words_data[0][0]} ({words_data[0][2]:.4f})")

    plt.show()


if __name__ == "__main__":
    main()
