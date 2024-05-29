'''
Author: Mingxin Zhang m.zhang@hapis.k.u-tokyo.ac.jp
Date: 2023-06-20 21:02:34
LastEditors: Mingxin Zhang
LastEditTime: 2023-10-31 16:20:20
Copyright (c) 2023 by Mingxin Zhang, All Rights Reserved. 
'''
import numpy as np

class GlobalOptimizer():
    def __init__(self, n, m, f, g, search_range, maximizer=True):
        self.n = n
        self.m = m
        self.f = f
        self.g = g
        self.search_range = search_range
        self.maximizer = maximizer

    def init(self, init_z):
        self.current_z = init_z
        self.current_x = self.f(self.current_z.reshape(1, -1))[0]
        self.current_score = self.g(self.current_x.reshape(1, -1))

        # print('Initialize', self.name, 'with score', self.current_score )

    def get_z(self, t):
        pass

    def find_optimal(self, sample_n, batch_size=100):
        if batch_size <= 0:
            batch_size = sample_n

        zs = []
        for i in range(sample_n):
            t = i / float(sample_n - 1)
            z = self.get_z(t)
            zs.append(z)
        zs = np.array(zs)

        batch_n = sample_n // batch_size
        remainder = sample_n - batch_size * batch_n

        xs = np.zeros((sample_n, self.m))
        for i in range(batch_n):
            xs[i * batch_size:(i + 1) * batch_size] = self.f(zs[i * batch_size:(i + 1) * batch_size]).cpu().detach()
        if remainder != 0:
            xs[batch_n * batch_size:] = self.f(zs[batch_n * batch_size:]).detach()

        scores = self.g(xs)

        if self.maximizer:
            idx = np.argmax(scores)
        else:
            idx = np.argmin(scores)
        t = idx / float(sample_n - 1)

        z = self.get_z(t)
        x = self.f(z.reshape(1, -1))[0]
        score = self.g(x.reshape(1, -1))[0]

        return z, x, score, t

    def update(self, t):
        pass
