import pandas as pd

# Read the CSV
df = pd.read_csv('/home/shaker/Documents/Thesis/Writing/data/EO_mutation_score_avg.csv')

# Pivot the DataFrame for Line Coverage
line_coverage_df = df.pivot(index='class', columns='model', values='eo_line_coverage_score').reset_index()
line_coverage_df.to_csv('/home/shaker/Downloads/line_coverage.csv', index=False)

# Pivot the DataFrame for Mutation Coverage
mutation_coverage_df = df.pivot(index='class', columns='model', values='eo_mutation_coverage_score').reset_index()
mutation_coverage_df.to_csv('/home/shaker/Downloads/mutation_coverage.csv', index=False)

# Pivot the DataFrame for Test Strengths
test_strengths_df = df.pivot(index='class', columns='model', values='eo_test_strength_score').reset_index()
test_strengths_df.to_csv('/home/shaker/Downloads/test_strengths.csv', index=False)
