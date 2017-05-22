import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

tth = 127. # degrees
Degree = np.pi/180.
E = 10. # keV
wl = 12.3984/E # Angstrom

x = np.sin(tth*Degree/2.)/wl # value to fit
print x

element = 'O'

# incoherent scattering
xx = np.array([0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00, 1.50, 2.00])
if element == 'H':
    yy = np.array([0.983, 0.995, 0.998, 0.999, 0.999, 1.000, 1.000, 1.000, 1.000]) # H
elif element == 'C':
    yy = np.array([4.184, 4.478, 4.690, 4.878, 5.051, 5.208, 5.348, 5.781, 5.930]) # C
elif element == 'O':
    yy = np.array([5.257, 5.828, 6.175, 6.411, 6.596, 6.755, 6.901, 7.462, 7.764]) # O

f = interp1d(xx, yy, kind='cubic')
print "incoherent interpolation value:", f(x)

plt.figure()
plt.plot(xx, yy, 'ro')
plt.plot(x, f(x), 'bo')
plt.title("incoherent")

xx = np.array([0.50, 0.55, 0.60, 0.65, 0.70, 0.80, 0.90, 1.00])
if element == 'H':
    yy = np.array([0.071, 0.053, 0.040, 0.031, 0.024, 0.015, 0.010, 0.007]) # H
elif element == 'C':
    yy = np.array([1.685, 1.603, 1.537, 1.479, 1.426, 1.322, 1.219, 1.114]) # C
elif element == 'O':
    yy = np.array([2.338, 2.115, 1.946, 1.816, 1.714, 1.568, 1.463, 1.377]) # O

f = interp1d(xx, yy, kind='cubic')
print "coherent interpolation value:", f(x)

plt.figure()
plt.plot(xx, yy, 'ro')
plt.plot(x, f(x), 'bo')
plt.title("coherent")

plt.show()
