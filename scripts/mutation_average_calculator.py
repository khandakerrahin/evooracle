import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# Read the CSV
df = pd.read_csv('/home/shaker/Documents/Thesis/Writing/data/EO_Mutation_Score_second_run.csv')

# Group by 'class' and 'model', and calculate the average
grouped_df = df.groupby(['class', 'model']).agg({
    'eo_test_count': 'mean',
    'eo_line_coverage_score': 'mean',
    'eo_mutation_coverage_score': 'mean',
    'eo_test_strength_score': 'mean'
}).reset_index()

# Write the results to another CSV
grouped_df.to_csv('/home/shaker/Documents/Thesis/Writing/data/EO_mutation_score_second_run_mean.csv', index=False)


# # Group by 'class' and 'model', and calculate the average, median, maximum, and minimum
# grouped_df = df.groupby(['class', 'model']).agg({
#     'eo_test_count': 'mean',
#     'eo_line_coverage_score': ['mean', 'median', 'max', 'min'],
#     'eo_mutation_coverage_score': ['mean', 'median', 'max', 'min'],
#     'eo_test_strength_score': ['mean', 'median', 'max', 'min']
# }).reset_index()

# # Flatten the multi-level column names
# grouped_df.columns = [' '.join(col).strip() for col in grouped_df.columns.values]

# # Write the results to another CSV
# grouped_df.to_csv('/home/shaker/Documents/Thesis/Writing/data/EO_mutation_score_mean_median_max_min.csv', index=False)

# # Set 'class' and 'model' as the index for better plotting
# # grouped_df.set_index(['class', 'model'], inplace=True)

# # Set the style for seaborn
# sns.set(style="whitegrid")

# # Create a bar plot for maximum values
# plt.figure(figsize=(16, 8))
# bar_plot_max = sns.barplot(x='class', y='eo_test_strength_score max', hue='model', data=grouped_df, palette='viridis')
# bar_plot_max.set_xticklabels(bar_plot_max.get_xticklabels(), rotation=45, horizontalalignment='right')
# bar_plot_max.set_title('Maximum Test Strength by Class and Model')
# bar_plot_max.set_xlabel('Class')
# bar_plot_max.set_ylabel('Maximum Test Strength Score')
# bar_plot_max.legend(title='Model')
# plt.tight_layout()
# plt.show()

# # Create a bar plot for minimum values
# plt.figure(figsize=(16, 8))
# bar_plot_min = sns.barplot(x='class', y='eo_test_strength_score min', hue='model', data=grouped_df, palette='viridis')
# bar_plot_min.set_xticklabels(bar_plot_min.get_xticklabels(), rotation=45, horizontalalignment='right')
# bar_plot_min.set_title('Minimum Test Strength by Class and Model')
# bar_plot_min.set_xlabel('Class')
# bar_plot_min.set_ylabel('Minimum Test Strength Score')
# bar_plot_min.legend(title='Model')
# plt.tight_layout()
# plt.show()

# # Create a bar plot for median values
# plt.figure(figsize=(16, 8))
# bar_plot_median = sns.barplot(x='class', y='eo_test_strength_score median', hue='model', data=grouped_df, palette='viridis')
# bar_plot_median.set_xticklabels(bar_plot_median.get_xticklabels(), rotation=45, horizontalalignment='right')
# bar_plot_median.set_title('Median Test Strength by Class and Model')
# bar_plot_median.set_xlabel('Class')
# bar_plot_median.set_ylabel('Median Test Strength Score')
# bar_plot_median.legend(title='Model')
# plt.tight_layout()
# plt.show()