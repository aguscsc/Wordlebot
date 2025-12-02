import torch
import torch.nn as nn
import torch.optim as optim
import random
import os
from collections import deque
from rl import WordleEnv
import csv
import kli_optimized as logic

# --- HYPERPARAMETERS ---
BATCH_SIZE = 512 # Increased for GPU utilization
LR = 0.0001
GAMMA = 0.99
EPSILON_START = 1.0
EPSILON_END = 0.05
EPSILON_DECAY = 0.99998
MEMORY_SIZE = 100000
TARGET_UPDATE = 500
WARMUP = 1000
TOTAL_EPISODES = 200000
TEACHER_RATE = 0.5

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
    start_episode = 1  # Default if no save exists
    logic.load_weights("kli_words.txt",logic.LISTS_DIR)

    # RESUME LOGIC
    if os.path.exists("wordle_dqn.pth"):
        print("Loading existing model...")
        checkpoint = torch.load("wordle_dqn.pth", map_location=device)
        
        # Load weights
        policy_net.load_state_dict(checkpoint['model_state_dict'])
        
        # Load progress
        start_episode = checkpoint['episode'] + 1
        epsilon = checkpoint['epsilon']
        print(f"Resuming from Episode {start_episode}, Epsilon {epsilon:.3f}")

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
    
    # 2. PERFORMANCE TRACKER (Last 1000 games)
    recent_rewards = deque(maxlen=1000)
    
    try:
        for episode in range(start_episode, TOTAL_EPISODES): 
            state = env.reset().to(device)
            total_reward = 0
            current_candidates = list(env.answers)
            teacher_guess = "slate"
            
            # Warmup Period
            if episode < WARMUP:
                epsilon = 1.0

            while True:
                # --- ACTION SELECTION ---
                mask_tensor = torch.tensor(env.guessed_mask, device=device, dtype=torch.bool)
                # Teacher and epsilon logic
                is_exploring = random.random() < epsilon
               
                if is_exploring:
                    if random.random() < TEACHER_RATE:
                        if len(current_candidates)>0:
                            word_choice = logic.entropy(current_candidates, env.full_answers)
                            action_idx = env.word_to_idx[word_choice]
                        else:    
                            valid_indices = (~env.guessed_mask).nonzero()[0]
                            if len(valid_indices) == 0: break 
                            action_idx = random.choice(valid_indices)
                    
                    else:
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

                # --- Update teacher ---
                guess_word = env.idx_to_word[action_idx]
                pat = logic.get_pattern(guess_word, env.target_word)
                current_candidates = logic.update(guess_word, pat, current_candidates)
                
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
            # If we are in Easy Mode and averaging > 50 reward over last 1000 games
            if current_mode == "easy" and avg_reward > 50 and episode > 1000 and epsilon < 0.5:
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
            # Save a DICT containing weights AND metadata
            checkpoint = {
                'model_state_dict': policy_net.state_dict(),
                'episode': episode,
                'epsilon': epsilon
            }
            torch.save(checkpoint, "wordle_dqn.pth")
            print(f"Model Saved at Episode {episode}.")

if __name__ == "__main__":
    train()
