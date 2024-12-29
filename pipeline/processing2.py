import re

import pandas as pd
import numpy as np

def preprocess(input_df):
    df = input_df.copy()

    '''
    Очистка данных:
    '''

    # Contractor не нужный признак
    df = df.drop(['Contractor'], axis=1)

    # Первая строка датасета выступает в качестве описания датасета. Уберем ее из данных
    df = df.drop(0)

    '''
    Заполнение пропусков:
    '''

    # Все адреса, у которых отсутствует значение поля AdmArea или District, находятся вне территории Москвы. 
    # Заменим Nan на 'Московская область'
    df['AdmArea'] = df['AdmArea'].fillna('Московская область')
    df['District'] = df['District'].fillna('Московская область')

    df['Customer'] = df['Customer'].fillna('Unknown')

    '''
    Изменение типов данных:
    '''
    df['WorksBeginDate'] = pd.to_datetime(df['WorksBeginDate'], format='%d.%m.%Y',  errors='coerce')
    df['PlannedEndDate'] = pd.to_datetime(df['PlannedEndDate'], format='%d.%m.%Y',  errors='coerce')
    df['ActualBeginDate'] = pd.to_datetime(df['ActualBeginDate'], format='%d.%m.%Y',  errors='coerce')
    df['ActualEndDate'] = pd.to_datetime(df['ActualEndDate'], format='%d.%m.%Y',  errors='coerce')

    df['WorkYear'] = df['WorkYear'].astype(np.int32)

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