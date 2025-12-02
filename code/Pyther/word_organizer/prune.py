import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
enhanced_shannon_dir = os.path.join(project_root, "enhanced_shannon")

if enhanced_shannon_dir not in sys.path:
    sys.path.append(enhanced_shannon_dir)

import kli_logic as logic

def generate_optimized_list():
    print("--- DICTIONARY OPTIMIZER ---")
    
    # 1. Load Data
    logic.load_weights("kli_words.txt", logic.LISTS_DIR)
    
    # Paths
    path_answers = os.path.join(logic.LISTS_DIR, "word_list.txt")
    path_full = os.path.join(logic.LISTS_DIR, "allowed_words.txt") # You need to download this!
    path_out = os.path.join(logic.LISTS_DIR, "optimized_guesses.txt")
    
    # Load sets
    with open(path_answers, 'r') as f:
        answers = set(line.strip().lower() for line in f)
        
    try:
        with open(path_full, 'r') as f:
            full_dict = [line.strip().lower() for line in f]
    except FileNotFoundError:
        print("Error: Please download the full 12k 'allowed_words.txt' first!")
        return

    print(f"Processing {len(full_dict)} words...")
    keep_list = []
    
    for word in full_dict:
        # CRITERIA 1: Always keep potential answers
        if word in answers:
            keep_list.append(word)
            continue
            
        # CRITERIA 2: Frequency Check
        # If a word is somewhat common, it's a valid linguistic probe.
        # Rare junk (score < 0.1) is useless for splitting common words.
        mass = logic.get_word_mass(word)
        if mass > 0.2: 
            keep_list.append(word)
            continue
            
        # CRITERIA 3: Letter Utility (Heuristic)
        # Keep words that use high-value letters (E, A, R, I, O, T, N, S, L, C)
        # Discard words with J, Q, Z, X unless they are common.
        common_letters = set("eariotnslc")
        unique_chars = set(word)
        overlap = len(unique_chars.intersection(common_letters))
        
        # If it has 4 or 5 very common letters, it's a good probe (e.g., 'SAINE')
        if overlap >= 4:
            keep_list.append(word)

    # Sort for tidiness
    keep_list.sort()
    
    # Save
    with open(path_out, 'w') as f:
        for w in keep_list:
            f.write(f"{w}\n")
            
    print(f"\nOptimization Complete!")
    print(f"Original Size: {len(full_dict)}")
    print(f"Optimized Size: {len(keep_list)}")
    print(f"Reduction: {100 - (len(keep_list)/len(full_dict)*100):.1f}% junk removed.")
    print(f"Saved to: {path_out}")

if __name__ == "__main__":
    generate_optimized_list()
