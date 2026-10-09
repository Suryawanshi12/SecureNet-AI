import pandas as pd
from sklearn.utils.class_weight import compute_class_weight
import numpy as np

train_file = "data/processed/train.csv"

# Read only labels
train = pd.read_csv(
    train_file,
    usecols=["Label"]
)

# Find all classes
classes = np.unique(train["Label"])

# Calculate normal balanced weights
weights = compute_class_weight(
    class_weight="balanced",
    classes=classes,
    y=train["Label"]
)

# Create dictionary
class_weights = dict(zip(classes, weights))

# Maximum allowed weight
MAX_WEIGHT = 50

# Cap the weights
capped_weights = {
    label: min(weight, MAX_WEIGHT)
    for label, weight in class_weights.items()
}

print("\nCAPPED CLASS WEIGHTS\n")

for label, weight in capped_weights.items():
    print(f"{label:30} : {weight:.4f}")