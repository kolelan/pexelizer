import argparse
import os
import json
import base64
import numpy as np
from PIL import Image, ImageOps, ImageDraw
from datetime import datetime
from sklearn.cluster import KMeans
import cv2
from collections import defaultdict


def resize_image(image, width=None, height=None, zoom=None):
    original_width, original_height = image.size

    if zoom is not None:
        if zoom > 0:
            # Увеличение
            new_width = int(original_width * (1 + zoom))
            new_height = int(original_height * (1 + zoom))
        else:
            # Уменьшение
            new_width = int(original_width / (1 - zoom))
            new_height = int(original_height / (1 - zoom))
    elif width is not None and height is not None:
        new_width, new_height = width, height
    elif width is not None:
        ratio = width / original_width
        new_width = width
        new_height = int(original_height * ratio)
    elif height is not None:
        ratio = height / original_height
        new_height = height
        new_width = int(original_width * ratio)
    else:
        return image

    return image.resize((new_width, new_height), Image.LANCZOS)


def apply_brightness(image, brightness):
    if brightness == 0:
        return image
    hsv = image.convert('HSV')
    h, s, v = hsv.split()
    v = v.point(lambda x: min(255, max(0, x + brightness)))
    hsv = Image.merge('HSV', (h, s, v))
    return hsv.convert('RGB')


def average_block_amac(block):
    """Arithmetic mean across channels"""
    return tuple(np.mean(block, axis=(0, 1)).astype(int))

def average_block_meav(block):
    """The median averaging"""
    return tuple(np.median(block, axis=(0, 1)).astype(int))

def average_block_aocs_hsv(block):
    """Averaging in HSV color space"""
    hsv_block = cv2.cvtColor(block, cv2.COLOR_RGB2HSV)
    h, s, v = cv2.split(hsv_block)
    avg_h = np.mean(h)
    avg_s = np.mean(s)
    avg_v = np.mean(v)
    avg_color = np.array([avg_h, avg_s, avg_v], dtype=np.uint8).reshape(1, 1, 3)
    rgb_color = cv2.cvtColor(avg_color, cv2.COLOR_HSV2RGB)
    return tuple(rgb_color[0, 0])


def average_block_aocs_lab(block):
    lab_block = cv2.cvtColor(block, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab_block)
    avg_l = np.mean(l)
    avg_a = np.mean(a)
    avg_b = np.mean(b)
    avg_color = np.array([avg_l, avg_a, avg_b], dtype=np.uint8).reshape(1, 1, 3)
    rgb_color = cv2.cvtColor(avg_color, cv2.COLOR_LAB2RGB)
    return tuple(rgb_color[0, 0])


def average_block_abdc(block):
    """Averaging by the dominant color using k-means"""
    # Приводим блок к правильной форме (N*M, 3) - игнорируем альфа-канал если есть
    pixels = block.reshape(-1, block.shape[-1])[:, :3]  # Берем только RGB
    if len(pixels) < 1:
        return (0, 0, 0)

    # Применяем k-means для 1 кластера (доминирующий цвет)
    kmeans = KMeans(n_clusters=1, random_state=0, n_init=10).fit(pixels)
    dominant_color = kmeans.cluster_centers_[0].round().astype(int).tolist()
    return tuple(dominant_color)


def average_block_gray_rgb(block):
    gray_value = np.mean(block)
    return (gray_value, gray_value, gray_value)


def average_block_gray_wav(block):
    r, g, b = np.mean(block, axis=(0, 1))
    gray_value = 0.299 * r + 0.587 * g + 0.114 * b
    return (gray_value, gray_value, gray_value)


def average_block_gray_hsv_v(block):
    hsv_block = cv2.cvtColor(block, cv2.COLOR_RGB2HSV)
    v = hsv_block[:, :, 2]
    gray_value = np.mean(v)
    return (gray_value, gray_value, gray_value)


def average_block_gray_hsv_s(block):
    hsv_block = cv2.cvtColor(block, cv2.COLOR_RGB2HSV)
    s = hsv_block[:, :, 1]
    gray_value = np.mean(s)
    return (gray_value, gray_value, gray_value)


