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
    return img


def main(args):
    pydiffvg.set_device(th.device('cuda:1'))

    # Load SVG
    svg_path = os.path.join(args.svg_path)
    save_svg_path = svg_path.replace('.svg', '_resave.svg')
    canvas_width, canvas_height, shapes, shape_groups = pydiffvg.svg_to_scene(svg_path)
    print("canvas_width", canvas_width)
    print("canvas_height", canvas_height)
    print("shapes", shapes)
    print("shape_groups", shape_groups)
    pydiffvg.save_svg_paths_only(save_svg_path, canvas_width, canvas_height, shapes, shape_groups)


    # Save initial state
    ref = render(canvas_width, canvas_height, shapes, shape_groups)
    # pydiffvg.imwrite(ref.cpu(), args.out_path, gamma=2.2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("svg_path", help="source SVG path")
    parser.add_argument("out_path", help="output image path")
    args = parser.parse_args()
    main(args)
