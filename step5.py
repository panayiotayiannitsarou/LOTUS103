
import pandas as pd
from collections import defaultdict

def step5_omadopoihsh_kai_katanomi(df, num_classes):
    df = df.copy()
    df['ΦΙΛΟΙ'] = df['ΦΙΛΙΑ'].fillna('').apply(lambda x: [f.strip() for f in str(x).split(',') if f.strip()])
    df['ΤΜΗΜΑ'] = df['ΤΜΗΜΑ'].fillna('')
    df['ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = df.get('ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ', '')

    # === Βήμα 1: Δημιουργία πλήρως αμοιβαίων ομάδων από μη τοποθετημένους ===
    unplaced_students = df[df['ΤΜΗΜΑ'] == '']
    friendship_graph = defaultdict(set)

    for _, row in unplaced_students.iterrows():
        name = row['ΟΝΟΜΑ']
        for friend in row['ΦΙΛΟΙ']:
            if friend in df['ΟΝΟΜΑ'].values:
                friend_row = df[df['ΟΝΟΜΑ'] == friend].iloc[0]
                if name in friend_row['ΦΙΛΟΙ']:
                    friendship_graph[name].add(friend)
                    friendship_graph[friend].add(name)

    visited = set()
    groups = []

    def dfs(student, group):
        visited.add(student)
        group.append(student)
        for neighbor in friendship_graph[student]:
            if neighbor not in visited:
                dfs(neighbor, group)

    for student in friendship_graph:
        if student not in visited:
            group = []
            dfs(student, group)
            if len(group) <= 3:
                groups.append(group)

    # === Βήμα 2: Κατηγοριοποίηση Ομάδων ===
    categories = defaultdict(list)
    for group in groups:
        members = df[df['ΟΝΟΜΑ'].isin(group)]
        genders = members['ΦΥΛΟ'].unique()
        greek_levels = members['ΓΝΩΣΗ_ΕΛ'].unique()

        if len(genders) > 1:
            cat = 'Μικτού Φύλου'
        elif len(greek_levels) == 1:
            if genders[0] == 'Α':
                cat = 'Καλή Γνώση (Αγόρια)' if greek_levels[0] == 'Ν' else 'Όχι Καλή Γνώση (Αγόρια)'
            else:
                cat = 'Καλή Γνώση (Κορίτσια)' if greek_levels[0] == 'Ν' else 'Όχι Καλή Γνώση (Κορίτσια)'
        else:
            cat = 'Μικτής Γνώσης (Ομάδες Αγoριών)' if genders[0] == 'Α' else 'Μικτής Γνώσης (Ομάδες Κοριτσιών)'

        categories[cat].append(group)

    # === Βήμα 3: Υπολογισμός υπάρχουσας κατανομής ανά κατηγορία ===
    placed_students = df[df['ΤΜΗΜΑ'] != '']
    placed_counts = {i: defaultdict(int) for i in range(num_classes)}
    for _, row in placed_students.iterrows():
        gender = row['ΦΥΛΟ']
        greek = row['ΓΝΩΣΗ_ΕΛ']
        if greek == 'Ν':
            cat = 'Καλή Γνώση (Αγόρια)' if gender == 'Α' else 'Καλή Γνώση (Κορίτσια)'
        elif greek == 'Ο':
            cat = 'Όχι Καλή Γνώση (Αγόρια)' if gender == 'Α' else 'Όχι Καλή Γνώση (Κορίτσια)'
        else:
            continue
        class_index = int(str(row['ΤΜΗΜΑ']).replace('Α', '')) - 1
        placed_counts[class_index][cat] += 1

    # === Βήμα 4: Τοποθέτηση Ομάδων με ισοκατανομή ===
    for cat, cat_groups in categories.items():
        for idx, group in enumerate(cat_groups):
            best_class = min(range(num_classes), key=lambda x: placed_counts[x][cat])
            for student in group:
                df.loc[df['ΟΝΟΜΑ'] == student, 'ΠΡΟΤΕΙΝΟΜΕΝΟ_ΤΜΗΜΑ'] = f'Α{best_class + 1}'
                placed_counts[best_class][cat] += 1

    return df, groups, categories
