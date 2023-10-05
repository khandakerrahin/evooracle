import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load your CSV file into a DataFrame
df = pd.read_csv("/home/shaker/Documents/Thesis/Writing/data/EO_Final.csv")

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
plt.figure(figsize=(12, 6))
sns.boxplot(x='model', y='total_time', data=df)
plt.title('Box Plot of Total Time by Model')
plt.show()
# plt.savefig("/home/shaker/Documents/Thesis/Writing/data/analysis_figures/total_time_by_model.png")

# Create a box plot for assertion generation time by each model
plt.figure(figsize=(12, 6))
sns.boxplot(x='model', y='assertion_generation_time', data=df)
plt.title('Box Plot of Assertion Generation Time by Model')
plt.show()
# plt.savefig("/home/shaker/Documents/Thesis/Writing/data/analysis_figures/assertion_generation_time_by_model.png")

# Create a box plot for total time taken by each run
plt.figure(figsize=(12, 6))
sns.boxplot(x='run', y='total_time', data=df)
plt.title('Box Plot of Total Time by Run')
plt.show()
# plt.savefig("/home/shaker/Documents/Thesis/Writing/data/analysis_figures/total_time_by_run.png")

# Create a box plot for assertion generation time by each run
plt.figure(figsize=(12, 6))
sns.boxplot(x='run', y='assertion_generation_time', data=df)
plt.title('Box Plot of Assertion Generation Time by Run')
plt.show()
# plt.savefig("/home/shaker/Documents/Thesis/Writing/data/analysis_figures/assertion_generation_time_by_run.png")

# Create a box plot for total time taken by each class
plt.figure(figsize=(16, 6))
sns.boxplot(x='CUT', y='total_time', data=df)
plt.title('Box Plot of Total Time by Class')
plt.xticks(rotation=45, ha='right')
plt.show()
# plt.savefig("/home/shaker/Documents/Thesis/Writing/data/analysis_figures/total_time_by_class.png")

# Create a box plot for assertion generation time by each class
plt.figure(figsize=(16, 6))
sns.boxplot(x='CUT', y='assertion_generation_time', data=df)
plt.title('Box Plot of Assertion Generation Time by Class')
plt.xticks(rotation=45, ha='right')
plt.show()
# plt.savefig("/home/shaker/Documents/Thesis/Writing/data/analysis_figures/assertion_generation_time_by_class.png")

# Question 1: Successful assertion generation
success_counts = df['assertion_generated'].value_counts()
success_counts.plot(kind='bar', title='Assertion Generation Success')
plt.xlabel('Assertion Generated')
plt.ylabel('Count')
plt.show()

# Question 2: Successful assertion generation after 3 attempts
attempts_3_success_counts = df[df['attempts'] <= 3]['assertion_generated'].value_counts()
attempts_3_success_counts.plot(kind='bar', title='Assertion Generation Success (Attempts <= 3)')
plt.xlabel('Assertion Generated')
plt.ylabel('Count')
plt.show()

# Question 3: Successful assertion generation at first attempt
first_attempt_success_counts = df[df['attempts'] == 1]['assertion_generated'].value_counts()
first_attempt_success_counts.plot(kind='bar', title='Assertion Generation Success (First Attempt)')
plt.xlabel('Assertion Generated')
plt.ylabel('Count')
plt.show()

# Question 4: Compare EO with ES for compile and run
eo_compile_run_counts = df.groupby(['eo_is_compiled', 'eo_is_run']).size().unstack(fill_value=0)
es_compile_run_counts = df.groupby(['es_is_compiled', 'es_is_run']).size().unstack(fill_value=0)

# Plotting
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

eo_compile_run_counts.plot(kind='bar', stacked=True, ax=axes[0], title='EO Compilation and Run Status')
axes[0].set_xlabel('Compilation Status')
axes[0].set_ylabel('Count')

es_compile_run_counts.plot(kind='bar', stacked=True, ax=axes[1], title='ES Compilation and Run Status')
axes[1].set_xlabel('Compilation Status')
axes[1].set_ylabel('Count')

plt.show()
