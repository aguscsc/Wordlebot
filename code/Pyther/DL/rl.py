import torch
import numpy as np
import os
import kli_logic as logic 

class WordleEnv:
    def __init__(self):
        # Load data using your existing infrastructure
        logic.load_weights("kli_words.txt", logic.LISTS_DIR)
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        list_dir = os.path.join(os.path.dirname(script_dir), "lists")
        
        with open(os.path.join(list_dir, "word_list.txt"), 'r') as f:
            raw_list = [line.strip().lower() for line in f]
            
        # --- CURRICULUM LEARNING SETUP ---
        # 1. Sort words by Frequency (High to Low) so "Easy Mode" uses common words
        # We use your existing logic.get_word_mass to score them
        raw_list.sort(key=lambda w: logic.get_word_mass(w), reverse=True)
        
        self.full_answers = raw_list          # Hard Mode (2331 words)
        self.easy_answers = raw_list[:100]    # Easy Mode (Top 100 common words)
        
        #sets hard mode on default
        self.answers = self.full_answers 
        # easy mode
        #self.answers = self.easy_answers
            
        # Map words to indices (Indices must align with the FULL list for the Neural Net)
        self.word_to_idx = {w: i for i, w in enumerate(self.full_answers)}
        self.idx_to_word = {i: w for w, i in self.word_to_idx.items()}
        
        self.reset()

    def set_difficulty(self, mode):
        """
        Switch between 'easy' (top 100 words) and 'hard' (all words).
        """
        if mode == "easy":
            print("Environment switched to EASY MODE (Top 100 words)")
            self.answers = self.easy_answers
        else:
            print("Environment switched to HARD MODE (Full Dictionary)")
            self.answers = self.full_answers

    def reset(self):
            import random
            # Pick target from the CURRENT active list (Easy or Hard)
            self.target_word = random.choice(self.answers)
            self.attempts = 0
            self.game_over = False
            
            # Reset State
            self.alphabet_state = np.zeros((26, 4), dtype=np.float32)
            self.alphabet_state[:, 0] = 1.0 
            
            # Reset Mask
            self.guessed_mask = np.zeros(len(self.full_answers), dtype=bool)
            
            # --- THE FIX: ARTIFICIAL CONSTRAINT ---
            # If we are in Easy Mode, force the bot to only pick from the Easy List.
            # We do this by marking all "Hard Words" as ALREADY GUESSED.
            if len(self.answers) < 1000: # Heuristic check for Easy Mode
                # Calculate how many words are in the easy list
                limit = len(self.answers)
                # Mark everything after that limit as "Guessed" (Unavailable)
                self.guessed_mask[limit:] = True 
            # --------------------------------------
            
            return self.get_state()

    def get_state(self):
        return torch.FloatTensor(self.alphabet_state.flatten())

    def step(self, action_idx):
            # Map index back to word using the FULL list logic
            guess = self.idx_to_word[action_idx]
            self.attempts += 1
            self.guessed_mask[action_idx] = True
            
            # 1. CALCULATE INTERMEDIATE REWARD (The "Cookies")
            # Initialize step_reward here!
            step_reward = 0
            
            # We need the pattern to calculate colors
            pattern = logic.get_pattern(guess, self.target_word)
            
            # Check colors and add bonuses
            for i, char in enumerate(guess):
                if pattern[i] == 2:   # Green
                    step_reward += 3  
                elif pattern[i] == 1: # Yellow
                    step_reward += 1  

            # Base penalty for time (-1) plus cookies
            # This means a guess with 2 greens (+6) results in a +5 reward for the step!
            current_step_score = -1 + step_reward

            # 2. WIN CONDITION
            if guess == self.target_word:
                self.game_over = True
                # Huge Win Bonus (100) + The points for the final correct letters
                final_reward = 100 + current_step_score
                return self.get_state(), final_reward, True

            # 3. LOSE CONDITION
            if self.attempts >= 6:
                self.game_over = True
                return self.get_state(), -50, True

            # 4. UPDATE STATE (Neural Net Inputs)
            for i, char in enumerate(guess):
                char_idx = ord(char) - ord('a')
                status = pattern[i] 
                nn_status = status + 1 
                
                self.alphabet_state[char_idx, :] = 0 
                self.alphabet_state[char_idx, nn_status] = 1.0

            # Return state and the calculated intermediate reward
            return self.get_state(), current_step_score, False
