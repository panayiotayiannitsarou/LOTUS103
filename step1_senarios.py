
import pandas as pd
from itertools import permutations
from collections import Counter

def check_conflicts(df, class_col):
    """Ελέγχει αν υπάρχει σύγκρουση ανάμεσα σε παιδιά εκπαιδευτικών στο ίδιο τμήμα"""
    conflicts = []

    teacher_children = df[df["ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ"] == "Ν"]
    grouped = teacher_children.groupby(class_col)

    for _, group in grouped:
        names = group["ΟΝΟΜΑ"].tolist()
        traits = group[["ΟΝΟΜΑ", "ΖΩΗΡΟΣ", "ΙΔΙΑΙΤΕΡΟΤΗΤΑ"]].set_index("ΟΝΟΜΑ").to_dict("index")

        # Έλεγχος σύγκρουσης μεταξύ των παιδιών του ίδιου τμήματος
        for i in range(len(names)):
            for j in range(i+1, len(names)):
                n1, n2 = names[i], names[j]
                trait1, trait2 = traits[n1], traits[n2]

                # Παιδαγωγική σύγκρουση: και οι δύο ζωηροί, ή και οι δύο με ιδιαιτερότητα, ή ένας με ζωηρότητα και ο άλλος με ιδιαιτερότητα
                cond1 = trait1["ΖΩΗΡΟΣ"] == "Ν" and trait2["ΖΩΗΡΟΣ"] == "Ν"
                cond2 = trait1["ΙΔΙΑΙΤΕΡΟΤΗΤΑ"] == "Ν" and trait2["ΙΔΙΑΙΤΕΡΟΤΗΤΑ"] == "Ν"
                cond3 = (trait1["ΖΩΗΡΟΣ"] == "Ν" and trait2["ΙΔΙΑΙΤΕΡΟΤΗΤΑ"] == "Ν") or                         (trait2["ΖΩΗΡΟΣ"] == "Ν" and trait1["ΙΔΙΑΙΤΕΡΟΤΗΤΑ"] == "Ν")

                if cond1 or cond2 or cond3:
                    conflicts.append((n1, n2, "Παιδαγωγική σύγκρουση"))

        # Έλεγχος εξωτερικών συγκρούσεων από στήλη "ΣΥΓΚΡΟΥΣΗ"
        for name in names:
            conflict_with = df.loc[df["ΟΝΟΜΑ"] == name, "ΣΥΓΚΡΟΥΣΗ"].values[0]
            if pd.notna(conflict_with) and conflict_with in names:
                conflicts.append((name, conflict_with, "Δηλωμένη εξωτερική σύγκρουση"))

    return conflicts

def generate_step1_scenarios(df, num_classes):
    df = df.copy()
    teacher_kids = df[df["ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ"] == "Ν"]
    others = df[df["ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ"] != "Ν"]
    names = teacher_kids["ΟΝΟΜΑ"].tolist()

    all_valid_scenarios = []

    # Υποψήφιες κατανομές (όλες οι πιθανές σειρές ανάθεσης)
    for perm in permutations(range(num_classes) * ((len(names) + num_classes - 1) // num_classes), len(names)):
        if max(Counter(perm).values()) - min(Counter(perm).values()) > 1:
            continue  # αποφυγή ανισοκατανομής >1

        df_temp = df.copy()
        mapping = dict(zip(names, perm))
        df_temp["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = df_temp["ΟΝΟΜΑ"].map(mapping)

        # Έλεγχος για συγκρούσεις
        conflicts = check_conflicts(df_temp, "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ")
        if not conflicts:
            all_valid_scenarios.append(df_temp)

    return all_valid_scenarios
