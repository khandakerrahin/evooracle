import pandas as pd
import matplotlib.pyplot as plt

# Load the original CSV file
df = pd.read_csv("/home/shaker/Documents/Thesis/Writing/data/thesis_final_evoracle_final_results.csv")

# Initialize variables for total counts
ultimate_total_methods = 0
ultimate_total_attempts = 0
ultimate_total_syntax_error = 0
ultimate_total_compile_error = 0
ultimate_total_runtime_error = 0
ultimate_total_passed = 0

ultimate_result_rows_csv = []

# Iterate over each unique model
for model in df['model'].unique():
    # Filter the dataframe for the current model
    model_df = df[df['model'] == model]
    
    # Initialize an empty list to store the results
    result_rows_plot = []
    result_rows_csv = []
    # Initialize variables for total counts
    total_methods = 0
    total_attempts = 0
    total_syntax_error = 0
    total_compile_error = 0
    total_runtime_error = 0
    total_passed = 0

    # Iterate over each unique Class (CUT)
    for cut in model_df['CUT'].unique():
        # Filter the dataframe for the current Class
        cut_df = model_df[model_df['CUT'] == cut]
        
        # Count unique test methods
        test_method_count = cut_df['test_method_name'].nunique()
        total_methods += test_method_count

        # Sum of attempts
        attempts = cut_df['attempts'].sum()
        total_attempts += attempts

        # Count SyntaxError
        syntax_error = cut_df['assertion_generated'].eq(False).sum()
        syntax_error_percent = (syntax_error / attempts) * 100
        total_syntax_error += syntax_error

        # Count CompileError
        compile_error = (cut_df['assertion_generated'].eq(True) & cut_df['eo_is_compiled'].eq(False)).sum()
        compile_error_percent = (compile_error / attempts) * 100
        total_compile_error += compile_error

        # Count RuntimeError
        runtime_error = (cut_df['eo_is_compiled'].eq(True) & cut_df['eo_is_run'].eq(False)).sum()
        runtime_error_percent = (runtime_error / attempts) * 100
        total_runtime_error += runtime_error

        # Count Passed
        passed = cut_df['eo_is_run'].eq(True).sum()
        passed_percent = (passed / attempts) * 100
        total_passed += passed

        # Append results to the result list
        result_rows_plot.append({
            "Class": cut,
            "Test_method_count": test_method_count,
            "Attempts": attempts,
            "SyntaxError": syntax_error,
            "SyntaxError (%)": syntax_error_percent,
            "CompileError": compile_error,
            "CompileError (%)": compile_error_percent,
            "RuntimeError": runtime_error,
            "RuntimeError (%)": runtime_error_percent,
            "Passed": passed,
            "Passed (%)": passed_percent
        })

        result_rows_csv.append({
            "Class": cut,
            "Test_method_count": test_method_count,
            "Attempts": attempts,
            "SyntaxError": f"{syntax_error} ({syntax_error_percent:.2f}%)",
            "CompileError": f"{compile_error} ({compile_error_percent:.2f}%)",
            "RuntimeError": f"{runtime_error} ({runtime_error_percent:.2f}%)",
            "Passed": f"{passed} ({passed_percent:.2f}%)"
        })
    # Create a new dataframe from the result list
    result_df_plot = pd.DataFrame(result_rows_plot)
    
    # Add a row for total counts
    result_rows_csv.append({
        "Class": "Total",
        "Test_method_count": total_methods,
        "Attempts": total_attempts,
        "SyntaxError": f"{total_syntax_error} ({((total_syntax_error / total_attempts) * 100):.2f}%)",
        "CompileError": f"{total_compile_error} ({((total_compile_error / total_attempts) * 100):.2f}%)",
        "RuntimeError": f"{total_runtime_error} ({((total_runtime_error / total_attempts) * 100):.2f}%)",
        "Passed": f"{total_passed} ({((total_passed / total_attempts) * 100):.2f}%)"
    })

    result_df_csv = pd.DataFrame(result_rows_csv)

    # Save the result dataframe to a new CSV file for each model
    result_df_csv.to_csv(f'/home/shaker/Documents/Thesis/Writing/data/RQ1_{model}.csv', index=False)

    ultimate_total_attempts += total_attempts
    ultimate_total_syntax_error += total_syntax_error
    ultimate_total_compile_error += total_compile_error
    ultimate_total_runtime_error += total_runtime_error
    ultimate_total_passed += total_passed

    # # Plotting
    # ax = result_df_plot.set_index('Class')[['SyntaxError (%)', 'CompileError (%)', 'RuntimeError (%)', 'Passed (%)']].plot(
    #     kind='bar', stacked=True, figsize=(12, 6), colormap='viridis', title=f'Results for {model}')

    # # Add labels
    # ax.set_ylabel('Percentage')
    # ax.set_xlabel('Class')

    # # Show legend
    # ax.legend(bbox_to_anchor=(1, 1), loc='upper left')

    # # Show plot
    # plt.show()
ultimate_result_rows_csv.append({
    "Class": "Total",
    "Test_method_count": total_methods,
    "Attempts": ultimate_total_attempts,
    "SyntaxError": f"{ultimate_total_syntax_error} ({((ultimate_total_syntax_error / ultimate_total_attempts) * 100):.2f}%)",
    "CompileError": f"{ultimate_total_compile_error} ({((ultimate_total_compile_error / ultimate_total_attempts) * 100):.2f}%)",
    "RuntimeError": f"{ultimate_total_runtime_error} ({((ultimate_total_runtime_error / ultimate_total_attempts) * 100):.2f}%)",
    "Passed": f"{ultimate_total_passed} ({((ultimate_total_passed / ultimate_total_attempts) * 100):.2f}%)"
})

ultimate_result_df_csv = pd.DataFrame(ultimate_result_rows_csv)

# Save the result dataframe to a new CSV file for each model
ultimate_result_df_csv.to_csv(f'/home/shaker/Documents/Thesis/Writing/data/RQ1_all_count.csv', index=False)