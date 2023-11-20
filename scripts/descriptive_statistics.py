import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import numpy as np

# Load your CSV file into a DataFrame
df = pd.read_csv("/home/shaker/Documents/Thesis/Writing/data/EO_Final_Second.csv")

# Display overall summary statistics
overall_stats = df.describe()

# Display summary statistics by model
model_stats = df.groupby('model').describe()

# Display summary statistics by run
run_stats = df.groupby('run').describe()

# Display summary statistics by class
class_stats = df.groupby('CUT').describe()

# You can continue to break down by other dimensions as needed

# Save these statistics to separate files or visualize them as needed
# overall_stats.to_csv("overall_stats.csv")
# model_stats.to_csv("model_stats.csv")
# # run_stats.to_csv("run_stats.csv")
# class_stats.to_csv("class_stats.csv")

# Set the style of seaborn for better aesthetics
sns.set(style="whitegrid")

# Create a box plot for total time taken by each model
# plt.figure(figsize=(12, 6))
# sns.boxplot(x='model', y='total_time', data=df)
# plt.title('Box Plot of Total Time by Model')
# # plt.show()
# # plt.savefig("/home/shaker/Documents/Thesis/Writing/data/analysis_figures/total_time_by_model.png")

# # Create a box plot for assertion generation time by each model
# plt.figure(figsize=(12, 6))
# sns.boxplot(x='model', y='assertion_generation_time', data=df)
# plt.title('Box Plot of Assertion Generation Time by Model')
# # plt.show()
# # plt.savefig("/home/shaker/Documents/Thesis/Writing/data/analysis_figures/assertion_generation_time_by_model.png")

# # Create a box plot for total time taken by each run
# plt.figure(figsize=(12, 6))
# sns.boxplot(x='run', y='total_time', data=df)
# plt.title('Box Plot of Total Time by Run')
# # plt.show()
# # plt.savefig("/home/shaker/Documents/Thesis/Writing/data/analysis_figures/total_time_by_run.png")

# # Create a box plot for assertion generation time by each run
# plt.figure(figsize=(12, 6))
# sns.boxplot(x='run', y='assertion_generation_time', data=df)
# plt.title('Box Plot of Assertion Generation Time by Run')
# # plt.show()
# # plt.savefig("/home/shaker/Documents/Thesis/Writing/data/analysis_figures/assertion_generation_time_by_run.png")

# # Create a box plot for total time taken by each class
# plt.figure(figsize=(16, 6))
# sns.boxplot(x='CUT', y='total_time', data=df)
# plt.title('Box Plot of Total Time by Class')
# plt.xticks(rotation=45, ha='right')
# # plt.show()
# # plt.savefig("/home/shaker/Documents/Thesis/Writing/data/analysis_figures/total_time_by_class.png")

# # Create a box plot for assertion generation time by each class
# plt.figure(figsize=(16, 6))
# sns.boxplot(x='CUT', y='assertion_generation_time', data=df)
# plt.title('Box Plot of Assertion Generation Time by Class')
# plt.xticks(rotation=45, ha='right')
# # plt.show()
# # plt.savefig("/home/shaker/Documents/Thesis/Writing/data/analysis_figures/assertion_generation_time_by_class.png")

# # Question 1: Successful assertion generation
# success_counts = df['assertion_generated'].value_counts()
# success_counts.plot(kind='bar', title='Assertion Generation Success')
# plt.xlabel('Assertion Generated')
# plt.ylabel('Count')
# # plt.show()

# # Question 2: Successful assertion generation after 3 attempts
# attempts_3_success_counts = df[df['attempts'] <= 3]['assertion_generated'].value_counts()
# attempts_3_success_counts.plot(kind='bar', title='Assertion Generation Success (Attempts <= 3)')
# plt.xlabel('Assertion Generated')
# plt.ylabel('Count')
# # plt.show()

# # Question 3: Successful assertion generation at first attempt
# first_attempt_success_counts = df[df['attempts'] == 1]['assertion_generated'].value_counts()
# first_attempt_success_counts.plot(kind='bar', title='Assertion Generation Success (First Attempt)')
# plt.xlabel('Assertion Generated')
# plt.ylabel('Count')
# # plt.show()

