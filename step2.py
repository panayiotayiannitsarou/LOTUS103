
import pandas as pd
import numpy as np
from collections import defaultdict

def step2_zoiri_mathites(df, num_classes):
    df = df.copy()
    df["ΖΩΗΡΟΣ"] = df["ΖΩΗΡΟΣ"].fillna("")
    df["ΦΥΛΟ"] = df["ΦΥΛΟ"].fillna("")
    df["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = df["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"].fillna("")
    df["ΤΜΗΜΑ"] = df["ΤΜΗΜΑ"].fillna("")

    # Αρχικά: ζωηροί μαθητές
    zoiroi = df[df["ΖΩΗΡΟΣ"] == "Ν"]
    zoiroi_not_assigned = zoiroi[zoiroi["ΤΜΗΜΑ"] == ""]

    # Υπολογισμός ζωηρών που έχουν ήδη τοποθετηθεί
    zoiroi_assigned = zoiroi[zoiroi["ΤΜΗΜΑ"] != ""]
    class_zoiroi_count = defaultdict(int)
    for _, row in zoiroi_assigned.iterrows():
        class_zoiroi_count[row["ΤΜΗΜΑ"]] += 1

    # Χαρτογράφηση φίλων και συγκρούσεων
    filia_map = defaultdict(set)
    for _, row in df.iterrows():
        if pd.notna(row["ΦΙΛΙΑ"]):
            filoi = [x.strip() for x in str(row["ΦΙΛΙΑ"]).split(",")]
            for f in filoi:
                filia_map[row["ΟΝΟΜΑ"]].add(f)

    sygkrousi_map = defaultdict(set)
    for _, row in df.iterrows():
        if pd.notna(row["ΣΥΓΚΡΟΥΣΗ"]):
            conflict = [x.strip() for x in str(row["ΣΥΓΚΡΟΥΣΗ"]).split(",")]
            for s in conflict:
                sygkrousi_map[row["ΟΝΟΜΑ"]].add(s)

    # Τρέχον φορτίο τμημάτων
    class_members = defaultdict(list)
    for _, row in df[df["ΤΜΗΜΑ"] != ""].iterrows():
        class_members[row["ΤΜΗΜΑ"]].append(row["ΟΝΟΜΑ"])

    class_names = [f"Τμήμα {i+1}" for i in range(num_classes)]
    for name in class_names:
        class_zoiroi_count[name] += 0
        class_members[name] += []

    # Τοποθέτηση ζωηρών που δεν έχουν ακόμη τοποθετηθεί
    for _, row in zoiroi_not_assigned.iterrows():
        name = row["ΟΝΟΜΑ"]
        fylo = row["ΦΥΛΟ"]
        idiaiterotita = row["ΙΔΙΑΙΤΕΡΟΤΗΤΑ"]
        best_class = None
        best_score = float("inf")

        for cname in class_names:
            score = 0

            # 1. Ισοποση κατανομή ζωηρών
            score += class_zoiroi_count[cname] * 10

            # 2. Εξωτερικές συγκρούσεις
            for m in class_members[cname]:
                if m in sygkrousi_map[name]:
                    score += 100

            # 3. Παιδαγωγικές συγκρούσεις
            for m in class_members[cname]:
                m_row = df[df["ΟΝΟΜΑ"] == m].iloc[0]
                if (
                    (m_row["ΖΩΗΡΟΣ"] == "Ν" and row["ΖΩΗΡΟΣ"] == "Ν")
                    or (m_row["ΙΔΙΑΙΤΕΡΟΤΗΤΑ"] == "Ν" and idiaiterotita == "Ν")
                    or (
                        (m_row["ΖΩΗΡΟΣ"] == "Ν" and idiaiterotita == "Ν")
                        or (row["ΖΩΗΡΟΣ"] == "Ν" and m_row["ΙΔΙΑΙΤΕΡΟΤΗΤΑ"] == "Ν")
                    )
                ):
                    score += 50

            # 4. Πλήρως αμοιβαίες φιλίες
            for friend in filia_map[name]:
                if (
                    friend in class_members[cname]
                    and name in filia_map[friend]
                ):
                    score -= 5

            # 5. Ισορροπία φύλου
            same_gender_count = sum(
                1 for m in class_members[cname] if df[df["ΟΝΟΜΑ"] == m].iloc[0]["ΦΥΛΟ"] == fylo
            )
            score += same_gender_count * 2

            if score < best_score:
                best_score = score
                best_class = cname

        df.loc[df["ΟΝΟΜΑ"] == name, "ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"] = best_class
        df.loc[df["ΟΝΟΜΑ"] == name, "ΤΜΗΜΑ"] = best_class
        class_members[best_class].append(name)
        class_zoiroi_count[best_class] += 1

    return df