def average_block_gray_hsv_h(block):
    hsv_block = cv2.cvtColor(block, cv2.COLOR_RGB2HSV)
    h = hsv_block[:, :, 0]
    gray_value = np.mean(h)
    return (gray_value, gray_value, gray_value)


def average_block_gray_lab_l(block):
    lab_block = cv2.cvtColor(block, cv2.COLOR_RGB2LAB)
    l = lab_block[:, :, 0]
    gray_value = np.mean(l)
    return (gray_value, gray_value, gray_value)


def average_block_bin_tc(block, threshold=128):
    gray_block = average_block_gray_wav(block)
    gray_value = gray_block[0]
    bw_value = 255 if gray_value >= threshold else 0
    return (bw_value, bw_value, bw_value)


def average_block_bin_mb(block):
    gray_block = average_block_gray_wav(block)
    gray_value = gray_block[0]
    bw_value = 255 if gray_value >= 128 else 0
    return (bw_value, bw_value, bw_value)


def average_block_gray_tc(block):
    gray_value = np.mean(block)
    return (gray_value, gray_value, gray_value)


def average_block_gray_mb(block):
    gray_value = np.median(block)
    return (gray_value, gray_value, gray_value)


def average_block_blwt(block):
    white_pixels = np.sum(block >= 128)
    total_pixels = block.size // 3
    gray_value = 255 * (white_pixels / total_pixels)
    return (gray_value, gray_value, gray_value)


def average_block_blwt_tc(block, threshold=128):
    gray_block = average_block_blwt(block)
    gray_value = gray_block[0]
    bw_value = 255 if gray_value >= threshold else 0
    return (bw_value, bw_value, bw_value)


def pixelate_image(image, block_width=10, block_height=10, averaging_method='meav', mode='color'):
    width, height = image.size
    pixelated = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(pixelated)

    for y in range(0, height, block_height):
        for x in range(0, width, block_width):
            box = (x, y, min(x + block_width, width), min(y + block_height, height))
            block = image.crop(box)
            block_array = np.array(block)

            # Нормализация формата блока
            if block_array.ndim == 2:  # Grayscale (H,W) -> (H,W,3)
                block_array = np.stack([block_array]*3, axis=-1)
            elif block_array.shape[-1] == 4:  # RGBA -> RGB
                block_array = block_array[..., :3]

            # Убедимся, что значения в пределах 0-255
            block_array = np.clip(block_array, 0, 255).astype(np.uint8)

            # Выбор метода усреднения
            if mode == 'grayscale':
                if averaging_method == 'abdc':  # Особый случай для abdc в grayscale
                        color = average_block_abdc(block_array)
                        gray = int(0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2])
                        avg_color = (gray, gray, gray)
                else:
                    if averaging_method == 'gray-rgb':
                        avg_color = average_block_gray_rgb(block_array)
                    elif averaging_method == 'gray-wav':
                        avg_color = average_block_gray_wav(block_array)
                    elif averaging_method == 'gray-hsv-v':
                        avg_color = average_block_gray_hsv_v(block_array)
                    elif averaging_method == 'gray-hsv-s':
                        avg_color = average_block_gray_hsv_s(block_array)
                    elif averaging_method == 'gray-hsv-h':
                        avg_color = average_block_gray_hsv_h(block_array)
                    elif averaging_method == 'gray-lab-l':
                        avg_color = average_block_gray_lab_l(block_array)
                    elif averaging_method == 'gray-tc':
                        avg_color = average_block_gray_tc(block_array)
                    elif averaging_method == 'gray-mb':
                        avg_color = average_block_gray_mb(block_array)
                    else:
                        avg_color = average_block_gray_wav(block_array)

            elif mode == 'black-white':
                if averaging_method == 'bin-tc':
                    avg_color = average_block_bin_tc(block_array)
                elif averaging_method == 'bin-mb':
                    avg_color = average_block_bin_mb(block_array)
                elif averaging_method == 'blwt':
                    avg_color = average_block_blwt(block_array)
                elif averaging_method == 'blwt-tc':
                    avg_color = average_block_blwt_tc(block_array)
                else:
                    avg_color = average_block_blwt_tc(block_array)

            else:  # color mode
                if averaging_method == 'amac':
                    avg_color = average_block_amac(block_array)
                elif averaging_method == 'meav':
                    avg_color = average_block_meav(block_array)
                elif averaging_method == 'aocs-hsv':
                    avg_color = average_block_aocs_hsv(block_array)
                elif averaging_method == 'aocs-lab':
                    avg_color = average_block_aocs_lab(block_array)
                elif averaging_method == 'abdc':
                    avg_color = average_block_abdc(block_array)
                else:
                    avg_color = average_block_meav(block_array)
            # Приведение к целым числам
            avg_color = tuple(int(c) for c in avg_color)
            draw.rectangle(box, fill=avg_color)

    return pixelated


