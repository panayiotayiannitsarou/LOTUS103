import streamlit as st
import pandas as pd
import math
from io import BytesIO
from step1_senarios import generate_step1_scenarios
from step2 import step2_katanomi_zoiroi
from step3 import step3_katanomi_idiaiterotites
from step4 import step4_katanomi_filia
from step5 import step5_omadopoihsh_katigories, step5_katanomi_omadon_se_tmimata
from step6 import step6_ypolipoi_xwris_filies
from step7 import step7_final_check_and_fix
from helpers.evaluation import evaluate_scenario

def reset_session():
    keys_to_clear = [
        "scenario_index",
        "scenario_dfs",
        "scenario_scores",
        "final_df",
        "all_stats_df",
        "best_index",
        "df_katanomes"
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]



def convert_multiple_dfs_to_excel(scenario_dfs):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        for i, df in enumerate(scenario_dfs):
            df.to_excel(writer, index=False, sheet_name=f"Σενάριο {i+1}")
    output.seek(0)
    return output

st.set_page_config(page_title="Κατανομή Μαθητών", layout="wide")
st.sidebar.title("🛡️ Όροι Χρήσης & Πνευματικά Δικαιώματα")
with st.sidebar.expander("📃 Προβολή Όρων"):
    st.markdown("""**© 2025 Παναγιώτα Γιαννίτσαρου – Όλα τα δικαιώματα διατηρούνται.**

    Η χρήση της παρούσας εφαρμογής προϋποθέτει την αποδοχή των εξής όρων:

    - Απαγορεύεται η αντιγραφή, τροποποίηση ή διανομή του λογισμικού χωρίς έγγραφη άδεια της δημιουργού.
    - Η εφαρμογή προστατεύεται από τη νομοθεσία περί πνευματικής ιδιοκτησίας.
    - Οποιαδήποτε μη εξουσιοδοτημένη χρήση διώκεται νομικά.""")
accepted = st.sidebar.checkbox("✅ Αποδέχομαι τους παραπάνω όρους")
if not accepted:
    st.warning("Για να συνεχίσετε, πρέπει να αποδεχτείτε τους όρους χρήσης.")
    st.stop()

password = st.sidebar.text_input("🔐 Εισάγετε τον κωδικό πρόσβασης:", type="password")
if password != "katanomi2025":
    st.warning("Παρακαλώ εισάγετε έγκυρο κωδικό για πρόσβαση στην εφαρμογή.")
    st.stop()

enable_app = st.sidebar.checkbox("✅ Ενεργοποίηση Εφαρμογής", value=True)
if not enable_app:
    st.info("🔒 Η εφαρμογή είναι προσωρινά απενεργοποιημένη.")
    st.stop()

st.title("🎯 Ψηφιακή Κατανομή Μαθητών Α΄ Δημοτικού")

if "scenario_index" not in st.session_state:
    st.session_state["scenario_index"] = 0
if "scenario_dfs" not in st.session_state:
    st.session_state["scenario_dfs"] = None
if "final_df" not in st.session_state:
    st.session_state["final_df"] = None

uploaded_file = st.file_uploader("📥 Εισαγωγή Αρχείου Excel Μαθητών", type=["xlsx"])
if uploaded_file:
    reset_session()
    if st.session_state.get("final_df") is not None:
        st.stop()
    # Αρχική επεξεργασία
    df_initial = pd.read_excel(uploaded_file)
    st.success("✅ Το αρχείο ανέβηκε επιτυχώς!")
    num_classes = math.ceil(len(df_initial) / 25)
    scenarios = generate_step1_scenarios(df_initial, num_classes)

    best_score = float("inf")
    best_index = 0
    processed_scenarios = []
    all_stats = []

    for i, s_df in enumerate(scenarios):
        df = s_df.copy()
        df["ΚΛΕΙΔΩΜΕΝΟΣ"] = False
        df = step2_katanomi_zoiroi(df, num_classes)
        df = step3_katanomi_idiaiterotites(df, num_classes)
        df = step4_katanomi_filia(df)
        categories, _ = step5_omadopoihsh_katigories(df)
        df = step5_katanomi_omadon_se_tmimata(df, categories, num_classes)
        df = step6_ypolipoi_xwris_filies(df, num_classes)
        df, warnings, success = step7_final_check_and_fix(df, num_classes)
        if not success:
            continue
        df["ΤΜΗΜΑ"] = df["ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ"]
        score = evaluate_scenario(df, num_classes)
        processed_scenarios.append((df, score, warnings))

        # Προσθήκη στατιστικών για προεπισκόπηση
        for j in range(num_classes):
            class_id = f"Τμήμα {j+1}"
            class_df = df[df["ΤΜΗΜΑ"] == class_id]
            total = class_df.shape[0]
            stats = {
                "ΣΕΝΑΡΙΟ": i+1,
                "ΤΜΗΜΑ": class_id,
                "ΑΓΟΡΙΑ": (class_df["ΦΥΛΟ"] == "Α").sum(),
                "ΚΟΡΙΤΣΙΑ": (class_df["ΦΥΛΟ"] == "Κ").sum(),
                "ΠΑΙΔΙΑ_ΕΚΠΑΙΔΕΥΤΙΚΩΝ": (class_df["ΠΑΙΔΙ ΕΚΠΑΙΔΕΥΤΙΚΟΥ"] == "Ν").sum(),
                "ΖΩΗΡΟΙ": (class_df["ΖΩΗΡΟΣ"] == "Ν").sum(),
                "ΙΔΙΑΙΤΕΡΟΤΗΤΕΣ": (class_df["ΙΔΙΑΙΤΕΡΟΤΗΤΑ"] == "Ν").sum(),
                "ΚΑΛΗ_ΓΝΩΣΗ_ΕΛΛΗΝΙΚΩΝ": (class_df["ΚΑΛΗ ΓΝΩΣΗ ΕΛΛΗΝΙΚΩΝ"] == "Ν").sum(),
                "ΣΥΝΟΛΟ": total,
                "SCORE": round(score, 3)
            }
            all_stats.append(stats)

        if score < best_score:
            best_score = score
            best_index = i


    # ➕ Έλεγχος αν υπάρχουν ισοβαθμίες
    all_scores = [s[1] for s in processed_scenarios]
    min_score = min(all_scores)
    tied_indices = [i for i, s in enumerate(all_scores) if s == min_score]
    if len(tied_indices) > 1:
        st.info(f"⚖️ {len(tied_indices)} σενάρια είχαν την ίδια χαμηλότερη βαθμολογία ({min_score}). Επιλέχθηκε το πρώτο.")    
    if not processed_scenarios:
        st.error("⛔ Κανένα σενάριο δεν ικανοποίησε τους περιορισμούς κατανομής.")
        st.stop()

    st.session_state["scenario_dfs"] = [s[0] for s in processed_scenarios]
    st.session_state["scenario_scores"] = [s[1] for s in processed_scenarios]
    st.session_state["final_df"] = processed_scenarios[best_index][0]
    st.session_state["all_stats_df"] = pd.DataFrame(all_stats)
    st.session_state["best_index"] = best_index

