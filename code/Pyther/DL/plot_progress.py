import pandas as pd
import matplotlib.pyplot as plt

def plot_training_metrics():
    try:
        # Load the log
        df = pd.read_csv("training_log.csv")
    except FileNotFoundError:
        print("No log file found. Run training first!")
        return

    # Calculate Moving Average (Smooths out the noise)
    # Window=50 means "Average of the last 50 data points"
    df['reward_ma'] = df['reward'].rolling(window=20).mean()

    # Create Plot
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # PLOT 1: REWARD (Left Axis, Blue)
    color = 'tab:blue'
    ax1.set_xlabel('Episode')
    ax1.set_ylabel('Reward (Score)', color=color)
    # Plot raw data faintly
    ax1.plot(df['episode'], df['reward'], color=color, alpha=0.2)
    # Plot smooth trend line strongly
    ax1.plot(df['episode'], df['reward_ma'], color=color, linewidth=2, label="Avg Reward")
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, alpha=0.3)

    # PLOT 2: EPSILON (Right Axis, Red)
    ax2 = ax1.twinx()  # Instantiate a second axes that shares the same x-axis
    color = 'tab:red'
    ax2.set_ylabel('Epsilon (Randomness)', color=color)
    ax2.plot(df['episode'], df['epsilon'], color=color, linestyle='--', label="Epsilon")
    ax2.tick_params(axis='y', labelcolor=color)

    # Title & Layout
    plt.title('DQN Training Progress: The Learning Curve')
    fig.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_training_metrics()