def generate_json_matrix(image, matrix_type='rgb'):
    width, height = image.size
    pixels = list(image.getdata())

    if matrix_type == 'aoa':
        pixel_matrix = []
        for y in range(height):
            row = []
            for x in range(width):
                pixel = pixels[y * width + x]
                row.append(list(pixel))
            pixel_matrix.append(row)
        json_data = {
            "width": width,
            "height": height,
            "pixels": pixel_matrix
        }
    elif matrix_type == 'sla':
        flat_pixels = []
        for pixel in pixels:
            flat_pixels.extend(pixel)
        json_data = {
            "width": width,
            "height": height,
            "channels": len(pixels[0]),
            "pixels": flat_pixels
        }
    elif matrix_type == 'slo':
        pixel_list = []
        for y in range(height):
            for x in range(width):
                pixel = pixels[y * width + x]
                pixel_dict = {
                    "x": x,
                    "y": y,
                    "r": pixel[0],
                    "g": pixel[1],
                    "b": pixel[2]
                }
                if len(pixel) > 3:
                    pixel_dict["a"] = pixel[3]
                pixel_list.append(pixel_dict)
        json_data = {
            "width": width,
            "height": height,
            "pixels": pixel_list
        }
    elif matrix_type == 'b64':
        img_bytes = image.tobytes()
        base64_data = base64.b64encode(img_bytes).decode('utf-8')
        json_data = {
            "width": width,
            "height": height,
            "format": "RGB",
            "data": base64_data
        }
    elif matrix_type == 'hex':
        pixel_matrix = []
        for y in range(height):
            row = []
            for x in range(width):
                pixel = pixels[y * width + x]
                hex_color = "#{:02x}{:02x}{:02x}".format(*pixel[:3])
                row.append(hex_color)
            pixel_matrix.append(row)
        json_data = {
            "width": width,
            "height": height,
            "pixels": pixel_matrix
        }
    elif matrix_type == 'rgb':
        pixel_matrix = []
        for y in range(height):
            row = []
            for x in range(width):
                pixel = pixels[y * width + x]
                rgb_str = " ".join(map(str, pixel[:3]))
                row.append(rgb_str)
            pixel_matrix.append(row)
        json_data = {
            "width": width,
            "height": height,
            "pixels": pixel_matrix
        }
    elif matrix_type == 'cmyk':
        pixel_matrix = []
        for y in range(height):
            row = []
            for x in range(width):
                pixel = pixels[y * width + x]
                r, g, b = pixel[:3]
                k = 1 - max(r / 255, g / 255, b / 255)
                if k == 1:
                    c = m = y = 0
                else:
                    c = (1 - r / 255 - k) / (1 - k)
                    m = (1 - g / 255 - k) / (1 - k)
                    y = (1 - b / 255 - k) / (1 - k)
                cmyk_str = " ".join(map(str, [int(c * 100), int(m * 100), int(y * 100), int(k * 100)]))
                row.append(cmyk_str)
            pixel_matrix.append(row)
        json_data = {
            "width": width,
            "height": height,
            "pixels": pixel_matrix
        }
    else:
        pixel_matrix = []
        for y in range(height):
            row = []
            for x in range(width):
                pixel = pixels[y * width + x]
                rgb_str = " ".join(map(str, pixel[:3]))
                row.append(rgb_str)
            pixel_matrix.append(row)
        json_data = {
            "width": width,
            "height": height,
            "pixels": pixel_matrix
        }

    return json_data


