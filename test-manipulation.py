from options.test_options import TestOptions
from data import create_dataset
from models import create_model
from util.visualizer import Visualizer, save_images
from util.html import HTML
import os
from util.util import AverageMeter, set_seed, write_location

import torch


opt = TestOptions().parse()  # get test options
# hard-code some parameters for test
opt.num_threads = 0   # test code only supports num_threads = 1
opt.batch_size = 1    # test code only supports batch_size = 1
opt.serial_batches = True  # disable data shuffling; comment this line if results on randomly chosen images are needed.
dataset = create_dataset(opt)  # create a dataset given opt.dataset_mode and other options
model = create_model(opt)      # create a model given opt.model and other options
model.setup(opt)               # regular setup: load and print networks; create schedulers
visualizer = Visualizer(opt)  # create a visualizer that display/save images and plots
meters_tst = {stat: AverageMeter() for stat in model.loss_names}

set_seed(opt.seed)

web_dir = os.path.join(opt.results_dir, opt.name, opt.exp_id,
                        '{}_{}'.format(opt.testset_name, opt.epoch))  # define the website directory
print('creating web directory', web_dir)
webpage = HTML(web_dir, 'Experiment = %s, Phase = %s, Epoch = %s' % (opt.name, opt.phase, opt.epoch))

file = open(os.path.join(opt.results_dir, opt.name, opt.exp_id, 'slot_location.txt'), 'w+')

for i, data in enumerate(dataset):
    visualizer.reset()
    model.set_input(data)  # unpack data from data loader
    # model.test()           # run inference: forward + compute_visuals

    file = open(os.path.join(opt.results_dir, opt.name, opt.exp_id, '{}_{}'.format(opt.testset_name, opt.epoch), 'slot_location.txt'), 'w')

    with torch.no_grad():
        model.forward()
        fg_slot_position = torch.zeros((opt.num_slots-1, 2))
        fg_slot_position[0] = torch.tensor([0, 0])
        fg_slot_position[1] = torch.tensor([0, 0])
        fg_slot_position[2] = torch.tensor([0, 0])
        fg_slot_position[3] = torch.tensor([0, 0])
        # fg_slot_position[4] = torch.tensor([0, 0.5])
        # fg_slot_position[5] = torch.tensor([0, -0.5])
        # fg_slot_position[6] = torch.tensor([0, 0])
        model.forward_position(fg_slot_nss_position=fg_slot_position)
        model.compute_visuals()

    # losses = model.get_current_losses()
    # visualizer.print_test_losses(i, losses)
    # for loss_name in model.loss_names:
    #     meters_tst[loss_name].update(float(losses[loss_name]))

    visuals = model.get_current_visuals()
    visualizer.display_current_results(visuals, epoch=None, save_result=False)
    img_path = model.get_image_paths()
    save_images(webpage, visuals, img_path, aspect_ratio=opt.aspect_ratio, width=opt.load_size)
    print('process image... %s' % img_path)
    # losses = {}
    # for loss_name in model.loss_names:
    #     losses[loss_name] = meters_tst[loss_name].avg
    # visualizer.print_test_losses('average', losses)

    # try:
    #     write_location(file, model.fg_slot_image_position, i, description='(image position)')
    #     write_location(file, model.fg_slot_nss_position, i, description='(nss position)')
    # except:
    #     pass