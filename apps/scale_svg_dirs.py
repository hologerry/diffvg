import os
import random

svg_dirs = 'random_svgs'
chars = "A"
types = ['fake']
target_size = 64
# scalar = target_size / 24

def multiply(num_str):
    is_number = False
    scalar = random.randint(-64, 64) * 1.0
    try:
        num = str(float(num_str) * scalar)
        num = str(scalar)
        is_number = True
    except Exception:
        num = num_str
    return num, is_number

for t in types:
    for c in chars:
        svg_path = os.path.join(svg_dirs, f'{t}_{c}.svg')
        with open(svg_path) as f:
            lines = f.readlines()
        new_lines = []
        for l in lines:
            strs = l.split()
            converted = []
            for s in strs:
                num, is_number = multiply(s)
                if is_number:
                    converted.append(num)
                else:
                    numstrs = num.split('"')
                    new_num = []
                    for ns in numstrs:
                        new_num.append(multiply(ns)[0])
                    converted.append('"'.join(new_num))

            new_line = ' '.join(converted)
            # new_line = new_line.replace('50px', f'{50*scalar}px')
            new_line = new_line.replace('50px', f'{133.33333}px')
            # new_line = new_line.replace('24"', f'{24*scalar}"')
            new_lines.append(new_line)

        scale_svg_path = svg_path.replace('.svg', f'_scale_{target_size}.svg')
        f = open(scale_svg_path, 'w')
        for new_line in new_lines:
            f.write(new_line)
