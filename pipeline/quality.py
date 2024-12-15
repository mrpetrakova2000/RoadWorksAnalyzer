import re
from datetime import datetime

import pandas as pd
import numpy as np

# 1. Проверка на неполные данные
def null_data(row):
    ness_columns = ['global_id', 'Address', 'AdmArea', 'District', 'WorksType', 'WorksStatus',
               'Customer','ActualBeginDate','WorksBeginDate', 'ActualEndDate',
               'PlannedEndDate', 'Lanes_closed','geoData', 'WorkYear']
    row = row.copy()
    
    for column in ness_columns:
        if column not in row.index:
            row[column] = np.nan
        
    nan_indices = row.index[row.isna()].tolist()
    if len(nan_indices) == 0:
        return None
    return "NULL_DATA", len(nan_indices), set(nan_indices)

def check_date_format_string(date):
    if isinstance(date, datetime):
        return True 

    if isinstance(date, str):
        try:
            datetime.strptime(date, '%Y-%m-%d')
            return True 
        except ValueError:
            return False 

    return False

# 2. Проверка формата даты:   
def date_format(row):
    date_columns = ['ActualBeginDate', 'WorksBeginDate', 'ActualEndDate', 'PlannedEndDate']
    errors = set()
    for col in date_columns:
        if col not in row.index or not check_date_format_string(row[col]):
            errors.add(col)
    if len(errors) == 0:
        return None
    return "DATE_FORMAT_ERROR", errors

# 3. Проверка формата координат
def coordinates_format(row):
    try:
        coords_text = row['geoData']
        for pair in coords_text.split("], ["):
            clean_pair = pair.replace("[", "").replace("]", "").strip()
            tmp = [float(coord) for coord in clean_pair.split(",")]
            lat, lon = tmp[1], tmp[0]
            if not ((0 <= abs(lat) <= 90) and (0 <= abs(lon) <= 180)):
                raise Exception()
        return None
    except:
        return 'DATE_COORDINATES_ERROR'

# 4. Проверка согласованности дат
def date_consistency(row):
    date_columns = ['ActualBeginDate', 'WorksBeginDate', 'ActualEndDate', 'PlannedEndDate']
    errors = set()
    if not ('ActualBeginDate' in row.index and 'ActualEndDate' in row.index and
        check_date_format_string(row['ActualBeginDate']) and check_date_format_string(row['ActualEndDate']) and
       row['ActualBeginDate'] <= row['ActualEndDate']):
        errors.add('ActualBeginDate & ActualEndDate')
    if not ('WorksBeginDate' in row.index and 'PlannedEndDate' in row.index and
        check_date_format_string(row['WorksBeginDate']) and check_date_format_string(row['PlannedEndDate']) and
       row['WorksBeginDate'] <= row['PlannedEndDate']):
        errors.add('WorksBeginDate & PlannedEndDate') 
    if len(errors) == 0:
        return None
    return "DATE_CONSISTENCY", errors

# 4. Проверка на дубли
def data_duplicates(df):
    res = df.duplicated().sum()
    return 'DATA_DUPLICATES', res

# Отчет
def quality(input_df):
    df = input_df.copy()

    total = df.shape[0]
    check_for_row = [null_data, coordinates_format, date_format, date_consistency]
    
    error_df = df.copy()
    error_df['NULL_DATA'] = 0 # метка, есть ли пропуски
    error_df['NULL_DATA_COUNT'] = 0 # колво пустых колонк
    error_df['DATE_COORDINATES_ERROR'] = 0
    error_df['DATE_FORMAT_ERROR'] = 0
    error_df['DATE_CONSISTENCY'] = 0
    for idx, row in error_df.iterrows():
        for f in check_for_row:
            res = f(row)
            if res == None:
                continue
            error, args = res[0], res[1:]
            error_df.loc[idx, error] = 1
            if error == 'NULL_DATA':
                error_df.loc[idx, 'NULL_DATA_COUNT'] = res[1]
    errors_rows = {
        'NULL_DATA': f'{error_df["NULL_DATA"].sum() / total * 100:.4f}%',
        'NULL_DATA_COUNT': f'{error_df["NULL_DATA_COUNT"].sum() / (total * len(df.columns)):.4f}%',
        'DATE_COORDINATES_ERROR': f'{error_df["DATE_COORDINATES_ERROR"].sum() / total * 100:.4f}%',
        'DATE_FORMAT_ERROR': f'{error_df["DATE_FORMAT_ERROR"].sum() / total * 100:.4f}%',
        'DATE_CONSISTENCY': f'{error_df["DATE_CONSISTENCY"].sum() / total * 100:.4f}%',
    }
    
    check_for_df = [data_duplicates]
    errors_df = {}
    for f in check_for_df:
        res = f(df)
        errors_df[res[0]] = f'{res[1] / total * 100:.4f}%'
    return {**errors_rows, **errors_df}

def pretty_print(report):
    print("===Data quality report===")
    print("Percentage of rows with incomplete data -", report['NULL_DATA'])
    print("Percentage of cell with incomplete data -", report['NULL_DATA_COUNT'])
    print("Percentage of rows with incorrect coordinate format -", report['DATE_COORDINATES_ERROR'])
    print("Percentage of rows with incorrect date format -", report['DATE_FORMAT_ERROR'])
    print("Percentage of rows with inconsistent dates -", report['DATE_FORMAT_ERROR'])
    print("=========================")