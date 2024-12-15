import pandas as pd
import time
import os

import processing1
import processing2
import merge
import db
import analysis
import quality

file_path_df1 = os.path.join('data', 'Moscow-data-2024-12-05.csv')
file_path_df2 = os.path.join('data', 'Moscow-alter-2024-11-13.csv')

try:
    overall_start_time = time.time()

    start_time = time.time()
    df_1 = pd.read_csv(file_path_df1, sep=';')
    df_2 = pd.read_csv(file_path_df2, sep=';')
    load_time = time.time() - start_time
    print(f"Loading data completed successfully in {load_time:.2f} seconds")

    start_time = time.time()
    df_1 = processing1.preprocess(df_1)
    process_1_time = time.time() - start_time
    print(f"Processing of data from the first source completed successfully in {process_1_time:.2f} seconds")

    start_time = time.time()
    df_2 = processing2.preprocess(df_2)
    process_2_time = time.time() - start_time
    print(f"Processing of data from the second source completed successfully in {process_2_time:.2f} seconds")

    start_time = time.time()
    df = merge.merge(df_1, df_2)
    merge_time = time.time() - start_time
    print(f"Merge data completed successfully in {merge_time:.2f} seconds")

    start_time = time.time()
    db.save_in_db(df)
    save_db_time = time.time() - start_time
    print(f"Loading in DB completed successfully in {save_db_time:.2f} seconds")

    start_time = time.time()
    analysis.analyse(df)
    analysis_time = time.time() - start_time
    print(f"Analysis completed successfully in {analysis_time:.2f} seconds")

    start_time = time.time()
    report = quality.quality(df)
    report_creation_time = time.time() - start_time
    print(f"Creating data quality report completed successfully in {report_creation_time:.2f} seconds")
    quality.pretty_print(report)

    overall_end_time = time.time()
    total_execution_time = overall_end_time - overall_start_time
    print(f"Pipeline completed successfully in {total_execution_time:.2f} seconds")
except Exception as e:
    print("Pipeline failed:")
    print(e)
