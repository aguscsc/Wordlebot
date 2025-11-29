import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor


def analyze_bot_logic():
    # 1. Load the Data
    try:
        df = pd.read_csv("bot_decision_data.csv")
    except FileNotFoundError:
        print("Error: Run generate_data.py first!")
        return

    print(f"Loaded {len(df)} decisions for analysis.")

    # 2. Prepare the "Surrogate Model"
    # Features (X): The metrics the bot used
    # Target (y): The result (Lower 'total_game_steps' is better)

    # We filter for turns where the bot actually had a choice (Turn 2+)
    # Turn 1 is hardcoded, so it has no variance to analyze.
    df_filtered = df[df["turn"] > 1]

    X = df_filtered[["entropy_score", "prob_score", "candidates_left", "turn"]]
    y = df_filtered["total_game_steps"]

    # 3. Train the Random Forest
    # This model learns to predict "How fast will I win?" based on Entropy/Prob
    print("Training Random Forest to reverse-engineer success...")
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X, y)

    # 4. Extract Feature Importance (Global XAI)
    importances = rf.feature_importances_
    feature_names = ["entropy_score", "prob_score", "candidates_left", "turn"]

    # 5. Visualize
    plt.figure(figsize=(10, 6))
    plt.barh(feature_names, importances, color="teal")
    plt.xlabel("Importance (Impact on Win Speed)")
    plt.title("XAI Analysis: What actually drives the bot's success?")
    plt.grid(axis="x", alpha=0.3)

    # Add values
    for index, value in enumerate(importances):
        plt.text(value, index, f"{value:.1%}")

    print("\n--- INSIGHTS ---")
    print("If 'prob_score' is higher than 'entropy_score', it means")
    print("Probability Mass was the decisive factor for winning fast.")

    plt.show()


if __name__ == "__main__":
    analyze_bot_logic()
