import pandas as pd
import joblib
from xgboost import XGBClassifier


# ============================================================
# 1. LOAD BALANCED TRAINING DATA
# ============================================================

print("Loading training data...")

df = pd.read_csv(
    "data/processed/train_balanced.csv",
    low_memory=False
)

print("Data loaded!")
print("Rows:", len(df))
print("Columns:", len(df.columns))


# ============================================================
# 2. SEPARATE FEATURES AND TARGET
# ============================================================

X = df.drop(
    columns=["Label"]
)

y = df["Label"]

print("\nFeatures:", X.shape)
print("Target:", y.shape)


# ============================================================
# 3. CHECK CLASS DISTRIBUTION
# ============================================================

print("\nClass distribution:")

print(
    y.value_counts().sort_index()
)


# ============================================================
# 4. CREATE XGBOOST MODEL
# ============================================================

print("\nCreating XGBoost model...")

model = XGBClassifier(
    objective="multi:softprob",
    num_class=15,

    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,

    subsample=0.8,
    colsample_bytree=0.8,

    tree_method="hist",

    eval_metric="mlogloss",

    random_state=42,
    n_jobs=-1
)


# ============================================================
# 5. TRAIN MODEL
# ============================================================

print("\nTraining model...")

# No class weights in this experiment
model.fit(
    X,
    y
)

print("\nTraining completed!")


# ============================================================
# 6. SAVE MODEL
# ============================================================

model_path = "models/xgboost_ids_model.pkl"

joblib.dump(
    model,
    model_path
)

print("\nModel saved to:")
print(model_path)


# ============================================================
# 7. FINISHED
# ============================================================

print("\n======================================")
print("XGBOOST TRAINING COMPLETED!")
print("======================================")