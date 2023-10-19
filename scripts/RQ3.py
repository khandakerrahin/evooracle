import pandas as pd
import matplotlib.pyplot as plt

# Your data (replace with your actual data)
data = {
    'Model': ['EvoSuite', 'MPT-7B-Chat', 'Nous-hermes-13B_ggml_v3', 'Orca_mini_13B-GGML_v3', 'StableVicuna-13B', 'WizardLM-13B-V1.1'],
    'Line Coverage': [71.23, 64.00, 64.37, 45.38, 66.00, 57.06],
    'Mutation Coverage': [52.69, 41.41, 40.57, 22.28, 42.82, 28.51],
    'Test Strength': [75.80, 62.68, 61.88, 43.82, 63.62, 48.68]
}

df = pd.DataFrame(data)

# Calculate differences from EvoSuite baseline
df_diff = df.set_index('Model').subtract(df.set_index('Model').loc['EvoSuite'], axis='columns')

# Plotting
ax = df_diff.plot(kind='bar', figsize=(10, 6), colormap='viridis', title='Differences from EvoSuite Baseline')
ax.set_ylabel('Difference')
ax.set_xlabel('Model')

# Show legend
ax.legend(bbox_to_anchor=(1, 1), loc='upper left')

# Show plot
plt.show()
