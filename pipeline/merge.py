import pandas as pd
import numpy as np

def merge(input_df_1, input_df_2):
    df_1 = input_df_1.copy()
    df_2 = input_df_2.copy()

    # Объединим данные:
    # 1. Ext_id - убираем, оставляем global_id, общий для df
    # 2. Address === WorksPlace
    # 3. global_id общий
    # 4. AdmArea, District === AdmArea, District
    # 5. Event_type + Name === WorksType
    # 6. Requester === Customer
    # 7. TS_from === ActualBeginDate и WorksBeginDate
    # 8. TS_to === PlannedEndDate и ActualEndDate
    # 9. Lanes_closed - оставить. Во втором df ставим как 0
    # 10. geoData общий
    # 11. WorkYear - добавить
    # 12. WorksStatus - добавить в зависимости от дат
    # 13. geodata_center - убираем

    # df_1
    # df_1['WorkYear'] = df_1['TS_to'].str[:4].astype(np.int32)
    df_1['WorkYear'] = df_1['TS_to'].dt.year.astype(np.int32)

    df_1['TS_from'] = pd.to_datetime(df_1['TS_from'], format='%Y-%m-%d',  errors='coerce')
    df_1['TS_to'] = pd.to_datetime(df_1['TS_to'], format='%Y-%m-%d',  errors='coerce')

    today = pd.Timestamp.now()

    conditions = [
        (df_1['TS_to'] < today),                               # Закончены
        ((df_1['TS_to'] > today) & (df_1['TS_from'] < today))  # Идут
    ]
    choices = ['закончены', 'идут']
    default = 'не начаты'

    df_1['WorksStatus'] = np.select(conditions, choices, default=default)

    df_1 = (
        df_1.assign(
            WorksType=lambda x: x['Event_type'].astype(str) + ', ' + x['Name'].astype(str),
            Customer=lambda x: x['Requester'],
            ActualBeginDate=lambda x: x['TS_from'],
            WorksBeginDate=lambda x: x['TS_from'],
            ActualEndDate=lambda x: x['TS_to'],
            PlannedEndDate=lambda x: x['TS_to']
        )[
            ['global_id',
            'Address',
            'AdmArea',
            'District',
            'WorksType',
            'WorksStatus',
            'Customer',
            'ActualBeginDate',
            'WorksBeginDate',
            'ActualEndDate',
            'PlannedEndDate',
            'Lanes_closed',
            'geoData',
            'WorkYear']
        ]
    )
    
    # df_2

    df_2['WorksBeginDate'] = pd.to_datetime(df_2['WorksBeginDate'], format='%Y-%m-%d',  errors='coerce')
    df_2['PlannedEndDate'] = pd.to_datetime(df_2['PlannedEndDate'], format='%Y-%m-%d',  errors='coerce')
    df_2['ActualBeginDate'] = pd.to_datetime(df_2['ActualBeginDate'], format='%Y-%m-%d',  errors='coerce')
    df_2['ActualEndDate'] = pd.to_datetime(df_2['ActualEndDate'], format='%Y-%m-%d',  errors='coerce')

    df_2 = (
        df_2.rename(columns={'WorksPlace': 'Address'})
            .assign(Lanes_closed=lambda x: 0)
        )[
            ['global_id',
            'Address',
            'AdmArea',
            'District',
            'WorksType',
            'WorksStatus',
            'Customer',
            'ActualBeginDate',
            'WorksBeginDate',
            'ActualEndDate',
            'PlannedEndDate',
            'Lanes_closed',
            'geoData',
            'WorkYear']
        ]
    
    df = pd.concat([df_1, df_2], ignore_index=True)

    # Удаление дублей
    before = df.shape[0]
    df = df.drop_duplicates(subset=df.columns)
    after = df.shape[0]

    print(f"Duplicated rows deleted: {before - after}")

    return df
