import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import os

# --- CONFIG ---
FILES_TO_CHECK = ["bot_decision_data.csv"]

def calculate_rf_weights():
    # 1. Load Data
    df = None
    for fname in FILES_TO_CHECK:
        if os.path.exists(fname):
            try:
                df = pd.read_csv(fname)
                break
            except: continue
    
    if df is None:
        print("Error: No data found. Run generate_dataset.py first.")
        return

    # Detect Target Column
    target_col = 'result_turns' if 'result_turns' in df.columns else 'total_game_steps'

    # 2. Define Stages
    stages = [
        ("EARLY GAME (>100 words)", df[df['candidates_left'] > 100]),
        ("MID GAME (10-100 words)",  df[(df['candidates_left'] <= 100) & (df['candidates_left'] > 10)]),
        ("END GAME (<10 words)",    df[df['candidates_left'] <= 10])
    ]

    print(f"{'STAGE':<25} | {'ENTROPY IMP':<15} | {'PROB IMP':<15} | {'REC. WEIGHTS (E:P)'}")
    print("-" * 75)

    for name, subset in stages:
        if len(subset) < 10:
            print(f"{name:<25} | Not enough data")
            continue

        X = subset[['entropy_score', 'prob_score']]
        y = subset[target_col]

        # 3. Train Random Forest (The "Judge")
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf.fit(X, y)

        # 4. Extract Importances
        imps = rf.feature_importances_
        imp_ent = imps[0]
        imp_prob = imps[1]

        # 5. Normalize to create clean weights summing to 1.0
        # (Random Forest importances already sum to 1, but we do this to be safe)
        total = imp_ent + imp_prob
        if total == 0: total = 1
        
        w_ent = imp_ent / total
        w_prob = imp_prob / total

        print(f"{name:<25} | {w_ent:.4f}          | {w_prob:.4f}        | {w_ent:.2f} : {w_prob:.2f}")

if __name__ == "__main__":
    calculate_rf_weights()
