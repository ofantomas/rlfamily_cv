import numpy as np
from rl.tools.utils.mvavg import ExpMvAvg, MomentMvAvg
from rl.tools.online_learners.base_algorithms.base_algorithm import MirrorDescent
from rl.tools.online_learners.prox import DiagQuad


class Adam(MirrorDescent):

    def __init__(self, x0, scheduler, beta1=0.9, beta2=0.999, eps=1e-8):
        self._scheduler = scheduler
        prox = DiagQuad(1.0 / self._scheduler.stepsize)
        super().__init__(x0, prox)
        self._beta1 = beta1
        self._beta2 = beta2
        self._m = ExpMvAvg(np.zeros_like(self._h), beta1)
        self._v = ExpMvAvg(np.zeros_like(self._h), beta2)
        self._eps = eps

    def reset(self):
        self._scheduler.reset()
        self._breg.update(1.0 / self._scheduler.stepsize)
        self._m = ExpMvAvg(np.zeros_like(self._h), self._beta1)
        self._v = ExpMvAvg(np.zeros_like(self._h), self._beta2)

    def adapt(self, g, w):
        self._scheduler.update(w)
        self._v.update(g**2)
        D = np.sqrt(self._v.val) + self._eps
        self._breg.update(D / self._scheduler.stepsize)

    def update(self, g, w):
        self._m.update(g)  # additional moving average
        super().update(self._m.val, w)


class Adagrad(MirrorDescent):

    def __init__(self, x0, scheduler, eps=1e-3, rate=1.0):
        self._scheduler = scheduler
        prox = DiagQuad(1.0 / self._scheduler.stepsize)
        super().__init__(x0, prox)
        self._v = MomentMvAvg(np.full_like(self._h, eps), rate)

    def reset(self):
        self._scheduler.reset()
        self._breg.update(1.0 / self._scheduler.stepsize)
        self._v = MomentMvAvg(np.full_like(self._h, eps), rate)

    def adapt(self, g, w):
        self._scheduler.update()  # w goes to the update of self._v
        self._v.update((w * g)**2)
        D = np.sqrt(self._v.val)
        self._breg.update(D / self._scheduler.stepsize)
