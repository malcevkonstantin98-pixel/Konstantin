#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Программа для строителей - Калькулятор строительных материалов
"""

import math


def calculate_bricks(length, height, width, brick_length=0.25, brick_height=0.065, brick_width=0.12, mortar_joint=0.01):
    """
    Расчет количества кирпичей для стены.
    
    :param length: длина стены в метрах
    :param height: высота стены в метрах
    :param width: толщина стены в метрах (для расчета объема)
    :param brick_length: длина кирпича в метрах (по умолчанию 250мм)
    :param brick_height: высота кирпича в метрах (по умолчанию 65мм)
    :param brick_width: ширина кирпича в метрах (по умолчанию 120мм)
    :param mortar_joint: толщина шва в метрах (по умолчанию 10мм)
    :return: количество кирпичей
    """
    # Площадь стены
    wall_area = length * height
    
    # Площадь одного кирпича с учетом шва
    brick_area_with_mortar = (brick_length + mortar_joint) * (brick_height + mortar_joint)
    
    # Количество кирпичей на 1 м²
    bricks_per_sqm = 1 / brick_area_with_mortar
    
    # Общее количество кирпичей
    total_bricks = math.ceil(wall_area * bricks_per_sqm)
    
    return {
        'wall_area': wall_area,
        'bricks_per_sqm': round(bricks_per_sqm, 1),
        'total_bricks': total_bricks,
        'volume': length * height * width
    }


def calculate_concrete(length, width, thickness):
    """
    Расчет объема бетона для фундамента или плиты.
    
    :param length: длина в метрах
    :param width: ширина в метрах
    :param thickness: толщина в метрах
    :return: объем бетона в м³
    """
    volume = length * width * thickness
    # Добавляем 5% запаса
    volume_with_reserve = volume * 1.05
    
    return {
        'volume': round(volume, 2),
        'volume_with_reserve': round(volume_with_reserve, 2),
        'length': length,
        'width': width,
        'thickness': thickness
    }


def calculate_room_parameters(length, width, height, windows=None, doors=None):
    """
    Расчет параметров помещения (площадь стен, пола, потолка).
    
    :param length: длина помещения в метрах
    :param width: ширина помещения в метрах
    :param height: высота помещения в метрах
    :param windows: список окон [(ширина, высота), ...]
    :param doors: список дверей [(ширина, высота), ...]
    :return: словарь с параметрами
    """
    # Площадь пола и потолка
    floor_area = length * width
    
    # Периметр помещения
    perimeter = 2 * (length + width)
    
    # Площадь стен
    wall_area = perimeter * height
    
    # Вычитаем окна и двери
    openings_area = 0
    
    if windows:
        for w, h in windows:
            openings_area += w * h
    
    if doors:
        for w, h in doors:
            openings_area += w * h
    
    net_wall_area = wall_area - openings_area
    
    return {
        'floor_area': round(floor_area, 2),
        'ceiling_area': round(floor_area, 2),
        'perimeter': round(perimeter, 2),
        'gross_wall_area': round(wall_area, 2),
        'openings_area': round(openings_area, 2),
        'net_wall_area': round(net_wall_area, 2),
        'room_volume': round(length * width * height, 2)
    }


def calculate_tiles(area, tile_length, tile_width, waste_percentage=10):
    """
    Расчет количества плитки.
    
    :param area: площадь для укладки в м²
    :param tile_length: длина плитки в см
    :param tile_width: ширина плитки в см
    :param waste_percentage: процент на подрезку и брак
    :return: количество плиток
    """
    # Площадь одной плитки в м²
    tile_area = (tile_length / 100) * (tile_width / 100)
    
    # Количество плиток без запаса
    tiles_needed = area / tile_area
    
    # С запасом
    tiles_with_waste = tiles_needed * (1 + waste_percentage / 100)
    
    return {
        'tile_area_sqm': round(tile_area, 4),
        'tiles_exact': math.ceil(tiles_needed),
        'tiles_with_waste': math.ceil(tiles_with_waste),
        'waste_percentage': waste_percentage
    }


def calculate_rebar(length, width, spacing=0.2, layers=2):
    """
    Расчет арматуры для армирования.
    
    :param length: длина участка в метрах
    :param width: ширина участка в метрах
    :param spacing: шаг арматуры в метрах
    :param layers: количество слоев
    :return: общая длина арматуры
    """
    # Количество стержней вдоль длины
    bars_along_length = math.ceil(width / spacing) + 1
    # Количество стержней вдоль ширины
    bars_along_width = math.ceil(length / spacing) + 1
    
    # Общая длина для одного слоя
    length_one_layer = (bars_along_length * length) + (bars_along_width * width)
    
    # Общая длина для всех слоев
    total_length = length_one_layer * layers
    
    return {
        'bars_along_length': bars_along_length,
        'bars_along_width': bars_along_width,
        'total_length': round(total_length, 2),
        'spacing': spacing,
        'layers': layers
    }


def main_menu():
    """Главное меню программы."""
    while True:
        print("\n" + "="*50)
        print("🏗️  КАЛЬКУЛЯТОР СТРОИТЕЛЯ")
        print("="*50)
        print("1. 🧱 Расчет количества кирпича")
        print("2. 🏗️  Расчет объема бетона")
        print("3. 📐 Расчет параметров помещения")
        print("4. 🔲 Расчет количества плитки")
        print("5. 🔩 Расчет арматуры")
        print("6. Выход")
        print("="*50)
        
        choice = input("\nВыберите опцию (1-6): ").strip()
        
        if choice == '1':
            brick_calculator()
        elif choice == '2':
            concrete_calculator()
        elif choice == '3':
            room_calculator()
        elif choice == '4':
            tile_calculator()
        elif choice == '5':
            rebar_calculator()
        elif choice == '6':
            print("\n✅ До свидания! Удачной стройки! 🏠")
            break
        else:
            print("\n❌ Неверный выбор. Попробуйте снова.")


def brick_calculator():
    """Калькулятор кирпича."""
    print("\n" + "="*50)
    print("🧱 РАСЧЕТ КОЛИЧЕСТВА КИРПИЧА")
    print("="*50)
    
    try:
        length = float(input("Длина стены (м): "))
        height = float(input("Высота стены (м): "))
        width = float(input("Толщина стены (м): "))
        
        result = calculate_bricks(length, height, width)
        
        print("\n" + "-"*50)
        print(f"📊 Результаты:")
        print(f"   Площадь стены: {result['wall_area']:.2f} м²")
        print(f"   Объем кладки: {result['volume']:.2f} м³")
        print(f"   Кирпичей на м²: ~{result['bricks_per_sqm']} шт")
        print(f"   Всего кирпичей: {result['total_bricks']} шт")
        print("-"*50)
        
    except ValueError:
        print("\n❌ Ошибка: введите корректные числовые значения!")


def concrete_calculator():
    """Калькулятор бетона."""
    print("\n" + "="*50)
    print("🏗️  РАСЧЕТ ОБЪЕМА БЕТОНА")
    print("="*50)
    
    try:
        length = float(input("Длина (м): "))
        width = float(input("Ширина (м): "))
        thickness = float(input("Толщина/высота (м): "))
        
        result = calculate_concrete(length, width, thickness)
        
        print("\n" + "-"*50)
        print(f"📊 Результаты:")
        print(f"   Чистый объем: {result['volume']} м³")
        print(f"   С запасом 5%: {result['volume_with_reserve']} м³")
        print(f"   Размеры: {result['length']} x {result['width']} x {result['thickness']} м")
        print("-"*50)
        
    except ValueError:
        print("\n❌ Ошибка: введите корректные числовые значения!")


def room_calculator():
    """Калькулятор помещения."""
    print("\n" + "="*50)
    print("📐 РАСЧЕТ ПАРАМЕТРОВ ПОМЕЩЕНИЯ")
    print("="*50)
    
    try:
        length = float(input("Длина помещения (м): "))
        width = float(input("Ширина помещения (м): "))
        height = float(input("Высота помещения (м): "))
        
        windows = []
        print("\nВведите окна (или нажмите Enter для пропуска):")
        while True:
            win = input("Окно (ширина высота, м): ").strip()
            if not win:
                break
            w, h = map(float, win.split())
            windows.append((w, h))
        
        doors = []
        print("\nВведите двери (или нажмите Enter для пропуска):")
        while True:
            door = input("Дверь (ширина высота, м): ").strip()
            if not door:
                break
            w, h = map(float, door.split())
            doors.append((w, h))
        
        result = calculate_room_parameters(length, width, height, windows if windows else None, doors if doors else None)
        
        print("\n" + "-"*50)
        print(f"📊 Результаты:")
        print(f"   Площадь пола: {result['floor_area']} м²")
        print(f"   Площадь потолка: {result['ceiling_area']} м²")
        print(f"   Периметр: {result['perimeter']} м")
        print(f"   Площадь стен (общая): {result['gross_wall_area']} м²")
        print(f"   Площадь проемов: {result['openings_area']} м²")
        print(f"   Площадь стен (чистая): {result['net_wall_area']} м²")
        print(f"   Объем помещения: {result['room_volume']} м³")
        print("-"*50)
        
    except ValueError:
        print("\n❌ Ошибка: введите корректные числовые значения!")


def tile_calculator():
    """Калькулятор плитки."""
    print("\n" + "="*50)
    print("🔲 РАСЧЕТ КОЛИЧЕСТВА ПЛИТКИ")
    print("="*50)
    
    try:
        area = float(input("Площадь для укладки (м²): "))
        tile_length = float(input("Длина плитки (см): "))
        tile_width = float(input("Ширина плитки (см): "))
        waste = float(input("Процент на подрезку (по умолчанию 10): ") or "10")
        
        result = calculate_tiles(area, tile_length, tile_width, waste)
        
        print("\n" + "-"*50)
        print(f"📊 Результаты:")
        print(f"   Площадь одной плитки: {result['tile_area_sqm']} м²")
        print(f"   Точное количество: {result['tiles_exact']} шт")
        print(f"   С запасом {result['waste_percentage']}%: {result['tiles_with_waste']} шт")
        print("-"*50)
        
    except ValueError:
        print("\n❌ Ошибка: введите корректные числовые значения!")


def rebar_calculator():
    """Калькулятор арматуры."""
    print("\n" + "="*50)
    print("🔩 РАСЧЕТ АРМАТУРЫ")
    print("="*50)
    
    try:
        length = float(input("Длина участка (м): "))
        width = float(input("Ширина участка (м): "))
        spacing = float(input("Шаг арматуры (м, по умолчанию 0.2): ") or "0.2")
        layers = int(input("Количество слоев (по умолчанию 2): ") or "2")
        
        result = calculate_rebar(length, width, spacing, layers)
        
        print("\n" + "-"*50)
        print(f"📊 Результаты:")
        print(f"   Стержней вдоль длины: {result['bars_along_length']} шт")
        print(f"   Стержней вдоль ширины: {result['bars_along_width']} шт")
        print(f"   Шаг арматуры: {result['spacing']} м")
        print(f"   Количество слоев: {result['layers']}")
        print(f"   Общая длина арматуры: {result['total_length']} м")
        print("-"*50)
        
    except ValueError:
        print("\n❌ Ошибка: введите корректные числовые значения!")


if __name__ == "__main__":
    main_menu()