def generate_txt_matrix(image, matrix_type='rgb'):
    width, height = image.size
    pixels = list(image.getdata())
    txt_lines = []

    if matrix_type == 'rgb':
        txt_lines.append(f"# Размеры: ширина={width}, высота={height}")
        for y in range(height):
            line = []
            for x in range(width):
                pixel = pixels[y * width + x]
                rgb_str = ",".join(map(str, pixel[:3]))
                line.append(rgb_str)
            txt_lines.append("   ".join(line))
    elif matrix_type == 'hex':
        txt_lines.append(f"# Размеры: {width}x{height}")
        for y in range(height):
            line = []
            for x in range(width):
                pixel = pixels[y * width + x]
                hex_color = "#{:02x}{:02x}{:02x}".format(*pixel[:3])
                line.append(hex_color)
            txt_lines.append(" ".join(line))
    elif matrix_type == 'ansi':
        color_map = {
            (255, 0, 0): "🟥",
            (0, 255, 0): "🟩",
            (0, 0, 255): "🟦",
            (255, 255, 0): "🟨",
            (0, 255, 255): "🟧",
            (255, 0, 255): "🟪",
            (255, 255, 255): "⬜",
            (0, 0, 0): "⬛"
        }
        for y in range(height):
            line = []
            for x in range(width):
                pixel = tuple(pixels[y * width + x][:3])
                closest_color = min(color_map.keys(), key=lambda c: sum((a - b) ** 2 for a, b in zip(c, pixel)))
                line.append(color_map[closest_color])
            txt_lines.append(" ".join(line))
    elif matrix_type == 'sdd':
        density_chars = "@%#*+=-:. "
        txt_lines.append(f"# Размеры: ширина={width}, высота={height}")
        for y in range(height):
            line = []
            for x in range(width):
                pixel = pixels[y * width + x]
                gray_value = 0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2]
                char_index = int((gray_value / 255) * (len(density_chars) - 1))
                line.append(density_chars[char_index])
            txt_lines.append(" ".join(line))
    elif matrix_type == 'sac':
        color_chars = {
            (255, 0, 0): 'R',
            (0, 255, 0): 'G',
            (0, 0, 255): 'B',
            (255, 255, 0): 'Y',
            (0, 255, 255): 'C',
            (255, 0, 255): 'M',
            (255, 255, 255): 'W',
            (0, 0, 0): 'K'
        }
        for y in range(height):
            line = []
            for x in range(width):
                pixel = tuple(pixels[y * width + x][:3])
                closest_color = min(color_chars.keys(), key=lambda c: sum((a - b) ** 2 for a, b in zip(c, pixel)))
                line.append(color_chars[closest_color])
            txt_lines.append(" ".join(line))

    return "\n".join(txt_lines)


def print_console_preview(image):
    width, height = image.size
    pixels = list(image.getdata())
    color_map = {
        (255, 0, 0): "🟥",
        (0, 255, 0): "🟩",
        (0, 0, 255): "🟦",
        (255, 255, 0): "🟨",
        (0, 255, 255): "🟧",
        (255, 0, 255): "🟪",
        (255, 255, 255): "⬜",
        (0, 0, 0): "⬛"
    }
    for y in range(height):
        line = []
        for x in range(width):
            pixel = tuple(pixels[y * width + x][:3])
            closest_color = min(color_map.keys(), key=lambda c: sum((a - b) ** 2 for a, b in zip(c, pixel)))
            line.append(color_map[closest_color])
        print(" ".join(line))


