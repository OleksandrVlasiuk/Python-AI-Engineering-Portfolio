# ==============================================================================
# CHAID DECISION TREE ALGORITHM (FROM SCRATCH)
# Implementation of the Chi-squared Automatic Interaction Detection algorithm
# applied to a consumer electronics (Laptop) purchase dataset.
# ==============================================================================

import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

# --- 1. Dataset Initialization ---
data = {
    'Age':            ['Young', 'Young', 'Middle', 'Old',    'Old',  'Old', 'Middle',  'Young'],
    'Income':         ['High',  'High',  'High',   'Medium', 'Low',  'Low', 'Low',     'Medium'],
    'Credit_History': ['Bad',   'Good',  'Bad',    'Bad',    'Good', 'Bad', 'Bad',     'Good'],
    'Bought_Laptop':  ['No',    'Yes',   'Yes',    'Yes',    'No',   'Yes', 'No',      'Yes']
}

df = pd.DataFrame(data)

# --- 2. Categorical Data Encoding ---
# Convert categorical string variables into numerical codes for mathematical processing
category_map = {}
for col in ['Age', 'Income', 'Credit_History']:
    df[col] = df[col].astype('category')
    category_map[col] = df[col].cat.categories
    df[col] = df[col].cat.codes

# Transform target variable and isolate input features
y = df['Bought_Laptop'].astype('category').cat.codes  
X = df.drop(columns=['Bought_Laptop'])  

# --- 3. Statistical Testing Function ---
def chi_square_test(feature, target):
    """Calculates the Chi-Square statistic and p-value for a given feature."""
    observed = pd.crosstab(feature, target)
    chi2, p, dof, expected = chi2_contingency(observed)
    print(f"  Chi-Square for feature '{feature.name}': {chi2:.4f}, p-value: {p:.4f}")
    return chi2

# --- 4. Core Algorithm Implementation ---
class CHAIDTree:
    """Chi-square based Decision Tree Classifier."""
    def __init__(self, max_depth=3):
        self.max_depth = max_depth
        self.tree = None

    def fit(self, X, y):
        self.tree = self._build_tree(X, y, depth=0)

    def _build_tree(self, X, y, depth):
        # Stop conditions: maximum depth reached or node is completely pure
        if depth >= self.max_depth or len(np.unique(y)) == 1:
            return np.bincount(y).argmax()

        best_feature = None
        best_chi2 = -1
        best_split = None

        print(f"\nStep {depth + 1}:")

        for feature in X.columns:
            print(f"  Evaluating feature: {feature}")
            chi2_value = chi_square_test(X[feature], y)
            if chi2_value > best_chi2:
                best_chi2 = chi2_value
                best_feature = feature
                best_split = X[feature]

        if best_feature is None:
            return np.bincount(y).argmax()

        print(f"  Best feature for splitting: {best_feature} with Chi-Square = {best_chi2:.4f}")

        tree = {best_feature: {}}
        used_categories = set()

        for category in np.unique(best_split):
            if category not in used_categories:
                sub_X = X[best_split == category]
                sub_y = y[best_split == category]
                
                # If all target values are identical, return the class without further splitting
                if len(np.unique(sub_y)) == 1:
                    tree[best_feature][category] = np.unique(sub_y)[0]
                else:
                    print(f"  Branching sub-nodes for category: {category_map[best_feature][category]}")
                    tree[best_feature][category] = self._build_tree(sub_X, sub_y, depth + 1)
                used_categories.add(category)

        return tree

    def predict(self, X):
        return X.apply(lambda row: self._predict_row(row, self.tree), axis=1)

    def _predict_row(self, row, tree):
        if isinstance(tree, dict):
            feature = list(tree.keys())[0]
            category = row[feature]
            return self._predict_row(row, tree[feature].get(category, np.bincount(y).argmax()))
        return tree

    def print_tree(self):
        self._print_tree(self.tree)

    def _print_tree(self, tree, depth=0, parent=""):
        if isinstance(tree, dict):
            for feature, branches in tree.items():
                print(f"{'  ' * depth}{feature}?")
                for category, subtree in branches.items():
                    category_name = category_map[feature][category]
                    if depth == 0:
                        print(f"{'  ' * (depth + 1)}├── {category_name} → ", end="")
                    else:
                        print(f"{'  ' * (depth + 1)}└── {category_name} → ", end="")
                    self._print_tree(subtree, depth + 2, category_name)
        else:
            # Print the final leaf node classification immediately
            print(f"{'  ' * depth}{['No', 'Yes'][tree]}")


# --- 5. Model Execution & Evaluation ---

# Instantiate and train the CHAID tree
chaid_tree = CHAIDTree(max_depth=2)
chaid_tree.fit(X, y)

# Output the learned tree topology
print("\nDecision Tree Topology:")
chaid_tree.print_tree()

# Category Mapping Legend
print("\nCategory Encodings:")
for col in ['Age', 'Income', 'Credit_History']:
    print(f"{col}:")
    for idx, category in enumerate(category_map[col]):
        print(f"  {idx} -> {category}")

# Execute Predictions
y_pred = chaid_tree.predict(X)

print("\nModel Predictions:")
for i, (pred, row) in enumerate(zip(y_pred, df[['Age', 'Income', 'Credit_History']].values)):
    age, income, credit = row  # Retrieve original numerical categories
    age_category = category_map['Age'][age]
    income_category = category_map['Income'][income]
    credit_category = category_map['Credit_History'][credit]
    print(f"Index {i}: Age={age_category}, Income={income_category}, Credit_History={credit_category} -> Prediction: {'Yes' if pred == 1 else 'No'}")