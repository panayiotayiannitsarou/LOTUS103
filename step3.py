
import pandas as pd

def step3_katanomi_idiaiterotites(df: pd.DataFrame, num_classes: int) -> pd.DataFrame:
    df = df.copy()

    # Εξασφάλιση κενών τιμών
    df['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] = df['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'].fillna("ΟΧΙ")
    df['ΖΩΗΡΟΣ'] = df['ΖΩΗΡΟΣ'].fillna("ΟΧΙ")
    df['ΤΜΗΜΑ'] = df['ΤΜΗΜΑ'].fillna("")
    df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'].fillna("")

    # Επιλογή παιδιών με ΙΔΙΑΙΤΕΡΟΤΗΤΑ = Ν
    idiaitera = df[df['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == "Ν"]

    # Υφιστάμενα ζωηρά παιδιά ήδη τοποθετημένα
    zoiri_df = df[(df['ΖΩΗΡΟΣ'] == "Ν") & (df['ΤΜΗΜΑ'] != "")]
    zoiri_count_per_class = zoiri_df['ΤΜΗΜΑ'].value_counts().to_dict()

    # Παιδιά με ιδιαιτερότητα ήδη τοποθετημένα
    already_placed = idiaitera[
        (idiaitera['ΤΜΗΜΑ'] != "") | (idiaitera['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] != "")
    ]
    to_place = idiaitera.drop(already_placed.index)

    # Κατάταξη τμημάτων από αυτά με λιγότερους ζωηρούς
    class_priority = sorted(
        list(range(1, num_classes + 1)),
        key=lambda x: zoiri_count_per_class.get(str(x), 0)
    )

    # Καταγραφή υπαρχόντων παιδιών με ιδιαιτερότητες ανά τμήμα
    current_idiaitera_counts = already_placed.apply(
        lambda row: row['ΤΜΗΜΑ'] if row['ΤΜΗΜΑ'] else row['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'], axis=1
    ).value_counts().to_dict()

    # Τοποθέτηση νέων παιδιών
    for _, row in to_place.iterrows():
        sorted_classes = sorted(
            class_priority,
            key=lambda x: (
                current_idiaitera_counts.get(str(x), 0),
                zoiri_count_per_class.get(str(x), 0)
            )
        )

        for class_num in sorted_classes:
            class_str = str(class_num)
            conflict = False

          classmates_ids = classmates['ΟΝΟΜΑ'].tolist()
...
df.loc[df['ΟΝΟΜΑ'] == row['ΟΝΟΜΑ'], ...] = ...

            classmates_ids = classmates['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'].tolist()

            # Έλεγχος εξωτερικής σύγκρουσης
            if any(conflict_name.strip() in classmates_ids for conflict_name in str(row.get("ΣΥΓΚΡΟΥΣΗ", "")).split(",")):
                continue

            # Έλεγχος παιδαγωγικής σύγκρουσης
            for _, cm in classmates.iterrows():
                if (cm['ΖΩΗΡΟΣ'] == "Ν" and row['ΖΩΗΡΟΣ'] == "Ν") or                    (cm['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == "Ν" and row['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == "Ν") or                    (cm['ΖΩΗΡΟΣ'] == "Ν" and row['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == "Ν") or                    (cm['ΙΔΙΑΙΤΕΡΟΤΗΤΑ'] == "Ν" and row['ΖΩΗΡΟΣ'] == "Ν"):
                    conflict = True
                    break

            if not conflict:
                df.loc[df['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'] == row['ΟΝΟΜΑΤΕΠΩΝΥΜΟ'], 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = class_str
                current_idiaitera_counts[class_str] = current_idiaitera_counts.get(class_str, 0) + 1
                break

    return df
