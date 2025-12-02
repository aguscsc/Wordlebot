import os
import math
import numpy as np
from numba import njit

# --- 1. CONFIG ---
CENTER = 4.5
WIDTH = 2.0

# --- 2. FAST PATTERN LOGIC (Compiled) ---
@njit
def get_pattern_numba(guess_arr, answer_arr):
    # 0=Gray, 1=Yellow, 2=Green
    result = np.zeros(5, dtype=np.uint8)
    answer_counts = np.zeros(26, dtype=np.uint8)
    
    # Count chars in answer
    for c in answer_arr:
        answer_counts[c] += 1
        
    # Pass 1: Green
    for i in range(5):
        g = guess_arr[i]
        if g == answer_arr[i]:
            result[i] = 2
            answer_counts[g] -= 1
            
    # Pass 2: Yellow
    for i in range(5):
        if result[i] == 2: continue
        g = guess_arr[i]
        if answer_counts[g] > 0:
            result[i] = 1
            answer_counts[g] -= 1
            
    # Convert pattern [2,0,1,0,0] to a single integer hash for fast dictionary keys
    # Base 3 encoding: p[0]*1 + p[1]*3 + ...
    pat_hash = 0
    multiplier = 1
    for i in range(5):
        pat_hash += result[i] * multiplier
        multiplier *= 3
    return pat_hash

# --- 3. HELPER: String <-> Int Conversion ---
def word_to_int_array(word):
    return np.array([ord(c) - 97 for c in word], dtype=np.uint8)

# --- 4. FAST ENTROPY CALCULATION ---
# This is the heavy lifter. It runs in C speed.
@njit
def calculate_entropy_fast(guess_arr, answer_matrix, probability_masses):
    num_answers = len(answer_matrix)
    total_mass = 0.0
    
    # We need a fixed size array for pattern buckets (3^5 = 243 possible patterns)
    pattern_buckets = np.zeros(243, dtype=np.float64)
    
    for i in range(num_answers):
        pat = get_pattern_numba(guess_arr, answer_matrix[i])
        mass = probability_masses[i]
        pattern_buckets[pat] += mass
        total_mass += mass
        
    entropy = 0.0
    for i in range(243):
        mass = pattern_buckets[i]
        if mass > 0:
            p = mass / total_mass
            entropy += p * (-math.log2(p))
            
    return entropy

# --- 5. THE WRAPPER LOGIC ---
WORD_WEIGHTS = {}
LOADED = False
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
LISTS_DIR = os.path.join(PROJECT_ROOT, "lists")

def load_weights(filepath, lists_dir):
    global WORD_WEIGHTS, LOADED
    file = os.path.join(lists_dir, filepath)
    try:
        with open(file, "r") as f:
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
        print("Freq file not found.")

def get_word_mass(word):
    if not LOADED: load_weights("kli_words.txt", LISTS_DIR)
    return WORD_WEIGHTS.get(word, 0.00001)

# Standard Python interface for simulation.py
def get_pattern(guess, answer):
    # We keep the tuple version for compatibility with your existing code
    g = word_to_int_array(guess)
    a = word_to_int_array(answer)
    p_hash = get_pattern_numba(g, a)
    
    # Decode hash back to tuple (0,2,1...)
    res = []
    for _ in range(5):
        res.append(p_hash % 3)
        p_hash //= 3
    return tuple(res)

def update(best_guess, pattern, answers):
    # Keep list comprehension, it's fast enough for filtering
    return [w for w in answers if get_pattern(best_guess, w) == pattern]

def entropy(answers, guess_list):
    # 1. Endgame Shortcut
    if len(answers) <= 2:
        return max(answers, key=get_word_mass)

    # 2. Pre-process Data for Numba
    # Convert strings to numpy arrays ONCE
    answer_matrix = np.array([word_to_int_array(w) for w in answers])
    masses = np.array([get_word_mass(w) for w in answers], dtype=np.float64)
    total_mass = np.sum(masses)
    
    # 3. Calculate Scores
    best_guess = "none"
    max_score = -1.0
    
    # Calculate win probabilities for current candidates
    # Map word -> probability (for the +P part)
    cand_probs = {w: m/total_mass for w, m in zip(answers, masses)}

    for guess in guess_list:
        guess_arr = word_to_int_array(guess)
        
        # Call the compiled function
        ent = calculate_entropy_fast(guess_arr, answer_matrix, masses)
        
        # Add Probability Bonus (Score Addition)
        p_win = cand_probs.get(guess, 0.0)
        
        # Safety Valve logic
        penalty = 0.0
        if ent < 1.0 and p_win < 0.5:
            penalty = 0.5
            
        score = ent + p_win - penalty
        
        if score > max_score:
            max_score = score
            best_guess = guess
            
    return best_guess
