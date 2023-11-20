import pandas as pd

# Read the CSV
df = pd.read_csv('/home/shaker/Documents/Thesis/Writing/data/EO_mutation_score_second_run_enhanced_ES_mean.csv')

# Pivot the DataFrame for Line Coverage
line_coverage_df = df.pivot(index='class', columns='model', values='eo_line_coverage_score').reset_index()
line_coverage_df.to_csv('/home/shaker/Documents/Thesis/Writing/data/second_table_line_coverage_enhanced_ES.csv', index=False)

# Pivot the DataFrame for Mutation Coverage
mutation_coverage_df = df.pivot(index='class', columns='model', values='eo_mutation_coverage_score').reset_index()
mutation_coverage_df.to_csv('/home/shaker/Documents/Thesis/Writing/data/second_table_mutation_coverage_enhanced_ES.csv', index=False)

# Pivot the DataFrame for Test Strengths
test_strengths_df = df.pivot(index='class', columns='model', values='eo_test_strength_score').reset_index()
test_strengths_df.to_csv('/home/shaker/Documents/Thesis/Writing/data/second_table_test_strengths_enhanced_ES.csv', index=False)
