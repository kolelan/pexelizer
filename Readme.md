# Pixelate Image Processor

## Описание
Программа `pixelate.py` предназначена для обработки изображений с эффектом пикселизации. Она поддерживает различные методы усреднения цветов, преобразование в черно-белый или grayscale режимы, а также генерацию матриц данных в форматах JSON и TXT.

## Установка
1. Убедитесь, что у вас установлен Python 3.6 или выше.
2. Установите необходимые зависимости:
   ```bash
   pip install Pillow numpy scikit-learn opencv-python
   ```

## Использование
```bash
python pixelate.py <image_path> [опции]
```

### Основные опции
- `--averating`: Метод усреднения цветов (по умолчанию: `meav`). Доступные варианты:
  - Для цветного режима: `amac`, `meav`, `aocs-hsv`, `aocs-lab`, `abdc`.
  - Для grayscale: `gray-rgb`, `gray-wav`, `gray-hsv-v`, `gray-hsv-s`, `gray-hsv-h`, `gray-lab-l`.
  - Для черно-белого режима: `bin-tc`, `bin-mb`, `blwt`, `blwt-tc`.
- `--width` и `--height`: Установка ширины и высоты выходного изображения.
- `--zoom`: Масштабирование изображения (положительное для увеличения, отрицательное для уменьшения).
- `--point-w` и `--point-h`: Размер блока пикселизации (по умолчанию: 10x10).
- `--bright`: Коррекция яркости (-255 до 255).
- `--mode-color`, `--mode-black-white`, `--mode-grayscale`: Выбор режима обработки изображения.

### Выходные файлы
- `--out-prefix`: Префикс для имени выходного файла.
- `--out-name`: Имя выходного файла.
- `--out-type`: Расширение выходного файла (например, `png`, `jpg`).
- `--matrix-json`: Генерация JSON-матрицы с данными изображения (форматы: `aoa`, `sla`, `slo`, `b64`, `hex`, `rgb`, `cmyk`).
- `--matrix-txt`: Генерация текстовой матрицы (форматы: `rgb`, `hex`, `ansi`, `sdd`, `sac`).
- `--console`: Вывод превью изображения в консоль.

## Примеры
1. Пикселизация изображения с размером блока 15x15 и сохранение в PNG:
   ```bash
   python pixelate.py input.jpg --point-w 15 --point-h 15
   ```

2. Преобразование в черно-белый режим с выводом JSON-матрицы:
   ```bash
   python pixelate.py input.jpg --mode-black-white --matrix-json
   ```

3. Grayscale с коррекцией яркости и выводом в консоль:
   ```bash
   python pixelate.py input.jpg --mode-grayscale --bright 50 --console
   ```
## Примеры работы скрипта с разными параметрами пикселизации

Следующие команды демонстрируют обработку изображения с разным размером блоков пикселизации:

```bash
# color
python .\pixelate.py .\example\girl.png --width 500 --point-w 5 --out-name "example/girl/girl-w500-p5"
python .\pixelate.py .\example\girl.png --width 500 --point-w 10 --out-name "example/girl/girl-w500-p10"
python .\pixelate.py .\example\girl.png --width 500 --point-w 15 --out-name "example/girl/girl-w500-p15"
# grayscale
python .\pixelate.py .\example\girl.png --width 500 --point-w 5 --out-name "example/girl/girl-g-w500-p5" --mode-grayscale
python .\pixelate.py .\example\girl.png --width 500 --point-w 10 --out-name "example/girl/girl-g-w500-p10" --mode-grayscale
python .\pixelate.py .\example\girl.png --width 500 --point-w 15 --out-name "example/girl/girl-g-w500-p15" --mode-grayscale
# black-white
python .\pixelate.py .\example\girl.png --width 500 --point-w 5 --out-name "example/girl/girl-bw-w500-p5" --mode-black-white --bright -10
python .\pixelate.py .\example\girl.png --width 500 --point-w 10 --out-name "example/girl/girl-bw-w500-p10" --mode-black-white --bright -10
python .\pixelate.py .\example\girl.png --width 500 --point-w 15 --out-name "example/girl/girl-bw-w500-p15" --mode-black-white --bright -10
```

### Результаты обработки исходного изображения
![Исходное изображение](https://github.com/kolelan/pexelizer/blob/main/example/girl.png)

| Блок 5x5                                                                                        | Блок 10x10 | Блок 15x15                                                                                         |
|-------------------------------------------------------------------------------------------------|------------|----------------------------------------------------------------------------------------------------|
| ![girl-w500-p5](https://github.com/kolelan/pexelizer/blob/main/example/girl/girl-w500-p5.png)   | ![girl-w500-p10](https://github.com/kolelan/pexelizer/blob/main/example/girl/girl-w500-p10.png) | ![girl-w500-p15](https://github.com/kolelan/pexelizer/blob/main/example/girl/girl-w500-p15.png)    |
| ![girl-w500-p5](https://github.com/kolelan/pexelizer/blob/main/example/girl/girl-g-w500-p5.png) | ![girl-w500-p10](https://github.com/kolelan/pexelizer/blob/main/example/girl/girl-g-w500-p10.png) | ![girl-w500-p15](https://github.com/kolelan/pexelizer/blob/main/example/girl/girl-g-w500-p15.png)  |
| ![girl-w500-p5](https://github.com/kolelan/pexelizer/blob/main/example/girl/girl-bw-w500-p5.png)   | ![girl-w500-p10](https://github.com/kolelan/pexelizer/blob/main/example/girl/girl-bw-w500-p10.png) | ![girl-w500-p15](https://github.com/kolelan/pexelizer/blob/main/example/girl/girl-bw-w500-p15.png) |

**Примечания:**
1. Все изображения приведены к ширине 500px
2. Размер блоков пикселизации варьируется от 5x5 до 15x15 пикселей
3. Имена выходных файлов соответствуют параметрам обработки:
   - `w500` - ширина 500px
   - `p5`/`p10`/`p15` - размер блока пикселизации
4. Изображения сохраняются в поддиректории `example/girl/` проекта

## Лицензия
Программа распространяется под лицензией MIT. Используйте на свой страх и риск.
