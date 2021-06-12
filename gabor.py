import cv2
import numpy as np
import scipy
import matplotlib as plt
class Gabor(object):

    def __init__(self):
        self.gabor_kernels = self.make_gabor_kernel()

    def make_gabor_kernel(self):
        filters = []
        ksize = 31
        for theta in np.arange(0, np.pi, np.pi / 16):
            kern = cv2.getGaborKernel((ksize, ksize), 4.0, theta, 10.0, 0.5, 0, ktype=cv2.CV_32F)
            kern /= 1.5 * kern.sum()
            filters.append(kern)
        return filters

    def gabor_histogram(self, input, type='global', n_slice=2):
        ''' count img histogram
        '''
    

        if type == 'global':
            hist = self._gabor(img, kernels=self.gabor_kernels)

        hist = cv2.calcHist([hist], [0], None, [256], [0, 256])

        return hist

    def _gabor(self, image, kernels):
        accum = np.zeros_like(image)
        for kern in kernels:
            fimg = cv2.filter2D(image, cv2.CV_8UC3, kern)
            np.maximum(accum, fimg, accum)

        return accum


# how to use it
# if __name__ == "__main__":
#     G = Gabor()
#     img = cv2.imread('HP_train.jpg')
#     img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#     hist = G.gabor_histogram(img)
#     plt.plot(hist)
#     plt.show()

