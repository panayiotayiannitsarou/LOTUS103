
import pandas as pd
from collections import Counter

def step6_ypolipoi_xwris_filies(df, num_classes):
    df = df.copy()
    tmimata = [f"Α{i+1}" for i in range(num_classes)]
    
    # Υπόλοιποι μαθητές χωρίς πλήρως αμοιβαία φιλία και χωρίς τοποθέτηση
    unplaced_students = df[df["ΤΜΗΜΑ"].isna() & (df["ΦΙΛΙΑ"].isna() | (df["ΦΙΛΙΑ"].str.strip() == ""))]

    for _, row in unplaced_students.iterrows():
        # Υπολογισμός αριθμού μαθητών ανά τμήμα
        current_counts = df["ΤΜΗΜΑ"].value_counts().reindex(tmimata, fill_value=0).to_dict()

        # Βρες τα τμήματα με τους λιγότερους μαθητές
        min_count = min(current_counts.values())
        candidate_classes = [t for t in tmimata if current_counts[t] == min_count]

        # Αν υπάρχουν περισσότερα από ένα, έλεγξε για ισορροπία φύλου
        if len(candidate_classes) > 1:
            gender = row["ΦΥΛΟ"]
            gender_counts = {t: len(df[(df["ΤΜΗΜΑ"] == t) & (df["ΦΥΛΟ"] == gender)]) for t in candidate_classes}
            best_class = min(gender_counts, key=gender_counts.get)
        else:
            best_class = candidate_classes[0]

        # Τοποθέτηση μαθητή
        df.loc[df["ΟΝΟΜΑ"] == row["ΟΝΟΜΑ"], "ΤΜΗΜΑ"] = best_class

    return df
