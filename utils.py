import random
import time
import datetime
import sys

from torch.autograd import Variable
import torch
from visdom import Visdom
import numpy as np
import torch.nn as nn
from torchvision import models
from torchvision.models import VGG19_Weights # Tambahkan import ini

# function to convert tensor to image


def tensor2image(tensor):
    image = 127.5*(tensor[0].cpu().float().numpy() + 1.0)
    if image.shape[0] == 1:
        image = np.tile(image, (3, 1, 1))
    return image.astype(np.uint8)

# Logging function for visdom


class Logger():
    def __init__(self, n_epochs, batches_epoch):
        self.viz = Visdom()
        self.n_epochs = n_epochs
        self.batches_epoch = batches_epoch
        self.epoch = 1
        self.batch = 1
        self.prev_time = time.time()
        self.mean_period = 0
        self.losses = {}
        self.loss_windows = {}
        self.image_windows = {}

    def log(self, losses=None, images=None):
        self.mean_period += (time.time() - self.prev_time)
        self.prev_time = time.time()

        sys.stdout.write('\rEpoch %03d/%03d [%04d/%04d] -- ' %
                         (self.epoch, self.n_epochs, self.batch, self.batches_epoch))

        for i, loss_name in enumerate(losses.keys()):
            if loss_name not in self.losses:
                self.losses[loss_name] = losses[loss_name].data
            else:
                self.losses[loss_name] += losses[loss_name].data

            if (i+1) == len(losses.keys()):
                sys.stdout.write('%s: %.4f -- ' %
                                 (loss_name, self.losses[loss_name]/self.batch))
            else:
                sys.stdout.write('%s: %.4f | ' %
                                 (loss_name, self.losses[loss_name]/self.batch))

        batches_done = self.batches_epoch*(self.epoch - 1) + self.batch
        batches_left = self.batches_epoch * \
            (self.n_epochs - self.epoch) + self.batches_epoch - self.batch
        sys.stdout.write('ETA: %s' % (datetime.timedelta(
            seconds=batches_left*self.mean_period/batches_done)))

        # Draw images
        for image_name, tensor in images.items():
            if image_name not in self.image_windows:
                self.image_windows[image_name] = self.viz.image(
                    tensor2image(tensor.data), opts={'title': image_name})
            else:
                self.viz.image(tensor2image(
                    tensor.data), win=self.image_windows[image_name], opts={'title': image_name})

        # End of epoch
        # Plot losses
        for loss_name, loss in self.losses.items():
            if loss_name not in self.loss_windows:
                self.loss_windows[loss_name] = self.viz.line(X=np.array([self.batch]), Y=np.array([loss.cpu().detach().numpy()/self.batch]),
                                                             opts={'xlabel': 'batch', 'ylabel': loss_name, 'title': loss_name})
            else:
                self.viz.line(X=np.array([self.batch]), Y=np.array([loss.cpu().detach(
                ).numpy()/self.batch]), win=self.loss_windows[loss_name], update='append')
            # Reset losses for next epoch

        if (self.batch % self.batches_epoch) == 0:
            # Plot losses
            for loss_name, loss in self.losses.items():
                if ("epoch"+loss_name) not in self.loss_windows:
                    epoch_loss_window = "epoch"+self.loss_windows[loss_name]
                    epoch_loss_window = self.viz.line(X=np.array([self.epoch]), Y=np.array([loss.cpu().detach().numpy()/self.batch]),
                                                      opts={'xlabel': 'epochs', 'ylabel': loss_name, 'title': loss_name})
                else:
                    epoch_loss_window = "epoch"+self.loss_windows[loss_name]
                    self.viz.line(X=np.array([self.epoch]), Y=np.array(
                        [loss.cpu().detach().numpy()/self.batch]), win=epoch_loss_window, update='append')
                # Reset losses for next epoch
                self.losses[loss_name] = 0.0

            self.epoch += 1
            self.batch = 1
            sys.stdout.write('\n')
        else:
            self.batch += 1

# sets a buffer to input images


class ReplayBuffer():
    def __init__(self, max_size=50):
        assert (
            max_size > 0), 'Empty buffer or trying to create a black hole. Be careful.'
        self.max_size = max_size
        self.data = []

    def push_and_pop(self, data):
        to_return = []
        for element in data.data:
            element = torch.unsqueeze(element, 0)
            if len(self.data) < self.max_size:
                self.data.append(element)
                to_return.append(element)
            else:
                if random.uniform(0, 1) > 0.5:
                    i = random.randint(0, self.max_size-1)
                    to_return.append(self.data[i].clone())
                    self.data[i] = element
                else:
                    to_return.append(element)
        return Variable(torch.cat(to_return))

# set decay


class LambdaLR():
    def __init__(self, n_epochs, offset, decay_start_epoch):
        assert ((n_epochs - decay_start_epoch) >
                0), "Decay must start before the training session ends!"
        self.n_epochs = n_epochs
        self.offset = offset
        self.decay_start_epoch = decay_start_epoch

    def step(self, epoch):
        return 1.0 - max(0, epoch + self.offset - self.decay_start_epoch)/(self.n_epochs - self.decay_start_epoch)

# initislize weights from a normal distribution


def weights_init_normal(m):
    classname = m.__class__.__name__
    if classname.find('Conv') != -1:
        torch.nn.init.normal_(m.weight.data, 0.0, 0.02)
    elif classname.find('BatchNorm2d') != -1:
        torch.nn.init.normal_(m.weight.data, 1.0, 0.02)
        torch.nn.init.constant(m.bias.data, 0.0)

# extracts feature from vgg19 network's 2nd and 5th pooling layer


class VGGNet(nn.Module):
    def __init__(self):
        """Select conv1_1 ~ conv5_1 activation maps."""
        super(VGGNet, self).__init__()
        self.select = ['9', '36'] # Perhatikan bahwa indeks layer mungkin perlu disesuaikan jika arsitektur VGG berubah antar versi.
                                     # Untuk VGG19_Weights.IMAGENET1K_V1, '9' adalah output dari conv3_4, dan '36' adalah output dari conv5_4 (setelah pooling).
                                     # Jika Anda menginginkan layer yang berbeda, Anda perlu menyesuaikan indeks ini.
                                     # Umumnya, layer yang digunakan adalah sebelum ReLU dan setelah MaxPool.
                                     # Untuk VGG19, layer '9' adalah relu2_2, '18' adalah relu3_4, '27' adalah relu4_4, '36' adalah relu5_4.
                                     # Jika Anda ingin fitur dari pooling layers, Anda mungkin perlu menyesuaikan.
                                     # Untuk saat ini, kita akan pertahankan '9' dan '36' sesuai kode asli,
                                     # namun ini adalah poin penting untuk diverifikasi jika perceptual loss tidak bekerja seperti yang diharapkan.
        self.vgg = models.vgg19(weights=VGG19_Weights.IMAGENET1K_V1).features

    def forward(self, x):
        """Extract multiple convolutional feature maps."""
        features = []
        for name, layer in self.vgg._modules.items():
            x = layer(x)
            if name in self.select:
                features.append(x)
        return features[0], features[1]
