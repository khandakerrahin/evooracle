from bs4 import BeautifulSoup
import csv
import re

def get_linecov_mutcov_teststrength(filename):
    
    # Read HTML from a file
    with open(filename, 'r', encoding='utf-8') as file:
        html = file.read()

    soup = BeautifulSoup(html, 'html.parser')

    line_coverage = 0
    mutation_coverage = 0
    test_strength = 0

    coverage_legend_line = ""
    coverage_legend_mutation = ""
    coverage_legend_test = ""

    # Extracting values
    try: 
        line_coverage = re.sub(r'[^0-9.]', '', soup.select_one('td:nth-of-type(2)').text.strip().split()[0])
        mutation_coverage = re.sub(r'[^0-9.]', '', soup.select_one('td:nth-of-type(3)').text.strip().split()[0])
        test_strength = re.sub(r'[^0-9.]', '', soup.select_one('td:nth-of-type(4)').text.strip().split()[0])

        coverage_legend_line = soup.select_one('td:nth-of-type(2) .coverage_legend').text.strip()
        coverage_legend_mutation = soup.select_one('td:nth-of-type(3) .coverage_legend').text.strip()
        coverage_legend_test = soup.select_one('td:nth-of-type(4) .coverage_legend').text.strip()
    except:
        print("Value parsing failed.")

    # # Writing to CSV
    # with open('coverage_report.csv', 'w', newline='') as csvfile:
    #     fieldnames = ['Line Coverage', 'Mutation Coverage', 'Test Strength']
    #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    #     writer.writeheader()
    #     writer.writerow({'Line Coverage': line_coverage, 'Mutation Coverage': mutation_coverage, 'Test Strength': test_strength})

    return line_coverage, mutation_coverage, test_strength, coverage_legend_line, coverage_legend_mutation, coverage_legend_test