import pydiffvg
import argparse
import ttools.modules
import torch
import skimage.io

gamma = 1.0


def main(target_path, svg_path, output_dir, num_iter=1000, use_lpips_loss=False):
    perception_loss = ttools.modules.LPIPS().to(pydiffvg.get_device())

    target = torch.from_numpy(skimage.io.imread(target_path, as_gray=False, pilmode="RGB")).to(torch.float32) / 255.0
    print("target", target.size())
    target = target.pow(gamma)
    target = target.to(pydiffvg.get_device())
    target = target.unsqueeze(0)
    target = target.permute(0, 3, 1, 2)  # NHWC -> NCHW

    canvas_width, canvas_height, shapes, shape_groups = \
        pydiffvg.svg_to_scene(svg_path)
    scene_args = pydiffvg.RenderFunction.serialize_scene(
        canvas_width, canvas_height, shapes, shape_groups)

    render = pydiffvg.RenderFunction.apply
    img = render(canvas_width,  # width
                 canvas_height,  # height
                 2,   # num_samples_x
                 2,   # num_samples_y
                 0,   # seed
                 None,  # bg
                 *scene_args)
    # The output image is in linear RGB space. Do Gamma correction before saving the image.
    pydiffvg.imwrite(img.cpu(), f'{output_dir}/init.png', gamma=gamma)

    points_vars = []
    for path in shapes:
        path.points.requires_grad = True
        points_vars.append(path.points)
    color_vars = {}
    for group in shape_groups:
        group.fill_color.requires_grad = True
        color_vars[group.fill_color.data_ptr()] = group.fill_color
    color_vars = list(color_vars.values())

    # Optimize
    points_optim = torch.optim.Adam(points_vars, lr=1.0)
    color_optim = torch.optim.Adam(color_vars, lr=0.01)

    # Adam iterations.
    for t in range(num_iter):
        print('iteration:', t)
        points_optim.zero_grad()
        color_optim.zero_grad()
        # Forward pass: render the image.
        scene_args = pydiffvg.RenderFunction.serialize_scene(
            canvas_width, canvas_height, shapes, shape_groups)
        img = render(canvas_width,  # width
                     canvas_height,  # height
                     2,   # num_samples_x
                     2,   # num_samples_y
                     0,   # seed
                     None,  # bg
                     *scene_args)
        # Compose img with white background
        img = img[:, :, 3:4] * img[:, :, :3] + torch.ones(img.shape[0], img.shape[1], 3, device=pydiffvg.get_device()) * (1 - img[:, :, 3:4])
        # Save the intermediate render.
        pydiffvg.imwrite(img.cpu(), f'{output_dir}/iter_{t}.png', gamma=gamma)
        img = img[:, :, :3]
        # Convert img from HWC to NCHW
        img = img.unsqueeze(0)
        img = img.permute(0, 3, 1, 2)  # NHWC -> NCHW
        # print(img.size())
        # print(target.size())
        if use_lpips_loss:
            loss = perception_loss(img, target)
        else:
            loss = (img - target).pow(2).mean()
        print('render loss:', loss.item())

        # Backpropagate the gradients.
        loss.backward()

        # Take a gradient descent step.
        points_optim.step()
        color_optim.step()
        for group in shape_groups:
            group.fill_color.data.clamp_(0.0, 1.0)

        if t % 10 == 0 or t == num_iter - 1:
            pydiffvg.save_svg(f'{output_dir}/iter_{t}.svg',
                              canvas_width, canvas_height, shapes, shape_groups)

    # Render the final result.
    scene_args = pydiffvg.RenderFunction.serialize_scene(
        canvas_width, canvas_height, shapes, shape_groups)
    img = render(canvas_width,  # width
                 canvas_height,  # height
                 2,   # num_samples_x
                 2,   # num_samples_y
                 0,   # seed
                 None,  # bg
                 *scene_args)
    # Save the intermediate render.
    pydiffvg.imwrite(img.cpu(), f'{output_dir}/final.png', gamma=gamma)
    # Convert the intermediate renderings to a video.
    from subprocess import call
    call(["ffmpeg", "-framerate", "24", "-i",
          f"{output_dir}/iter_%d.png", "-vb", "20M",
          f"{output_dir}/out.mp4"])


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("svg", help="source SVG path")
    # parser.add_argument("target", help="target image path")
    # parser.add_argument("--use_lpips_loss", dest='use_lpips_loss', action='store_true')
    # parser.add_argument("--num_iter", type=int, default=2500)
    # args = parser.parse_args()
    # main(args)
    # styles = ['4', '9', '14', '30']
    # chars = ['A', 'B', 'C', 'D']
    # styles = ['30']
    # chars = ['C']
    # num_iter = 2500
    # use_lpips_loss = False
    # for s in styles:
    #     for c in chars:
    #         target_path = f'partial_svg_diffvg/style_{s}/real_{c}_scale.png'
    #         svg_path = f'partial_svg_diffvg/style_{s}/fake_{c}_scale.svg'
    #         output_dir = f'results/refine_svg_style_{s}_{c}'
    #         main(target_path, svg_path, output_dir, num_iter, use_lpips_loss)
    num_iter = 2500
    use_lpips_loss = False
    target_img_size = 64
    chars = ['A', 'B', 'C', 'D']
    char_ids = ['10', '11', '12', '13']
    for i, c in zip(char_ids, chars):
        target_path = f'vae_generated_imgs_whitebg/{i}.bmp'
        svg_path = f'vae_generated_svgs/fake_{c}_scale_{target_img_size}.svg'
        output_dir = f'results/refine_svg_vae_gen_{i}_{c}'
        main(target_path, svg_path, output_dir, num_iter, use_lpips_loss)
