import re

import pandas as pd
import numpy as np

def preprocess(input_df):
    df = input_df.copy()

    '''
    Очистка данных:
    '''
    # Удаление признака c невалидным именем
    df = df.drop('Unnamed: 17', axis=1)

    # Признаки Descr, Geometry_point, geodata_center имеют только Nan значения. Удалим их
    df = df.drop(['Descr', 'Geometry_point', 'geodata_center'], axis=1)

    # Geometry_line повторяет признак geoData. Удалим Geometry_line
    df = df.drop(['Geometry_line'], axis=1)

    # Geometry_type не нужный признак
    df = df.drop(['Geometry_type'], axis=1)

    # Первая строка датасета выступает в качестве описания датасета. Уберем ее из данных
    df = df.drop(0)

    '''
    Заполнение пропусков:
    '''
    df['Requester'] = df['Requester'].fillna('Unknown')
    df['Lanes_closed'] = df['Lanes_closed'].fillna(0)

    '''
    Изменение типов данных:
    '''
    df['Ext_id'] = df['Ext_id'].astype(np.int32)
    df['Lanes_closed'] = df[df['Lanes_closed'].notna()]['Lanes_closed'].astype(np.int32)

    df['TS_from'] = pd.to_datetime(df['TS_from'], format='%d.%m.%Y',  errors='coerce')
    df['TS_to'] = pd.to_datetime(df['TS_to'], format='%d.%m.%Y',  errors='coerce')

    df['AdmArea'] = df['AdmArea'].apply(convert_to_list)
    df['District'] = df['District'].apply(convert_to_list)
    df = df.explode('AdmArea')
    df = df.explode('District')

    df['geoData'] = df['geoData'].apply(extract_coordinates)

    return df

def extract_coordinates(geometry_str):
    pattern = r"coordinates=\[\[\[(.*?)\]\]"
    match = re.search(pattern, geometry_str)

    if match:
        coordinates_str = match.group(1)
        return f'[[{coordinates_str}]]'
    return None

def convert_to_list(value):
    # Удаляем квадратные скобки и разделяем по запятой
    items = value.strip('[]').split(', ')
    # Возвращаем список
    return items if items != [''] else []