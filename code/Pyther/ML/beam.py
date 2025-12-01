import math
from math import log2
import os

# --- 1. YOUR TUNED CONSTANTS ---
# Keep these! They are the foundation of your pruning.
CENTER = 4.5
WIDTH = 2.0
PROB_SCALAR = 2.0  # Or whatever won your sweep (e.g. 2.0 or 9.0)

# --- 2. CONFIGURATION ---
# How many top candidates to simulate deeply?
# 10-15 is the sweet spot. 
# Lower = Faster but might miss a clever move.
# Higher = Slower but finds "God Mode" moves.
PRUNE_TOP_N = 12

# --- LOAD WEIGHTS ---
WORD_WEIGHTS = {}
LOADED = False
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LISTS_DIR = os.path.join(os.path.dirname(BASE_DIR), "lists")

def load_weights(filename="kli_words.txt"):
    global WORD_WEIGHTS, LOADED
    filepath = os.path.join(LISTS_DIR, filename)
    try:
        with open(filepath, 'r') as f:
            for line in f:
                parts = line.split()
                if len(parts) < 2: continue
                word = parts[0].strip().lower()
                try: count = int(parts[1])
                except: count = 1
                if count <= 0: count = 1
                score = 1 / (1 + math.exp(-(math.log10(count) - CENTER) / WIDTH))
                WORD_WEIGHTS[word] = score
        LOADED = True
    except FileNotFoundError:
        pass

def get_word_mass(word):
    if not LOADED: load_weights()
    return WORD_WEIGHTS.get(word, 0.00001)

# --- HELPERS ---
def get_pattern(guess, answer):
    # (Optimized Pattern Matcher code goes here - keeping it brief)
    # Use your existing robust implementation
    pattern = [0] * 5
    answer_letters = list(answer)
    for i in range(5):
        if guess[i] == answer[i]:
            pattern[i] = 2
            answer_letters[i] = None
    for i in range(5):
        if pattern[i] == 2: continue
        if guess[i] in answer_letters:
            pattern[i] = 1
            answer_letters.remove(guess[i])
    return tuple(pattern)

def update(best_guess, pattern, answers):
    return [w for w in answers if get_pattern(best_guess, w) == pattern]

# --- 1-STEP SCORE (Used for Pruning) ---
def get_greedy_score(guess, answers, candidate_probs):
    patterns_counts = {}
    for answer in answers:
        pattern = get_pattern(guess, answer)
        p_mass = candidate_probs[answer]
        patterns_counts[pattern] = patterns_counts.get(pattern, 0.0) + p_mass

    entropy_val = 0
    for p in patterns_counts.values():
        if p > 0: entropy_val += p * (-log2(p))
    
    p_win = candidate_probs.get(guess, 0.0)
    return entropy_val + (p_win * PROB_SCALAR)

# --- 2-STEP DEEP SEARCH ---
def entropy(answers, guess_list):
    
    # 1. Endgame Shortcut (Standard)
    if len(answers) <= 2:
        return max(answers, key=get_word_mass)

    # Pre-calc Mass
    total_mass = sum(get_word_mass(w) for w in answers)
    if total_mass == 0: return answers[0]
    candidate_probs = {w: get_word_mass(w) / total_mass for w in answers}

    # 2. PRUNING PHASE
    # We cannot simulate 2300 words. We filter for the Top N most promising.
    search_space = answers if len(answers) < 20 else guess_list
    
    # Score all candidates using your fast Greedy formula
    candidates = []
    for guess in search_space:
        score = get_greedy_score(guess, answers, candidate_probs)
        candidates.append((guess, score))
    
    # Sort and Keep Top N
    candidates.sort(key=lambda x: x[1], reverse=True)
    shortlist = [x[0] for x in candidates[:PRUNE_TOP_N]]
    
    # 3. DEEP SIMULATION PHASE
    # Objective: Minimize "Expected Remaining Entropy"
    
    best_word = shortlist[0]
    best_expected_score = -1
    
    for guess in shortlist:
        # Group answers by pattern (Future Universes)
        groups = {}
        for ans in answers:
            pat = get_pattern(guess, ans)
            if pat not in groups: groups[pat] = []
            groups[pat].append(ans)
            
        # Calculate Expected Score of this guess
        # Sum ( Prob_of_Pattern * Best_Score_in_Next_Turn )
        expected_next_score = 0
        
        for pat, subset in groups.items():
            prob_of_subset = sum(candidate_probs[w] for w in subset)
            
            if pat == (2,2,2,2,2):
                # We won! Value is huge.
                # 100 points matches the scale of our previous utility
                next_step_utility = 100.0 
            else:
                # RECURSION: What is the score of the best move in this new universe?
                # We approximate "Best Move" by running the Greedy Solver on the subset.
                
                # New probabilities for the subset
                sub_total = sum(get_word_mass(w) for w in subset)
                sub_probs = {w: get_word_mass(w)/sub_total for w in subset}
                
                # Find the best greedy score available in this future
                max_greedy_future = 0
                
                # OPTIMIZATION: Only scan the subset itself to save time
                # (Scanning 12,000 words here would be too slow)
                scan_list = subset if len(subset) > 0 else guess_list
                
                for next_guess in scan_list:
                    s = get_greedy_score(next_guess, subset, sub_probs)
                    if s > max_greedy_future: max_greedy_future = s
                
                next_step_utility = max_greedy_future

            expected_next_score += prob_of_subset * next_step_utility
            
        # Note: We do NOT add immediate_p here, because it's captured 
        # in the (2,2,2,2,2) case inside the loop.
        
        if expected_next_score > best_expected_score:
            best_expected_score = expected_next_score
            best_word = guess
            
    return best_word
