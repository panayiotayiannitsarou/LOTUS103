
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

from itertools import permutations
import pandas as pd
import math

def generate_step1_scenarios(df, num_classes):
    df = df.copy()
    names = df[df["ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ"] == "Ν"]["ΟΝΟΜΑ"].tolist()

    # ✅ Επιστροφή κενής λίστας αν δεν υπάρχουν παιδιά εκπαιδευτικών
    if len(names) == 0:
        return []

    base_df = df.copy()
    scenarios = []

    # Δημιουργία όλων των πιθανών κατανομών
    min_repeats = math.ceil(len(names) / num_classes)
    class_indices = [i % num_classes for i in range(len(names))]
    all_perms = set(permutations(class_indices))

    for perm in all_perms:
        temp_df = base_df.copy()
        for name, class_index in zip(names, perm):
            temp_df.loc[temp_df["ΟΝΟΜΑ"] == name, "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = f"Α{class_index+1}"
            temp_df.loc[temp_df["ΟΝΟΜΑ"] == name, "ΠΗΓΗ"] = "ΒΗΜΑ 1"
        scenarios.append(temp_df)

    return scenarios

