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