if st.session_state["final_df"] is not None:
    df = st.session_state["final_df"]
    index = st.session_state["best_index"]
    st.success(f"📌 Το πρόγραμμα επέλεξε αυτόματα το **Σενάριο {index + 1}** ως το καλύτερο.")
    st.subheader("🔍 Προεπισκόπηση Κατανομής")
    st.dataframe(df)

    excel_all = convert_multiple_dfs_to_excel(st.session_state["scenario_dfs"])
    st.download_button("📦 Κατέβασε Excel με όλα τα Σενάρια", data=excel_all, file_name="ola_ta_senaria.xlsx")

    st.subheader("📊 Σύγκριση Στατιστικών για Όλα τα Σενάρια")
    st.dataframe(st.session_state["all_stats_df"])

# ➕ Επιπλέον κουμπί για κατέβασμα στατιστικών
# Προσθήκη κουμπιού για κατέβασμα αρχείου με στατιστικά
stats_df = st.session_state["all_stats_df"]
stats_buffer = BytesIO()
with pd.ExcelWriter(stats_buffer, engine="xlsxwriter") as writer:
    stats_df.to_excel(writer, index=False, sheet_name="Στατιστικά")
stats_buffer.seek(0)

st.download_button(
    label="📊 Κατέβασε Στατιστικά Όλων των Σεναρίων",
    data=stats_buffer,

# 🔄 Κουμπί: Δοκίμασε νέο αρχείο
st.markdown("---")
if st.button("🔄 Δοκίμασε νέο αρχείο"):
    reset_session()
    st.experimental_rerun()


# 📥 Κατέβασμα μόνο του καλύτερου σεναρίου σε Excel
if 'final_df' in st.session_state:
    final_df = st.session_state['final_df'].copy()
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        final_df.to_excel(writer, index=False, sheet_name='Καλύτερο Σενάριο')
    st.download_button(
        label="📥 Κατέβασμα Excel – Καλύτερο Σενάριο",
        data=output.getvalue(),
        file_name="kalytero_senario_katanomi.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


#


# 📊 Κατέβασμα Excel – Στατιστικά μόνο για το καλύτερο σενάριο
if 'all_stats_df' in st.session_state and 'best_index' in st.session_state:
    best_stats = st.session_state['all_stats_df']
    best_stats = best_stats[best_stats["ΣΕΝΑΡΙΟ"] == st.session_state['best_index'] + 1]
    output_stats = BytesIO()
    with pd.ExcelWriter(output_stats, engine='xlsxwriter') as writer:
        best_stats.to_excel(writer, index=False, sheet_name='Στατιστικά Καλύτερου')
    st.download_button(
        label="📊 Κατέβασμα Excel – Στατιστικά Καλύτερου Σεναρίου",
        data=output_stats.getvalue(),
        file_name="statistika_kalyterou_senariou.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


#


# 📌 Footer με προσωπικό λογότυπο και απόφθεγμα
st.markdown("---")
col1, col2 = st.columns([1, 5])
with col1:
    st.image("Screenshot 2025-07-17 170457.png", width=90)
with col2:
    st.markdown("**Για μια παιδεία που βλέπει το φως σε όλα τα παιδιά**  
© 2025 • Δημιουργία: Παναγιώτα Γιαννίτσαρου")