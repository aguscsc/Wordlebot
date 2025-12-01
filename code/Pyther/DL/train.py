import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np
import os
import sys
from collections import deque
from rl import WordleEnv
import csv

# --- HYPERPARAMETERS ---
BATCH_SIZE = 512 # Increased for GPU utilization
LR = 0.0001
GAMMA = 0.99
EPSILON_START = 1.0
EPSILON_END = 0.05
EPSILON_DECAY = 0.99998
MEMORY_SIZE = 100000
TARGET_UPDATE = 500


# --- THE BRAIN ---
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

def train():
    # --- SETUP ---
    EPSILON_START = 1.0
    env = WordleEnv()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on: {device}")

    n_actions = len(env.answers)
    
    policy_net = DQN(104, n_actions).to(device)
    
    # RESUME LOGIC
    if os.path.exists("wordle_dqn.pth"):
        print("Loading existing model...")
        try:
            policy_net.load_state_dict(torch.load("wordle_dqn.pth", map_location=device))
            EPSILON_START = 0.1 
        except:
            print("Model corrupted. Starting fresh.")

    target_net = DQN(104, n_actions).to(device)
    target_net.load_state_dict(policy_net.state_dict())
    
    optimizer = optim.Adam(policy_net.parameters(), lr=LR)
    memory = deque(maxlen=MEMORY_SIZE)
    epsilon = EPSILON_START

    # LOGGING
    log_file = open("training_log.csv", "w", newline="")
    logger = csv.writer(log_file)
    logger.writerow(["episode", "reward", "epsilon", "mode"]) # Added 'mode' to logs
    
    print("Starting Training Loop...")
    
    # 1. START IN EASY MODE
    env.set_difficulty("easy")
    current_mode = "easy"
    
    # 2. PERFORMANCE TRACKER (Last 100 games)
    recent_rewards = deque(maxlen=100)
    
    try:
        for episode in range(1, 200001): 
            state = env.reset().to(device)
            total_reward = 0
            
            # Warmup Period
            if episode < 1000:
                epsilon = 1.0

            while True:
                # --- ACTION SELECTION ---
                mask_tensor = torch.tensor(env.guessed_mask, device=device, dtype=torch.bool)
                
                if random.random() < epsilon:
                    valid_indices = (~env.guessed_mask).nonzero()[0]
                    if len(valid_indices) == 0: break 
                    action_idx = random.choice(valid_indices)
                else:
                    with torch.no_grad():
                        q_values = policy_net(state.unsqueeze(0))
                        q_values[0, mask_tensor] = -float('inf')
                        action_idx = q_values.argmax().item()

                # --- STEP ---
                next_state, reward, done = env.step(action_idx)
                next_state = next_state.to(device)
                total_reward += reward
                
                # --- MEMORY ---
                memory.append((state, action_idx, reward, next_state, done))
                state = next_state
                
                # --- OPTIMIZATION ---
                if len(memory) > BATCH_SIZE:
                    batch = random.sample(memory, BATCH_SIZE)
                    states, actions, rewards, next_states, dones = zip(*batch)
                    
                    states_t = torch.stack(states)
                    actions_t = torch.tensor(actions, device=device).unsqueeze(1)
                    rewards_t = torch.tensor(rewards, device=device, dtype=torch.float)
                    next_states_t = torch.stack(next_states)
                    dones_t = torch.tensor(dones, device=device, dtype=torch.float)
                    
                    current_q = policy_net(states_t).gather(1, actions_t).squeeze(1)
                    
                    with torch.no_grad():
                        next_q = target_net(next_states_t).max(1)[0]
                        target_q = rewards_t + (GAMMA * next_q * (1 - dones_t))
                        
                    loss = nn.MSELoss()(current_q, target_q)
                    
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()

                if done:
                    break
            
            # --- END OF EPISODE UPDATES ---
            
            # 1. Update Decay
            if epsilon > EPSILON_END:
                epsilon *= EPSILON_DECAY
            
            # 2. Update Target Net
            if episode % TARGET_UPDATE == 0:
                target_net.load_state_dict(policy_net.state_dict())
            
            # 3. TRACK CURRICULUM PROGRESS
            recent_rewards.append(total_reward)
            avg_reward = sum(recent_rewards) / len(recent_rewards) if recent_rewards else 0
            
            # --- AUTO-PROMOTION LOGIC ---
            # If we are in Easy Mode and averaging > 50 reward over last 100 games
            if current_mode == "easy" and avg_reward > 50 and episode > 1000:
                print(f"\n>>> GRADUATION! Bot mastered Easy Mode (Avg: {avg_reward:.2f}). Switching to HARD MODE. <<<")
                env.set_difficulty("hard")
                current_mode = "hard"
                # Optional: Reset epsilon slightly to help it adjust to the harder words
                epsilon = max(epsilon, 0.2) 
            
            # 4. LOGGING
            if episode % 100 == 0:
                print(f"Ep {episode} | Avg: {avg_reward:.1f} | Eps: {epsilon:.3f} | Mode: {current_mode}")
                logger.writerow([episode, avg_reward, epsilon, current_mode])
                log_file.flush()

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    
    finally:
        print("Saving Model...")
        torch.save(policy_net.state_dict(), "wordle_dqn.pth")
        print("Model Saved.")
        log_file.close()

if __name__ == "__main__":
    train()
