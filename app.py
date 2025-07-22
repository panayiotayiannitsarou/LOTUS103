import streamlit as st
import pandas as pd
import math
from io import BytesIO

from step1_senarios import step1_katanomi_paidia_ekpaideutikon_senarios
from step2 import step2_zoiri_mathites
from step3 import step3_idiaiterotites
from step4 import step4_amivaia_filia
from step5 import step5_filikoi_omades
from step6 import step6_ypolipoi_xwris_filies
from step7 import step7_final_check_and_fix
from utils.excel_export import convert_multiple_dfs_to_excel
from utils.statistics import show_statistics_table, calculate_score_for_all_scenarios

st.set_page_config(page_title="Κατανομή Μαθητών", layout="wide")
st.title("📊 Ψηφιακή Κατανομή Μαθητών Α΄ Δημοτικού")

with st.sidebar:
    st.header("🔐 Όροι Χρήσης & Πρόσβαση")
    password = st.text_input("Κωδικός Πρόσβασης", type="password")
    if password != "katanomi2025":
        st.warning("🔒 Εισάγετε σωστό κωδικό για να προχωρήσετε.")
        st.stop()
    st.success("🔓 Πρόσβαση Εγκεκριμένη")

uploaded_file = st.file_uploader("⬆️ Μεταφόρτωση Excel Μαθητών (Μόνο Πυρήνας)", type=["xlsx"])
num_classes = st.number_input("🔢 Επιλέξτε Αριθμό Τμημάτων", min_value=2, max_value=10, value=2, step=1)

if uploaded_file:
    df = pd.read_excel(uploaded_file)
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

    # 🔽 Κατέβασμα Excel με όλα τα Σενάρια
    excel_all = convert_multiple_dfs_to_excel(st.session_state["scenario_dfs"])
    st.download_button("📥 Κατέβασε Excel με όλα τα Σενάρια", data=excel_all, file_name="ola_ta_senaria.xlsx")

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

    # 🔽 Κατέβασμα Στατιστικών Όλων των Σεναρίων
    stats_df = st.session_state["all_stats_df"]
    stats_buffer = BytesIO()
    with pd.ExcelWriter(stats_buffer, engine="xlsxwriter") as writer:
        stats_df.to_excel(writer, index=False, sheet_name="Στατιστικά")
        stats_buffer.seek(0)
    st.download_button(
        label="📊 Κατέβασε Στατιστικά Όλων των Σεναρίων",
        data=stats_buffer,
        file_name="statistika_ola_senaria.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # 🔽 Κατέβασμα Στατιστικών Καλύτερου Σεναρίου
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
