import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Read the CSV
df = pd.read_csv('/home/shaker/Documents/Thesis/Writing/data/EO_mutation_score_second_run_median.csv')

# Set the style for seaborn
sns.set(style="whitegrid")

# Create a bar plot
plt.figure(figsize=(16, 8))  # Adjust the figure size
bar_plot = sns.barplot(x='class', y='eo_mutation_coverage_score', hue='model', data=df, palette='viridis')
bar_plot.set_xticklabels(bar_plot.get_xticklabels(), rotation=45, horizontalalignment='right')  # Rotate x-axis labels

# Customize the plot
bar_plot.set_title('Median Mutation Coverage by Class and Model')
bar_plot.set_xlabel('Class')
bar_plot.set_ylabel('Median Mutation Coverage Score')
bar_plot.legend(title='Model')

# Show the plot
plt.tight_layout()  # Ensure tight layout to prevent clipping of rotated labels
plt.show()