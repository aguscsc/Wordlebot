import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
LISTS_DIR = os.path.join(PROJECT_ROOT, "lists")
most_used_words_EN_list = os.path.join(LISTS_DIR, "most_used_words_EN.txt")
kli_list = os.path.join(LISTS_DIR, "kli_words.txt")
with open(most_used_words_EN_list, "r") as f_in:
    with open(kli_list, "w") as f_out:
        for line in f_in:
            parts = line.strip().lower().split()

            # Safety check: ensure line has at least a word
            if not parts:
                continue

            word = parts[0]

            # If there's a count, grab it. If not, default to 1.
            count = parts[1] if len(parts) > 1 else "1"

            # Check length of the WORD
            if len(word) == 5:
                f_out.write(f"{word} {count}\n")

print("Done! kld_words.txt is ready with frequencies.")
