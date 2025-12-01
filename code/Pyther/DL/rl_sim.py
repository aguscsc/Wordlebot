import torch
import torch.nn as nn
import numpy as np
import os
import time
from tqdm import tqdm
from rl import WordleEnv

# --- 1. DEFINE THE BRAIN (Must match training exactly) ---
class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 512)
        self.fc2 = nn.Linear(512, 512)
        self.fc3 = nn.Linear(512, output_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

def run_rl_simulation(num_games="ALL"):
    # 1. Setup Environment & Device
    env = WordleEnv()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Running Inference on: {device}")

    # 2. Load the Trained Model
    n_actions = len(env.answers)
    model = DQN(104, n_actions).to(device)
    
    model_path = "wordle_dqn.pth"
    if not os.path.exists(model_path):
        print("Error: 'wordle_dqn.pth' not found. Train the model first!")
        return

    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval() # Set to evaluation mode (turns off dropout/batchnorm behavior)
    print("Model loaded successfully.")

    # 3. Determine Targets
    if num_games == "ALL":
        targets = env.answers # Deterministic full run
    else:
        import random
        targets = [random.choice(env.answers) for _ in range(int(num_games))]

    scores = []
    fails = 0
    start_time = time.time()

    # 4. The Game Loop
    for target in tqdm(targets, desc="RL Agent Playing"):
        # Reset Env manually for this specific target
        # (We hack the env slightly to force a specific target)
        env.reset()
        env.target_word = target 
        
        state = env.get_state().to(device)
        
        for t in range(1, 7):
            # --- INTELLIGENT MOVE ---
            with torch.no_grad():
                # 1. Get raw scores for all 2331 words
                q_values = model(state.unsqueeze(0)) 
                
                # 2. MASKING: Don't guess words we already guessed
                # Set q-values of guessed words to Negative Infinity
                invalid_mask = torch.tensor(env.guessed_mask, dtype=torch.bool).to(device)
                q_values[0, invalid_mask] = -float('inf')
                
                # 3. GREEDY SELECTION: Pick the highest score
                action_idx = q_values.argmax().item()
            
            # --- EXECUTE ---
            next_state, reward, done = env.step(action_idx)
            state = next_state.to(device)
            
            if done:
                # Check if we won
                guess = env.idx_to_word[action_idx]
                if guess == target:
                    scores.append(t)
                else:
                    scores.append(7) # Fail
                    fails += 1
                break
        else:
            # If loop finishes without 'break', we failed (reached 6 turns)
            if not done: 
                scores.append(7)
                fails += 1

    # 5. Stats
    avg = sum(scores) / len(scores)
    end_time = time.time()
    
    print("\n" + "="*30)
    print(f"RL AGENT PERFORMANCE")
    print(f"Average Guesses: {avg:.4f}")
    print(f"Fail Rate: {fails}/{len(targets)} ({fails/len(targets):.1%})")
    print(f"Time Taken: {end_time - start_time:.2f} seconds")
    print("="*30)

if __name__ == "__main__":
    # Choose "ALL" for full benchmark, or 100 for a quick check
    run_rl_simulation("ALL")
