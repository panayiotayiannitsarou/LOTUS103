import pandas as pd
from collections import Counter
from itertools import combinations


def evaluate_population_balance(df):
    counts = df['ΤΜΗΜΑ'].value_counts()
    max_size = counts.max()
    min_size = counts.min()
    diff = max_size - min_size
    if diff > 2:
        return None
    elif diff == 2:
        return 2
    elif diff == 1:
        return 1
    return 0


def evaluate_conflicts(df):
    score = 0
    grouped = df.groupby('ΤΜΗΜΑ')
    for _, group in grouped:
        names = group['ΟΝΟΜΑ'].tolist()
        conflict_dict = dict(zip(group['ΟΝΟΜΑ'], group['ΣΥΓΚΡΟΥΣΗ']))
        for a, b in combinations(names, 2):
            if conflict_dict.get(a) == b or conflict_dict.get(b) == a:
                score += 10
    return score


def evaluate_pedagogical_conflicts(df):
    score = 0
    grouped = df.groupby('ΤΜΗΜΑ')
    for _, group in grouped:
        flags = group[['ΟΝΟΜΑ', 'ΖΩΗΡΟΣ', 'ΙΔΙΑΙΤΕΡΟΤΗΤΑ']].set_index('ΟΝΟΜΑ')
        for a, b in combinations(flags.index, 2):
            z1, i1 = flags.loc[a]
            z2, i2 = flags.loc[b]
            if (z1 == 'Ν' and z2 == 'Ν') or (i1 == 'Ν' and i2 == 'Ν') or ((z1 == 'Ν' and i2 == 'Ν') or (z2 == 'Ν' and i1 == 'Ν')):
                score += 3
    return score


def evaluate_broken_friendships(df):
    score = 0
    friend_map = dict(zip(df['ΟΝΟΜΑ'], df['ΦΙΛΟΙ']))
    class_map = dict(zip(df['ΟΝΟΜΑ'], df['ΤΜΗΜΑ']))
    for name, friends in friend_map.items():
        if pd.isna(friends) or name not in class_map:
            continue
        for friend in str(friends).split(','):
            friend = friend.strip()
            if friend in class_map and class_map[friend] != class_map[name]:
                if name in str(friend_map.get(friend, '')).split(','):
                    score += 5
    return score


def evaluate_gender_balance(df):
    score = 0
    grouped = df.groupby('ΤΜΗΜΑ')['ΦΥΛΟ'].value_counts().unstack().fillna(0)
    if 'Α' in grouped.columns and 'Κ' in grouped.columns:
        diffs = abs(grouped['Α'] - grouped['Κ'])
        for diff in diffs:
            if diff > 3:
                score += int(diff - 3)
    return score


def evaluate_language_balance(df):
    score = 0
    grouped = df.groupby('ΤΜΗΜΑ')['ΓΛΩΣΣΑ'].value_counts().unstack().fillna(0)
    if 'Ν' in grouped.columns and 'Ο' in grouped.columns:
        diffs = abs(grouped['Ν'] - grouped['Ο'])
        for diff in diffs:
            if diff > 3:
                score += int(diff - 3)
    return score


def evaluate_scenario(df):
    score = 0

    population_score = evaluate_population_balance(df)
    if population_score is None:
        return None
    score += population_score

    score += evaluate_conflicts(df)
    score += evaluate_pedagogical_conflicts(df)
    score += evaluate_broken_friendships(df)
    score += evaluate_gender_balance(df)
    score += evaluate_language_balance(df)

    return score
