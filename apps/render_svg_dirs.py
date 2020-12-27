"""
Simple utility to render an .svg to a .png
"""
import os
import argparse
import pydiffvg
import torch as th


def render(canvas_width, canvas_height, shapes, shape_groups):
    _render = pydiffvg.RenderFunction.apply
    scene_args = pydiffvg.RenderFunction.serialize_scene(
        canvas_width, canvas_height, shapes, shape_groups)
    img = _render(canvas_width,  # width
                  canvas_height,  # height
                  2,   # num_samples_x
                  2,   # num_samples_y
                  0,   # seed
                  None,
                  *scene_args)
    # print(img.size())
    img = img[:, :, 3:4] * img[:, :, :3] + th.ones(img.shape[0], img.shape[1], 3, device=pydiffvg.get_device()) * (1 - img[:, :, 3:4])
    return img


def main(svg_dirs):
    pydiffvg.set_device(th.device('cuda:1'))

    assert os.path.exists(svg_dirs)
    svg_files = os.listdir(svg_dirs)
    for svg_file in svg_files:
        if '.svg' not in svg_file:
            continue
        svg_file_path = os.path.join(svg_dirs, svg_file)
        out_file_path = svg_file_path.replace('.svg', '.png')
        # Load SVG
        canvas_width, canvas_height, shapes, shape_groups = pydiffvg.svg_to_scene(svg_file_path)
        # Save initial state
        ref = render(canvas_width, canvas_height, shapes, shape_groups)
        pydiffvg.imwrite(ref.cpu(), out_file_path, gamma=2.2)


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("svg_dirs", help="source SVG path")
    # args = parser.parse_args()
    styles = ['4', '9', '14', '30']
    for s in styles:
        svg_dirs = f'partial_svg_diffvg/style_{s}'
        main(svg_dirs)
