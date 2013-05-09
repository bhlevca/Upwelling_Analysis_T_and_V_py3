import scipy.interpolate as interpolate
import scipy.optimize as optimize
import scipy.signal as signal
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d



def f(xy):
   x, y = xy
   z = np.array([y - x ** 2, y - x - 1.0])
   return z


#===============================================================================
# get_interpolate1d_func
#===============================================================================
def get_interpolate1d_func(x, y, kind = 'cubic'):
    f2 = interp1d(x, y, kind = kind)
    return f



#===============================================================================
# find_roots
#===============================================================================
def find_roots(x1, y1, x2, y2):

    def pdiff(x):
        return p1(x) - p2(x)

    # define the functions based on the x and y  arrays
    p1 = interpolate.PiecewisePolynomial(x1, y1[:, np.newaxis])
    p2 = interpolate.PiecewisePolynomial(x2, y2[:, np.newaxis])

    # estimate roots
    xs = np.r_[x1, x2]
    xs.sort()
    x_min = xs.min()
    x_max = xs.max()
    x_mid = xs[:-1] + np.diff(xs) / 2
    roots = set()
    for val in x_mid:
        # print val
        root, infodict, ier, mesg = optimize.fsolve(pdiff, val, full_output = True, col_deriv = True, epsfcn = 0.01)
        # ier==1 indicates a root has been found
        # print root, p1(root), ier
        if ier == 1 and x_min < root < x_max:
            roots.add(root[0])
            print "added root: %f" % root[0]
    roots = list(roots)

    return roots, p1(roots), p2(roots), p1, p2

if __name__ == '__main__':
    x1 = np.array([1.4, 2.1, 3, 5.9, 8, 9, 23])
    y1 = np.array([2.3, 3.1, 1, 3.9, 8, 9, 11])
    x2 = np.array([1.4, 2, 3, 4, 6, 8, 23])
    y2 = np.array([4, 12, 7, 1, 6.3, 8.5, 12])

#     p1 = interpolate.PiecewisePolynomial(x1, y1[:, np.newaxis])
#     p2 = interpolate.PiecewisePolynomial(x2, y2[:, np.newaxis])
#
#     xs = np.r_[x1, x2]
#     xs.sort()
#     x_min = xs.min()
#     x_max = xs.max()
#     x_mid = xs[:-1] + np.diff(xs) / 2
#     roots = set()
#     for val in x_mid[1:-1]:
#         print val
#         root, infodict, ier, mesg = optimize.fsolve(pdiff, val, full_output = True, col_deriv = True, epsfcn = 0.01)
#         # ier==1 indicates a root has been found
#         print root, p1(root), ier
#         if ier == 1 and x_min < root < x_max:
#             roots.add(root[0])
#     roots = list(roots)
#     x = np.linspace(2, 23, 100)
#     plt.plot(x1, y1, x2, y2, x, p1(x), x, p2(x))
#     plt.grid(True)
#
#     print(np.column_stack((roots, p1(roots), p2(roots))))

    rx, ry1, ry2, p1, p2 = find_roots(x1, y1, x2, y2)
    print(np.column_stack((rx, ry1, ry1)))
    x = np.linspace(1.5, 23, 100)
    plt.plot(x1, y1, x2, y2, x, p1(x), x, p2(x))
    plt.plot(rx, ry1, 'bo')
    plt.grid(True)



    x = x1  # np.linspace(0, 10, 10)
    y = y1  # np.cos(-x ** 2 / 8.0)
    f = interp1d(x, y)
    f2 = interp1d(x, y, kind = 'cubic')

    xnew = np.linspace(2, 10, 40)

    fig = plt.figure()
    plt.plot(x, y, 'o', xnew, f(xnew), '-', xnew, f2(xnew), '--')
    plt.legend(['data', 'linear', 'cubic'], loc = 'best')
    plt.show()

# print optimize.fsolve(fu, [1.0, 2.0], full_output = True)
