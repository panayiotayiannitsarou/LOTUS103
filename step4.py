
import pandas as pd

def step4_katanomi_filikes_sxeseis(df):
    df = df.copy()

    # Εντοπισμός μη τοποθετημένων μαθητών
    df_not_assigned = df[df["ΤΜΗΜΑ"].isna()]

    for idx, row in df_not_assigned.iterrows():
        student_name = row["ΟΝΟΜΑ"]
        friend_name = row["ΦΙΛΙΑ"]

        # Έλεγχος αν ο φίλος είναι πλήρως αμοιβαίος και ήδη τοποθετημένος
        if friend_name in df["ΟΝΟΜΑ"].values:
            friend_row = df[df["ΟΝΟΜΑ"] == friend_name].iloc[0]
            if friend_row["ΦΙΛΙΑ"] == student_name and pd.notna(friend_row["ΤΜΗΜΑ"]):
                df.at[idx, "ΤΜΗΜΑ"] = friend_row["ΤΜΗΜΑ"]

    return df
