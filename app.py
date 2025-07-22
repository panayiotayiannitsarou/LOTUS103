
import streamlit as st
import pandas as pd
import math
from io import BytesIO

from step1_senarios import generate_step1_scenarios
from step2 import step2_zoiri_mathites
from step3 import step3_idiaiterotites
from step4 import step4_amivaia_filia
from step5 import step5_filikoi_omades
from step6 import step6_ypolipoi_xwris_filies
from step7 import step7_final_check_and_fix
from utils.excel_export import convert_multiple_dfs_to_excel
from utils.statistics import show_statistics_table, calculate_score_for_all_scenarios

def reset_session():
    keys_to_clear = [
        "scenario_dfs",
        "all_stats_df",
        "final_df",
        "best_index"
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

st.set_page_config(page_title="Κατανομή Μαθητών", layout="wide")
st.title("📊 Ψηφιακή Κατανομή Μαθητών Α΄ Δημοτικού")

with st.sidebar:
    st.header("🔐 Όροι Χρήσης & Πρόσβαση")
    password = st.text_input("Κωδικός Πρόσβασης", type="password")
    if password != "katanomi2025":
        st.warning("🔒 Εισάγετε σωστό κωδικό για να προχωρήσετε.")
        st.stop()
    st.success("🔓 Πρόσβαση Εγκεκριμένη")

uploaded_file = st.file_uploader("⬆️ Μεταφόρτωση Excel με ΟΛΟΥΣ τους Μαθητές της Α΄ Δημοτικού", type=["xlsx"])

if uploaded_file:
    reset_session()
    df = pd.read_excel(uploaded_file)
    num_classes = math.ceil(len(df) / 25)
    st.info(f"📌 Υπολογίστηκαν αυτόματα **{num_classes} τμήματα** (μέγιστο 25 μαθητές ανά τμήμα)")

    scenarios = step1_katanomi_paidia_ekpaideutikon_senarios(df.copy(), num_classes)

    all_scenario_dfs = []
    all_stats = []

    for i, scenario_df in enumerate(scenarios):
        scenario_df = step2_zoiri_mathites(scenario_df, num_classes)
        scenario_df = step3_idiaiterotites(scenario_df, num_classes)
        scenario_df = step4_amivaia_filia(scenario_df)
        scenario_df = step5_filikoi_omades(scenario_df, num_classes)
        scenario_df = step6_ypolipoi_xwris_filies(scenario_df, num_classes)
        scenario_df = step7_final_check_and_fix(scenario_df, num_classes)
        all_scenario_dfs.append(scenario_df)

        score_df = calculate_score_for_all_scenarios(scenario_df, i+1, num_classes)
        all_stats.append(score_df)

    all_stats_df = pd.concat(all_stats, ignore_index=True)
    best_index = all_stats_df['SCORE'].idxmin()

    st.session_state["scenario_dfs"] = all_scenario_dfs
    st.session_state["all_stats_df"] = all_stats_df
    st.session_state["final_df"] = all_scenario_dfs[best_index]
    st.session_state["best_index"] = best_index

if "final_df" in st.session_state and st.session_state["final_df"] is not None:
    df = st.session_state["final_df"]
    index = st.session_state["best_index"]

    st.success(f"📌 Το πρόγραμμα επέλεξε αυτόματα το **Σενάριο {index + 1}** ως το καλύτερο.")
    st.subheader("🔍 Προεπισκόπηση Κατανομής")
    st.dataframe(df)

    # 🔽 Κατέβασμα μόνο του Καλύτερου Σεναρίου
    final_df = df.copy()
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        final_df.to_excel(writer, index=False, sheet_name='Καλύτερο Σενάριο')
    st.download_button(
        label="📥 Κατέβασμα Excel – Καλύτερο Σενάριο",
        data=output.getvalue(),
        file_name="kalytero_senario_katanomi.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # 🔽 Κατέβασμα Στατιστικών Καλύτερου Σεναρίου
    stats_df = st.session_state["all_stats_df"]
    best_stats = stats_df[stats_df["ΣΕΝΑΡΙΟ"] == index + 1]
    output_stats = BytesIO()
    with pd.ExcelWriter(output_stats, engine='xlsxwriter') as writer:
        best_stats.to_excel(writer, index=False, sheet_name='Στατιστικά Καλύτερου')
    st.download_button(
        label="📊 Κατέβασμα Excel – Στατιστικά Καλύτερου Σεναρίου",
        data=output_stats.getvalue(),
        file_name="statistika_kalyterou_senariou.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # 📊 Προβολή Στατιστικών Πίνακα
    st.subheader("📊 Στατιστικά Κατανομής ανά Τμήμα")
    show_statistics_table(df, num_classes)

    # 🔁 Κουμπί επανεκκίνησης
    st.markdown("---")
    if st.button("🔄 Δοκίμασε νέο αρχείο"):
        reset_session()
        st.experimental_rerun()

    # 📌 Footer με προσωπικό λογότυπο και απόφθεγμα
    st.markdown("---")
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("Screenshot 2025-07-17 170457.png", width=90)
    with col2:
        st.markdown("**Για μια παιδεία που βλέπει το φως σε όλα τα παιδιά**")
    st.markdown("© 2025 • Δημιουργία: Παναγιώτα Γιαννίτσαρου")
