import pandas as pd
import itertools
import copy
from collections import defaultdict

def fully_mutual_friends(df):
    """
    Επιστρέφει ένα λεξικό όπου για κάθε παιδί εμφανίζονται οι πλήρως αμοιβαίοι φίλοι του.
    """
    mutual = defaultdict(list)
    names = df["ΟΝΟΜΑ"].tolist()
    friends_dict = dict(zip(df["ΟΝΟΜΑ"], df["ΦΙΛΟΙ"]))
    for name in names:
        declared_friends = [f.strip() for f in str(friends_dict.get(name, "")).split(",") if f.strip() in names]
        for friend in declared_friends:
            friends_of_friend = [f.strip() for f in str(friends_dict.get(friend, "")).split(",") if f.strip() in names]
            if name in friends_of_friend:
                mutual[name].append(friend)
    return dict(mutual)

def check_conflicts(pair, df):
    """
    Επιστρέφει True αν υπάρχει εξωτερική ή παιδαγωγική σύγκρουση στο ζεύγος
    """
    df = df.set_index("ΟΝΟΜΑ")
    p1, p2 = pair

    # Εξωτερική σύγκρουση
    conflict_1 = str(df.loc[p1, "ΣΥΓΚΡΟΥΣΗ"]).split(',') if pd.notna(df.loc[p1, "ΣΥΓΚΡΟΥΣΗ"]) else []
    conflict_2 = str(df.loc[p2, "ΣΥΓΚΡΟΥΣΗ"]).split(',') if pd.notna(df.loc[p2, "ΣΥΓΚΡΟΥΣΗ"]) else []
    if p2 in [c.strip() for c in conflict_1] or p1 in [c.strip() for c in conflict_2]:
        return True

    # Παιδαγωγική σύγκρουση
    def is_zoiros(x): return str(df.loc[x, "ΖΩΗΡΟΣ"]).strip().upper() == 'Ν'
    def is_idiaterotita(x): return str(df.loc[x, "ΙΔΙΑΙΤΕΡΟΤΗΤΑ"]).strip().upper() == 'Ν'

    if (is_zoiros(p1) and is_zoiros(p2)) or (is_idiaterotita(p1) and is_idiaterotita(p2)) or \
       (is_zoiros(p1) and is_idiaterotita(p2)) or (is_zoiros(p2) and is_idiaterotita(p1)):
        return True

    return False

def step1_teacher_scenarios(df, num_classes):
    df = df.copy()
    df["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = ""

    teachers_kids = df[df["ΠΑΙΔΙ_ΕΚΠΑΙΔΕΥΤΙΚΟΥ"] == "Ν"]["ΟΝΟΜΑ"].tolist()
    all_names = df["ΟΝΟΜΑ"].tolist()

    if len(teachers_kids) <= num_classes:
        # Τοποθέτηση ένα παιδί ανά τμήμα χωρίς σενάρια
        for i, name in enumerate(teachers_kids):
            df.loc[df["ΟΝΟΜΑ"] == name, "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = f"Α{i+1}"
        return [df]

    mutual = fully_mutual_friends(df)

    # Γεννήτρια για όλα τα σενάρια ισόποσης κατανομής
    valid_scenarios = []
    for perm in set(itertools.permutations(range(num_classes) * ((len(teachers_kids) + num_classes - 1) // num_classes), len(teachers_kids))):
        if max([perm.count(i) for i in range(num_classes)]) - min([perm.count(i) for i in range(num_classes)]) > 1:
            continue

        temp_df = df.copy()
        scenario = {}
        used = set()
        for i, name in enumerate(teachers_kids):
            class_id = f"Α{perm[i]+1}"
            scenario[name] = class_id

        # Έλεγχος για σύγκρουση
        pairs = list(itertools.combinations(scenario.items(), 2))
        skip = False
        for (n1, c1), (n2, c2) in pairs:
            if c1 == c2:
                if check_conflicts((n1, n2), df):
                    skip = True
                    break
        if skip:
            continue

        # Αν όλα καλά, καταγραφή σεναρίου
        for name, class_id in scenario.items():
            temp_df.loc[temp_df["ΟΝΟΜΑ"] == name, "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = class_id

        # Κρατάμε μόνο μοναδικά σενάρια (κανονικοποίηση κατά περιεχόμενο τμημάτων)
        class_sets = tuple(sorted([tuple(sorted(temp_df[temp_df["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] == f"Α{i+1}"]["ΟΝΟΜΑ"].tolist())) for i in range(num_classes)]))
        if class_sets not in [tuple(sorted([tuple(sorted(v[v["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] == f"Α{i+1}"]["ΟΝΟΜΑ"].tolist())) for i in range(num_classes)])) for v in valid_scenarios]:
            valid_scenarios.append(temp_df)

    return valid_scenarios