# # Question 4: Compare EO with ES for compile and run
# eo_compile_run_counts = df.groupby(['eo_is_compiled', 'eo_is_run']).size().unstack(fill_value=0)
# es_compile_run_counts = df.groupby(['es_is_compiled', 'es_is_run']).size().unstack(fill_value=0)

# # Plotting
# fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# eo_compile_run_counts.plot(kind='bar', stacked=True, ax=axes[0], title='EO Compilation and Run Status')
# axes[0].set_xlabel('Compilation Status')
# axes[0].set_ylabel('Count')

# es_compile_run_counts.plot(kind='bar', stacked=True, ax=axes[1], title='ES Compilation and Run Status')
# axes[1].set_xlabel('Compilation Status')
# axes[1].set_ylabel('Count')

# plt.show()

# Assertion patterns
assertion_patterns = [
    r'(\w+\.)?assert\s*\(.+?\);',
    r'(\w+\.)?assertTrue\s*\(.+?\);',
    r'(\w+\.)?assertNull\s*\(.+?\);',
    r'(\w+\.)?fail\s*\(.+?\);',
    r'(\w+\.)?assertFalse\s*\(.+?\);',
    r'(\w+\.)?assertNotEquals\s*\(.+?\);',
    r'(\w+\.)?assertEquals\s*\(.+?\);',
    r'(\w+\.)?assertArrayEquals\s*\(.+?\);',
    r'(\w+\.)?assertNotNull\s*\(.+?\);',
    r'(\w+\.)?assertNotSame\s*\(.+?\);',
    r'(\w+\.)?assertSame\s*\(.+?\);',
    r'(\w+\.)?assertThat\s*\(.+?\);',
]

# Labels for each assertion pattern
assertion_labels = [
    'assert',
    'assertTrue',
    'assertNull',
    'fail',
    'assertFalse',
    'assertNotEquals',
    'assertEquals',
    'assertArrayEquals',
    'assertNotNull',
    'assertNotSame',
    'assertSame',
    'assertThat',
]

# Filter rows where assertion is generated
generated_assertions_df = df[df['assertion_generated']]

# Count occurrences of each pattern in es_assertion
pattern_counts_es = {label: 0 for label in assertion_labels}
pattern_counts_eo = {label: 0 for label in assertion_labels}

# Count occurrences of each pattern in es_assertion and eo_assertion
for _, row in generated_assertions_df.iterrows():
    es_pattern = str(row['es_assertion'])  # Ensure it's a string
    eo_pattern = str(row['eo_assertion'])  # Ensure it's a string

    for pattern, label in zip(assertion_patterns, assertion_labels):
        if re.fullmatch(pattern, es_pattern):
            pattern_counts_es[label] += 1
            if re.fullmatch(pattern, eo_pattern):
                pattern_counts_eo[label] += 1

# Sort patterns by counts
sorted_patterns_es = sorted(pattern_counts_es.items(), key=lambda x: x[1], reverse=True)
sorted_labels_es, sorted_counts_es = zip(*sorted_patterns_es)

sorted_patterns_eo = sorted(pattern_counts_eo.items(), key=lambda x: x[1], reverse=True)
sorted_labels_eo, sorted_counts_eo = zip(*sorted_patterns_eo)

bar_width = 0.35
bar_positions_es = np.arange(len(sorted_patterns_es))
bar_positions_eo = bar_positions_es + bar_width

# Normalize counts
normalized_counts_es = np.array(sorted_counts_es) / sum(sorted_counts_es)
normalized_counts_eo = np.array(sorted_counts_eo) / sum(sorted_counts_eo)

# Plotting
fig, ax = plt.subplots(figsize=(15, 6))

# Plot bars for es_assertion counts
ax.bar(bar_positions_es, normalized_counts_es, width=bar_width, label='EvoSuite Assertions', color='blue')

# Plot bars for eo_assertion counts
ax.bar(bar_positions_eo, normalized_counts_eo, width=bar_width, label='EvoOracle Assertions', color='orange')

ax.set_xticks(bar_positions_es + bar_width / 2)
ax.set_xticklabels(sorted_labels_es, rotation=45, ha='right')
ax.set_xlabel('Assertions')
ax.set_ylabel('Normalized Count')
ax.set_title('Testing APIs Breakdown Distribution')

ax.legend()
plt.tight_layout()
plt.show()