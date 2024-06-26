'''
Author: Mingxin Zhang m.zhang@hapis.u-tokyo.ac.jp
Date: 2023-04-12 01:41:18
LastEditors: Mingxin Zhang
LastEditTime: 2023-11-14 15:07:21
Copyright (c) 2023 by Mingxin Zhang, All Rights Reserved. 
'''

from torch import nn
import torch.nn.functional as F
import torch
import numpy as np


class Generator(nn.Module):
    def __init__(self, encoded_space_dim):
        super().__init__()
        self.encoded_space_dim = encoded_space_dim
        self.fc1 = nn.Linear(encoded_space_dim, 128 * 1 * 23)
        self.unflatten = nn.Unflatten(dim=1, unflattened_size=(128, 1, 23))

        self.deconv1 = nn.ConvTranspose2d(128, 256, 5, stride=2, output_padding=1)
        self.bn1 = nn.BatchNorm2d(256)
        self.deconv2 = nn.ConvTranspose2d(256, 128, 5, stride=2, padding=2, output_padding=1)
        self.bn2 = nn.BatchNorm2d(128)
        self.deconv3 = nn.ConvTranspose2d(128, 1, 3, padding=1)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.unflatten(x)
        x = F.relu(self.bn1(self.deconv1(x)))
        x = F.relu(self.bn2(self.deconv2(x)))
        x = torch.tanh(self.deconv3(x))
        return x
    
    def calc_model_gradient(self, latent_vector):
        jacobian = self.calc_model_gradient_FDM(latent_vector, delta=1e-2)
        return jacobian

    def calc_model_gradient_FDM(self, latent_vector, delta=1e-4):
        sample_latents = np.repeat(latent_vector.reshape(1, -1), repeats=self.encoded_space_dim + 1, axis=0)
        sample_latents[1:] += np.identity(self.encoded_space_dim) * delta

        sample_datas = self.forward(sample_latents)
        sample_datas = sample_datas.reshape(-1, 12*100)

        jacobian = (sample_datas[1:] - sample_datas[0]).T / delta
        return jacobian


class Discriminator(nn.Module):
    def __init__(self):
        super().__init__()

        ### Convolutional section
        self.conv1 = nn.Conv2d(1, 4, 3, padding=1)
        self.conv2 = nn.Conv2d(4, 8, 5, padding=2)
        self.bn1 = nn.BatchNorm2d(8)
        self.conv3 = nn.Conv2d(8, 16, 5, padding=0)
        self.bn2 = nn.BatchNorm2d(16)

        self.pool = nn.MaxPool2d(2)

        self.flatten = nn.Flatten(start_dim=1)

        self.fc1 = nn.Linear(16 * 1 * 23, 1)

        self.dropout = nn.Dropout(p=0.2)

    def forward(self, x):
        x = self.dropout(F.leaky_relu(self.conv1(x), 0.2))
        x = self.pool(self.conv2(x))
        x = self.dropout(F.leaky_relu(self.bn1(x), 0.2))
        x = self.pool(self.conv3(x))
        x = self.dropout(F.leaky_relu(self.bn2(x), 0.2))
        x = self.flatten(x)
        x = F.sigmoid(self.fc1(x))
        return x