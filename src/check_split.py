import pandas as pd
from sklearn.utils.class_weight import compute_class_weight
import numpy as np

train_file = "data/processed/train.csv"

train = pd.read_csv(
    train_file,
    usecols=["Label"]
)

classes = np.unique(train["Label"])

weights = compute_class_weight(
    class_weight="balanced",
    classes=classes,
    y=train["Label"]
)

class_weights = dict(zip(classes, weights))

print("\nCLASS WEIGHTS\n")

for label, weight in class_weights.items():
    print(f"{label:30} : {weight:.4f}")