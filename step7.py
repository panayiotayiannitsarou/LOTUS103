
from typing import List, Tuple
import pandas as pd

def step7_check_balance_and_correct(df: pd.DataFrame, num_classes: int) -> Tuple[pd.DataFrame, List[str]]:
    warnings = []
    df = df.copy()

    # Μαρκάρισμα "κλειδωμένων" μαθητών (προηγούμενα βήματα)
    df['locked'] = df['ΠΗΓΗ'].isin(['ΒΗΜΑ 1', 'ΒΗΜΑ 2', 'ΒΗΜΑ 3', 'ΒΗΜΑ 4'])

    # Συνάρτηση ανταλλαγής για κάθε χαρακτηριστικό
    def attempt_swap(col):
        counts = df.groupby('ΤΜΗΜΑ')[col].value_counts().unstack().fillna(0)
        if len(counts.columns) < 2:
            return
        major_cat = counts.columns[0]
        minor_cat = counts.columns[1]
        diffs = counts[major_cat] - counts[minor_cat]
        if diffs.abs().max() <= 3:
            return

        over_class = diffs.idxmax()
        under_class = diffs.idxmin()

        from_over = df[(df['ΤΜΗΜΑ'] == over_class) & (df[col] == major_cat) & (~df['locked'])]
        from_under = df[(df['ΤΜΗΜΑ'] == under_class) & (df[col] == minor_cat) & (~df['locked'])]

        if not from_over.empty and not from_under.empty:
            idx_over = from_over.index[0]
            idx_under = from_under.index[0]
            df.at[idx_over, 'ΤΜΗΜΑ'] = under_class
            df.at[idx_under, 'ΤΜΗΜΑ'] = over_class
        else:
            warnings.append(f"⚠️ Δεν κατέστη δυνατή η ανταλλαγή για ισορροπία {col}")

    # Ανταλλαγές για ΦΥΛΟ και ΓΛΩΣΣΑ
    attempt_swap('ΦΥΛΟ')
    attempt_swap('ΓΛΩΣΣΑ')

    # Έλεγχος πληθυσμιακής ισορροπίας
    class_sizes = df.groupby('ΤΜΗΜΑ').size().reindex(range(1, num_classes + 1), fill_value=0)
    max_students = class_sizes.max()
    min_students = class_sizes.min()
    diff = max_students - min_students

    if max_students > 25:
        warnings.append(f"❌ Κάποιο τμήμα έχει πάνω από 25 μαθητές ({max_students})")
    if diff > 2:
        warnings.append(f"❌ Η διαφορά πληθυσμού μεταξύ τμημάτων υπερβαίνει τους 2 ({diff})")

    # Προειδοποιήσεις για ποιοτικές αποκλίσεις
    for col, label in [('ΦΥΛΟ', 'Φύλου'), ('ΓΛΩΣΣΑ', 'Γλώσσας')]:
        counts = df.groupby('ΤΜΗΜΑ')[col].value_counts().unstack().fillna(0)
        if counts.shape[1] < 2:
            continue
        major_cat = counts.columns[0]
        minor_cat = counts.columns[1]
        diffs = abs(counts[major_cat] - counts[minor_cat])
        if diffs.max() > 3:
            warnings.append(f"⚠️ Υπάρχει απόκλιση >3 στο χαρακτηριστικό {label}")

    return df.drop(columns='locked'), warnings
