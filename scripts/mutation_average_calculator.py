import pandas as pd

# Read the CSV
df = pd.read_csv('/home/shaker/Downloads/EOMutationScore.csv')

# Group by 'class' and 'model', and calculate the average
grouped_df = df.groupby(['class', 'model']).agg({
    'eo_test_count': 'mean',
    'eo_line_coverage_score': 'mean',
    'eo_mutation_coverage_score': 'mean',
    'eo_test_strength_score': 'mean'
}).reset_index()

# Write the results to another CSV
grouped_df.to_csv('/home/shaker/Downloads/EO_mutation_score_avg.csv', index=False)