def main():
    parser = argparse.ArgumentParser(description='Pixelate an image with various options.')
    parser.add_argument('image_path', help='Path to the image file to process')
    parser.add_argument('--averating', choices=['amac', 'meav', 'aocs-hsv', 'aocs-lab', 'abdc',
                                                'gray-rgb', 'gray-wav', 'gray-hsv-v', 'gray-hsv-s', 'gray-hsv-h',
                                                'gray-lab-l',
                                                'bin-tc', 'bin-mb', 'gray-tc', 'gray-mb', 'blwt', 'blwt-tc'],
                        default='meav', help='Averaging method to use')
    parser.add_argument('--width', type=int, help='Output image width in pixels')
    parser.add_argument('--height', type=int, help='Output image height in pixels')
    parser.add_argument('--zoom', type=float, help='Zoom factor (positive to enlarge, negative to shrink)')
    parser.add_argument('--point-w', type=int, default=10, help='Block width in pixels (default: 10)')
    parser.add_argument('--point-h', type=int, default=10, help='Block height in pixels (default: 10)')
    parser.add_argument('--mode-color', action='store_true', help='Output in color mode')
    parser.add_argument('--mode-black-white', action='store_true', help='Output in black and white mode')
    parser.add_argument('--mode-grayscale', action='store_true', help='Output in grayscale mode')
    parser.add_argument('--bright', type=int, default=0, help='Brightness adjustment (-255 to 255)')
    parser.add_argument('--out-prefix', help='Prefix for output filename')
    parser.add_argument('--out-name', help='Output filename')
    parser.add_argument('--out-type', help='Output file extension')
    parser.add_argument('--matrix-json', nargs='?', const='rgb',
                        choices=['aoa', 'sla', 'slo', 'b64', 'hex', 'rgb', 'cmyk'],
                        help='Generate JSON matrix file with specified format')
    parser.add_argument('--matrix-txt', choices=['rgb', 'hex', 'ansi', 'sdd', 'sac'],
                        help='Generate TXT matrix file with specified format')
    parser.add_argument('--console', action='store_true', help='Print ANSI-color preview to console')

    args = parser.parse_args()

    # Determine output mode
    if args.mode_black_white:
        mode = 'black-white'
        if args.averating == 'meav':
            args.averating = 'blwt-tc'
    elif args.mode_grayscale:
        mode = 'grayscale'
        if args.averating == 'meav':
            args.averating = 'gray-wav'
    else:
        mode = 'color'

    # Open image
    try:
        image = Image.open(args.image_path)
    except Exception as e:
        print(f"Error opening image: {e}")
        return

    # Resize image
    image = resize_image(image, args.width, args.height, args.zoom)

    # Apply brightness
    if args.bright != 0:
        image = apply_brightness(image, args.bright)

    # Pixelate image
    pixelated = pixelate_image(image, args.point_w, args.point_h, args.averating, mode)

    # Determine output filename
    if args.out_name:
        output_filename = args.out_name
    else:
        base_name = os.path.splitext(os.path.basename(args.image_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = args.out_prefix if args.out_prefix else 'pic_'
        output_filename = f"{prefix}{base_name}_{timestamp}"

    # Determine output extension
    if args.out_type:
        output_ext = args.out_type
    else:
        output_ext = os.path.splitext(args.image_path)[1][1:] or 'png'

    # Save pixelated image
    if args.out_type:
        output_ext = args.out_type
    else:
        output_ext = os.path.splitext(args.image_path)[1][1:] or 'png'

    if args.out_name:
        output_filename = f"{args.out_name}.{output_ext}"
    else:
        base_name = os.path.splitext(os.path.basename(args.image_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = args.out_prefix if args.out_prefix else 'pic_'
        output_filename = f"{prefix}{base_name}_{timestamp}.{output_ext}"

    output_path = output_filename  # Убираем автоматическое добавление .png
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    pixelated.save(output_path)
    print(f"Pixelated image saved to {output_path}")

    # Generate JSON matrix if requested
    if args.matrix_json:
        json_data = generate_json_matrix(pixelated, args.matrix_json)
        json_path = f"{output_filename}.json"
        with open(json_path, 'w') as f:
            json.dump(json_data, f, indent=2)
        print(f"JSON matrix saved to {json_path}")

    # Generate TXT matrix if requested
    if args.matrix_txt:
        txt_data = generate_txt_matrix(pixelated, args.matrix_txt)
        txt_path = f"{output_filename}.txt"
        with open(txt_path, 'w') as f:
            f.write(txt_data)
        print(f"TXT matrix saved to {txt_path}")

    # Print console preview if requested
    if args.console:
        print("\nConsole preview:")
        print_console_preview(pixelated)


if __name__ == "__main__":
    main()