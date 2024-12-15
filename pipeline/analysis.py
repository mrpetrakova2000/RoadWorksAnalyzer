import os
import re
from datetime import datetime

import pandas as pd
import numpy as np
import folium
from geopy.distance import geodesic

import matplotlib.pyplot as plt
import seaborn as sns

def generate_months(start_date, end_date):
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    months = pd.date_range(start, end, freq='MS').strftime('%Y-%m').tolist()
    return months

def get_list_coordinates(coords_text):
  coordinates = []
  for pair in coords_text.split("], ["):
      clean_pair = pair.replace("[", "").replace("]", "").strip()
      tmp = [float(coord) for coord in clean_pair.split(",")]
      tmp[0], tmp[1] = tmp[1], tmp[0]
      coordinates.append(tmp)
  return coordinates

def calculate_path_length(coords_text):
    total_distance = 0.0
    coords = get_list_coordinates(coords_text)
    for i in range(len(coords) - 1):
        total_distance += geodesic(coords[i][::-1], coords[i + 1][::-1]).kilometers
    return total_distance

def setup_folder():
    main_folder = 'analysis'
    os.makedirs(main_folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    subfolder_name = f"{timestamp}"
    full_subfolder_path = os.path.join(main_folder, subfolder_name)
    os.makedirs(full_subfolder_path, exist_ok=True)
    return full_subfolder_path

def analyse(input_df):
    dir_path = setup_folder()

    df = input_df.copy()

    # 1. Количество начатых работ по месяцам
    name = 'Количество начатых работ по месяцам'
    save_path = os.path.join(dir_path, name + '.png')
    df['YearMonthActualBeginDate'] = pd.to_datetime(df['ActualBeginDate']).dt.strftime('%Y-%m')
    plt.figure(figsize=(20, 12))
    df['YearMonthActualBeginDate'].value_counts().sort_index().plot(kind='bar')
    plt.title(name)
    plt.xlabel('Год')
    plt.ylabel('Количество начатых работ')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Количество выполненных работ по месяцам
    name = 'Количество выполненных работ по месяцам'
    save_path = os.path.join(dir_path, name + '.png')
    df['YearMonthActualEndDate'] = pd.to_datetime(df['ActualEndDate']).dt.strftime('%Y-%m')
    plt.figure(figsize=(20, 12))
    df['YearMonthActualEndDate'].value_counts().sort_index().plot(kind='bar')
    plt.title('Количество выполненных работ по месяцам')
    plt.xlabel('Год')
    plt.ylabel('Количество выполненных работ')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

    #3
    name = 'Количество активных работ по месяцам'
    save_path = os.path.join(dir_path, name + '.png')
    df = df.dropna()
    df['Months'] = df.apply(lambda row: generate_months(row['YearMonthActualBeginDate'], row['YearMonthActualEndDate']), axis=1)
    explode_df = df.explode('Months')
    plt.figure(figsize=(20, 12))
    explode_df['Months'].value_counts().sort_index().plot(kind='bar')
    plt.title('Количество активных работ по месяцам')
    plt.xlabel('Год')
    plt.ylabel('Количество активных работ')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

    # 4. Доля работ, которые начались позже срокаx
    name = 'Доля работ, которые начались позже срока'
    save_path = os.path.join(dir_path, name + '.png')
    df['ActualBeginDate'] = pd.to_datetime(df['ActualBeginDate'])
    df['WorksBeginDate'] = pd.to_datetime(df['WorksBeginDate'])
    df['StatusBegin'] = df.apply(lambda row: 'В срок' if row['WorksBeginDate'] >= row['ActualBeginDate'] else 'Позже срока', axis=1)
    status_counts = df['StatusBegin'].value_counts()
    plt.figure(figsize=(8, 6))
    status_counts.plot(kind='pie', autopct='%1.1f%%', startangle=90, colors=['#66c2a5', '#fc8d62'])
    plt.title('Доля работ, начатых в срок и позже срока')
    plt.ylabel('')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

    # 5. Количество работ, начатых в срок и позже срока
    name = 'Количество работ, начатых в срок и позже срока'
    save_path = os.path.join(dir_path, name + '.png')
    status_counts = df.groupby(['YearMonthActualBeginDate', 'StatusBegin']).size().unstack(fill_value=0)
    status_counts.plot(kind='bar', stacked=True, figsize=(20, 12), color=['#66c2a5', '#fc8d62'])
    plt.title('Количество работ, начатых в срок и позже срока (по месяцам)', fontsize=16)
    plt.xlabel('Месяц год', fontsize=12)
    plt.ylabel('Количество работ', fontsize=12)
    plt.legend(title='Статус начала работы')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

    # 6. Доля работ, законченных в срок и позже срока
    name = 'Доля работ, законченных в срок и позже срока'
    save_path = os.path.join(dir_path, name + '.png')
    df['ActualEndDate'] = pd.to_datetime(df['ActualEndDate'])
    df['PlannedEndDate'] = pd.to_datetime(df['PlannedEndDate'])
    df['StatusEnd'] = df.apply(lambda row: 'В срок' if row['PlannedEndDate'] >= row['ActualEndDate'] else 'Позже срока', axis=1)
    status_counts = df['StatusEnd'].value_counts()
    plt.figure(figsize=(8, 6))
    status_counts.plot(kind='pie', autopct='%1.1f%%', startangle=90, colors=['#66c2a5', '#fc8d62'])
    plt.title('Доля работ, законченных в срок и позже срока')
    plt.ylabel('')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

    # 7. Количество работ, законченных в срок и позже срока
    name = 'Количество работ, законченных в срок и позже срока'
    save_path = os.path.join(dir_path, name + '.png')
    status_counts = df.groupby(['YearMonthActualEndDate', 'StatusEnd']).size().unstack(fill_value=0)
    status_counts.plot(kind='bar', stacked=True, figsize=(20, 12), color=['#66c2a5', '#fc8d62'])
    plt.title('Количество работ, законченных в срок и позже срока (по месяцам)', fontsize=16)
    plt.xlabel('Месяц год', fontsize=12)
    plt.ylabel('Количество работ', fontsize=12)
    plt.legend(title='Статус начала работы')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

    # 8. Количество ремонтируемых дорог по округам
    name = 'Количество ремонтируемых дорог по округам'
    save_path = os.path.join(dir_path, name + '.png')
    plt.figure(figsize=(20, 12))
    df['AdmArea'].value_counts().sort_index().sort_values(ascending=False).plot(kind='bar')
    plt.title('Количество ремонтируемых дорог по округам')
    plt.xlabel('Округ')
    plt.ylabel('Количество работ')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

    # 9. Количество ремонтируемых дорог по районам
    name = 'Количество ремонтируемых дорог по районам'
    save_path = os.path.join(dir_path, name + '.png')
    plt.figure(figsize=(20, 12))
    district_counts = df['District'].value_counts().sort_index()
    district_counts[district_counts > 10].sort_values(ascending=False).plot(kind='bar')
    plt.title('Количество ремонтируемых дорог по районам')
    plt.xlabel('Район')
    plt.ylabel('Количество работ')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

    df['LengthKm'] = df['geoData'].apply(calculate_path_length)

    # 10. Длина ремонтируемых дорог по округам
    name = 'Длина ремонтируемых дорог по округам'
    save_path = os.path.join(dir_path, name + '.png')
    plt.figure(figsize=(20, 12))
    district_lengths = df.groupby('AdmArea')['LengthKm'].sum().reset_index()
    district_lengths.columns = ['AdmArea', 'TotalLengthKm']
    district_lengths = district_lengths.sort_values(by='TotalLengthKm', ascending=False)
    plt.bar(district_lengths['AdmArea'], district_lengths['TotalLengthKm'])
    plt.title('Суммарная длина дорог по округам', fontsize=16)
    plt.xlabel('Районы', fontsize=12)
    plt.ylabel('Длина дорог (км)', fontsize=12)
    plt.xticks(rotation=90, fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

    # 11. Длина ремонтируемых дорог по районам
    name = 'Длина ремонтируемых дорог по районам'
    save_path = os.path.join(dir_path, name + '.png')
    plt.figure(figsize=(20, 12))
    district_lengths = df.groupby('District')['LengthKm'].sum().reset_index()
    district_lengths.columns = ['District', 'TotalLengthKm']
    district_lengths = district_lengths[district_lengths['TotalLengthKm'] > 50].sort_values(by='TotalLengthKm', ascending=False)
    plt.bar(district_lengths['District'], district_lengths['TotalLengthKm'])
    plt.title('Суммарная длина дорог по районам', fontsize=16)
    plt.xlabel('Районы', fontsize=12)
    plt.ylabel('Длина дорог (км)', fontsize=12)
    plt.xticks(rotation=90, fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

    # Карта. Выбор по окргам
    name = 'map_adm_area.html'
    save_path = os.path.join(dir_path, name)
    m = folium.Map(location=[55.7558, 37.6173], zoom_start=11)
    layer_groups = {}
    # Проход по всем строкам DataFrame
    for idx, row in df.iterrows():
        coords_text = row['geoData']
        adm_area = row['AdmArea']

        if pd.notna(coords_text):
            # Преобразование строки координат в список точек
            coordinates = []
            for pair in coords_text.split("], ["):
                clean_pair = pair.replace("[", "").replace("]", "").strip()
                tmp = [float(coord) for coord in clean_pair.split(",")]
                tmp[0], tmp[1] = tmp[1], tmp[0]
                coordinates.append(tmp)

            # Создание слоя для административного округа, если его еще нет
            if adm_area not in layer_groups:
                layer_groups[adm_area] = folium.FeatureGroup(name=adm_area)

            # Добавление линии в слой района
            folium.PolyLine(
                locations=coordinates,
                color='blue',
                weight=3,
                popup=f"{row['Address']} ({row['WorksType']})"
            ).add_to(layer_groups[adm_area])

    for layer in layer_groups.values():
        layer.add_to(m)
    # Добавление переключателя слоев
    folium.LayerControl().add_to(m)
    # Сохранение карты
    m.save(save_path)

    # Карта. Выбор по районам
    name = 'map_district.html'
    save_path = os.path.join(dir_path, name)
    m = folium.Map(location=[55.7558, 37.6173], zoom_start=11)
    layer_groups = {}
    # Проход по всем строкам DataFrame
    for idx, row in df.iterrows():
        coords_text = row['geoData']
        district = row['District']

        if pd.notna(coords_text):
            coordinates = []
            for pair in coords_text.split("], ["):
                clean_pair = pair.replace("[", "").replace("]", "").strip()
                tmp = [float(coord) for coord in clean_pair.split(",")]
                tmp[0], tmp[1] = tmp[1], tmp[0]
                coordinates.append(tmp)

            if district not in layer_groups:
                layer_groups[district] = folium.FeatureGroup(name=district)

            folium.PolyLine(
                locations=coordinates,
                color='blue',
                weight=3,
                popup=f"{row['Address']} ({row['WorksType']})"
            ).add_to(layer_groups[district])

    for layer in layer_groups.values():
        layer.add_to(m)
    # Добавление переключателя слоев
    folium.LayerControl().add_to(m)
    # Сохранение карты
    m.save(save_path)

    # Карта. Выбор по статусу работ
    name = 'map_works_status.html'
    save_path = os.path.join(dir_path, name)
    m = folium.Map(location=[55.7558, 37.6173], zoom_start=11)
    layer_groups = {}
    # Проход по всем строкам DataFrame
    for idx, row in df.iterrows():
        coords_text = row['geoData']
        worksStatus = row['WorksStatus']

        if pd.notna(coords_text):
            coordinates = []
            for pair in coords_text.split("], ["):
                clean_pair = pair.replace("[", "").replace("]", "").strip()
                tmp = [float(coord) for coord in clean_pair.split(",")]
                tmp[0], tmp[1] = tmp[1], tmp[0]
                coordinates.append(tmp)

            if worksStatus not in layer_groups:
                layer_groups[worksStatus] = folium.FeatureGroup(name=worksStatus)

            folium.PolyLine(
                locations=coordinates,
                color='blue',
                weight=3,
                popup=f"{row['Address']} ({row['WorksType']})"
            ).add_to(layer_groups[worksStatus])

    for layer in layer_groups.values():
        layer.add_to(m)
    # Добавление переключателя слоев
    folium.LayerControl().add_to(m)
    # Сохранение карты
    m.save(save_path)

    # Карта. Выбор по месяцам
    name = 'map_months_area.html'
    save_path = os.path.join(dir_path, name)
    m = folium.Map(location=[55.7558, 37.6173], zoom_start=11)
    layer_groups = {}
    # Проход по всем строкам DataFrame
    for idx, row in explode_df.iterrows():
        coords_text = row['geoData']
        months = row['Months']

        if pd.notna(coords_text):
            coordinates = []
            for pair in coords_text.split("], ["):
                clean_pair = pair.replace("[", "").replace("]", "").strip()
                tmp = [float(coord) for coord in clean_pair.split(",")]
                tmp[0], tmp[1] = tmp[1], tmp[0]
                coordinates.append(tmp)

            if months not in layer_groups:
                layer_groups[months] = folium.FeatureGroup(name=months)

            folium.PolyLine(
                locations=coordinates,
                color='blue',
                weight=3,
                popup=f"{row['Address']} ({row['WorksType']})"
            ).add_to(layer_groups[months])
    for k,layer in sorted(layer_groups.items()):
        layer.add_to(m)
    # Добавление переключателя слоев
    folium.LayerControl().add_to(m)
    # Сохранение карты
    m.save(save_path)
    