Вот примеры вызовов `pixelate.py` с файлом `girl.png`, покрывающие основные комбинации аргументов (всего 30 вариантов):

### 1. Базовые варианты (разные методы усреднения)
```bash
# Цветные режимы
python pixelate.py girl.png --averating amac --
python pixelate.py girl.png --averating meav
python pixelate.py girl.png --averating aocs-hsv
python pixelate.py girl.png --averating aocs-lab
python pixelate.py girl.png --averating abdc

# Градации серого
python pixelate.py girl.png --mode-grayscale --averating gray-rgb
python pixelate.py girl.png --mode-grayscale --averating gray-wav
python pixelate.py girl.png --mode-grayscale --averating gray-hsv-v

# Чёрно-белые
python pixelate.py girl.png --mode-black-white --averating bin-tc
python pixelate.py girl.png --mode-black-white --averating bin-mb
```

### 2. Разные размеры блоков
```bash
python pixelate.py girl.png --point-w 5 --point-h 5
python pixelate.py girl.png --point-w 20 --point-h 10
python pixelate.py girl.png --point-w 8 --point-h 8 --averating meav
```

### 3. Изменение размеров изображения
```bash
python pixelate.py girl.png --width 400
python pixelate.py girl.png --height 300
python pixelate.py girl.png --width 800 --height 600
python pixelate.py girl.png --zoom 0.5  # Уменьшить в 1.5 раза
python pixelate.py girl.png --zoom -0.3 # Уменьшить на 30%
```

### 4. Регулировка яркости
```bash
python pixelate.py girl.png --bright 50   # Увеличить яркость
python pixelate.py girl.png --bright -30 # Уменьшить яркость
python pixelate.py girl.png --bright 100 --averating aocs-hsv
```

### 5. Разные форматы вывода
```bash
python pixelate.py girl.png --out-type jpg
python pixelate.py girl.png --out-type png --out-name pixelated_girl
python pixelate.py girl.png --out-prefix art_ --out-type webp
```

### 6. Генерация JSON-матриц
```bash
python pixelate.py girl.png --matrix-json aoa
python pixelate.py girl.png --matrix-json hex
python pixelate.py girl.png --matrix-json b64 --averating meav
```

### 7. Текстовые матрицы
```bash
python pixelate.py girl.png --matrix-txt rgb
python pixelate.py girl.png --matrix-txt hex --mode-grayscale
python pixelate.py girl.png --matrix-txt ansi --point-w 15
```

### 8. Комбинированные примеры
```bash
python pixelate.py girl.png --width 500 --averating abdc --point-w 12 --bright 20 --out-name girl_abdc
python pixelate.py girl.png --mode-black-white --averating blwt-tc --matrix-json sla --matrix-txt sdd
python pixelate.py girl.png --zoom 0.2 --averating gray-lab-l --console --out-type gif
```

### 9. Консольный вывод
```bash
python pixelate.py girl.png --console
python pixelate.py girl.png --averating meav --point-w 8 --console
python pixelate.py girl.png --mode-black-white --console
```

### 10. Максимально полный пример
```bash
python pixelate.py girl.png \
  --width 600 \
  --height 400 \
  --averating aocs-lab \
  --point-w 15 \
  --point-h 15 \
  --bright 25 \
  --out-name lab_style \
  --out-type jpg \
  --matrix-json hex \
  --matrix-txt ansi \
  --console
```

Эти примеры покрывают:
- Все основные методы усреднения (`--averating`)
- Все режимы (`--mode-color`, `--mode-grayscale`, `--mode-black-white`)
- Разные размеры блоков и изображений
- Форматы вывода
- Дополнительные файлы (JSON/TXT)
- Консольный вывод

Для тестирования можно выбрать по 1-2 примера из каждой группы.