svg_path = 'partial_svg_diffvg/style_4/real_C.svg'

with open(svg_path) as f:
    lines = f.readlines()
    new_lines = []
    for l in lines:
        strs = l.split()
        converted = []
        for s in strs:
            try:
                ss = float(s)
                ss = ss * 10.0
                converted.append(str(ss))
            except Exception:
                converted.append(s)
        new_line = ' '.join(converted)
        new_line = new_line.replace('50px', '500px')
        new_line = new_line.replace('24"', '240"')
        new_lines.append(new_line)

scale_svg_path = svg_path.replace('.svg', '_scale.svg')
f = open(scale_svg_path, 'w')
for new_line in new_lines:
    f.write(new_line)
