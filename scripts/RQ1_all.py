import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the original CSV file
df = pd.read_csv("/home/shaker/Documents/Thesis/Writing/data/thesis_final_evoracle_final_results.csv")

# Initialize an empty list to store the results
result_rows = []

# Iterate over each unique model
for model in df['model'].unique():
    # Filter the dataframe for the current model
    model_df = df[df['model'] == model]
    
    # Iterate over each unique Class (CUT)
    for cut in model_df['CUT'].unique():
        # Filter the dataframe for the current Class
        cut_df = model_df[model_df['CUT'] == cut]
        
        # Count unique test methods
        test_method_count = cut_df['test_method_name'].nunique()
        
        # Sum of attempts
        attempts = cut_df['attempts'].sum()
        
        # Count SyntaxError
        syntax_error = cut_df['assertion_generated'].eq(False).sum()
        
        # Count CompileError
        compile_error = (cut_df['assertion_generated'].eq(True) & cut_df['eo_is_compiled'].eq(False)).sum()
        # Count RuntimeError
        runtime_error = (cut_df['eo_is_compiled'].eq(True) & cut_df['eo_is_run'].eq(False)).sum()
        
        # Count Passed
        passed = cut_df['eo_is_run'].eq(True).sum()
        
        # Append results to the result list
        result_rows.append({
            "Model": model,
            "Class": cut,
            "Test_method_count": test_method_count,
            "Attempts": attempts,
            "SyntaxError": syntax_error,
            "CompileError": compile_error,
            "RuntimeError": runtime_error,
            "Passed": passed
        })

# Create a new dataframe from the result list
result_df = pd.DataFrame(result_rows)

# Plotting
fig, ax = plt.subplots(figsize=(15, 6))
sns.barplot(data=result_df, x='Model', y='Passed', hue='Class', ax=ax)
ax.set_xlabel('Model')
ax.set_ylabel('Passed Test Cases')
ax.set_title('Comparison of Passed Test Cases for Different Models and Classes')
plt.tight_layout()
plt.show()
