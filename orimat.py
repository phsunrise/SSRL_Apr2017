import numpy as np
from scipy import optimize
from settings import centralpix, R_det, pixsize

Degree = np.pi/180.

## incoming xray
## for vectors, assuming k has unit length 
ki = np.array([-1.,0.,0.])

## calculate the rotation matrix
def R(th, chi, phi):
    th, chi, phi = th*Degree, chi*Degree, phi*Degree
    chi -= np.pi/2.
    phi *= -1.

    R1 = np.matrix([[np.cos(th), -np.sin(th), 0.],
                    [np.sin(th), np.cos(th),  0.],
                    [0.,         0.,          1.]])
    R2 = np.matrix([[1., 0.,                   0.], 
                    [0., np.cos(chi), -np.sin(chi)],
                    [0., np.sin(chi), np.cos(chi)]])
    R3 = np.matrix([[np.cos(phi), 0., -np.sin(phi)],
                    [0.,          1., 0.          ],
                    [np.sin(phi), 0., np.cos(phi) ]])
    return R3*R2*R1

## function to calculate q vector for a given pixel
def qvec(tth, th, chi, phi, pix=centralpix):
    tth = tth*Degree
    ## calculate pixel position in lab coordinates 
    ## (X-ray coming in -x direction, pixel (126, 250) lies in xy-plane)
    ko = np.array([-np.cos(tth)+pixsize/R_det*(pix[1]-centralpix[1])*np.sin(tth), \
                   np.sin(tth)+pixsize/R_det*(pix[1]-centralpix[1])*np.cos(tth), \
                   -pixsize/R_det*(pix[0]-centralpix[0])])
    ko = ko/np.linalg.norm(ko) # normalize ko

    return np.array(R(th, chi, phi)*np.matrix(ko-ki).T).ravel()

## function to calculate q vector for an array of pixels
## the input pixs should be a 2d array of size (2, n) 
## the output is (h,k,l) numpy array of size (3, n)
def qvec_array(tth, th, chi, phi, pixs=None):
    pixs = np.array(pixs)
    if not pixs.shape[0] == 2:
        raise ValueError("Wrong input shape for pixs! Must be (2, n) numpy array")
    tth = tth*Degree
    ko = np.matrix([-np.cos(tth)+pixsize/R_det*(pixs[1]-centralpix[1])*np.sin(tth), \
                   np.sin(tth)+pixsize/R_det*(pixs[1]-centralpix[1])*np.cos(tth), \
                   -pixsize/R_det*(pixs[0]-centralpix[0])])
    ## normalize each vector
    ko = ko/np.power(np.sum(np.power(ko, 2), axis=0), 0.5)

    k = ko - np.matrix(ki).T
    return np.array(R(th, chi, phi)*k)

def orimat_calc(or0, hkl0, or1, hkl1):
## the input parameters or0 and or1 are (tth, th, chi, phi) arrays
    q0 = qvec(*or0)
    q1 = qvec(*or1)

    hkl0 = np.array(hkl0)
    hkl1 = np.array(hkl1)

    A = np.linalg.norm(hkl0)/np.linalg.norm(q0) # normalization factor
    
    ## We enforce correspondence between hkl0 and q0,
    ##      but vary the direction of vector cross(hkl0, hkl1),
    ##      so that q1 corresponds to hkl1 as close as possible
    ## First, get two vectors in the plane perpendicular to q0
    e1 = np.cross(q0, q1)
    if np.linalg.norm(e1) == 0.:
        raise ValueError("The two input positions cannot be colinear in the radial direction!")
    e2 = np.cross(q0, e1)
    e1 /= np.linalg.norm(e1)
    e2 /= np.linalg.norm(e2)

    ## Now, we decompose hkl1 into hkl2 (parallel to hkl0) 
    ##      and hkl3 (perpendicular to hkl0); hkl3 must correspond to a linear
    ##      combination of e1 and e2
    hkl2 = hkl0 * hkl1.dot(hkl0)/hkl0.dot(hkl0)
    hkl3 = hkl1 - hkl2
    if np.linalg.norm(hkl3) == 0.:
        raise ValueError("hkl0 and hkl1 cannot be parallel!")

    ## The following function calculates the difference between q1 and
    ##      the vector q1p corresponding to hkl1, as a function of the
    ##      orientation of hkl3 in q space
    def diff(theta):
        q2 = np.linalg.norm(hkl3)/A * (np.cos(theta)*e1+np.sin(theta)*e2)
        q1p = q2 + q0/np.linalg.norm(hkl0)*np.linalg.norm(hkl2)
        return np.linalg.norm(q1p-q1)
    res = optimize.basinhopping(diff, 0.)
    #print "Minimization result: %f deg, func=%f" % (res.x/np.pi*180., res.fun)

    ## Calculate the optimal orientation matrix
    q3 = np.linalg.norm(hkl3)/A * (np.cos(res.x)*e1+np.sin(res.x)*e2) # this corresponds to hkl3
    q4 = np.cross(q0, q3)
    hkl4 = np.cross(hkl0, hkl3)/A
    ## now q0 corresponds to hkl0, q3 to hkl3, q4 to hkl4
    return np.transpose(np.linalg.inv(np.array([q0, q3, q4])).dot(np.array([hkl0, hkl3, hkl4])))

## calculate the angles for (h,k,l) under phifix mode
## the formula is:
## (already taken into account that chi=90 is the zero point)
## orimat.R3.[2*sin(tth/2)*sin(tth/2-th), 
##            2*sin(tth/2)*cos(tth/2-th)*sin(chi),
##           -2*sin(tth/2)*cos(tth/2-th)*cos(chi)]T = [h,k,l]T
def angs_phifix(h, k, l, phi, orimat):
    phi = -phi*Degree
    R3 = np.matrix([[np.cos(phi), 0., -np.sin(phi)],
                    [0.,          1., 0.          ],
                    [np.sin(phi), 0., np.cos(phi) ]])
    v1, v2, v3 = np.array((np.linalg.inv(orimat.dot(R3))).dot([[h],[k],[l]])).flatten()
    chi = np.arctan2(v2, -v3)/Degree
    x = np.arctan2(v1, v2/np.sin(chi*Degree))/Degree # this is tth/2-th
    tth = np.arcsin(v1/(2.*np.sin(x*Degree)))*2./Degree
    th = tth/2. - x

    return tth, th, chi 


## main function calculates the orientation matrices
if __name__=='__main__':
    ######## orimat1 ########
    ## (220) peak (primary):
    or0 = (67.250, 33.733, 89.35, 0.)
    hkl0 = [2., 2., 0.]
    ## (112) peak:
    or1 = (57.2656, 30.78, 143.9644, 60.)
    hkl1 = [1., 1., 2.]

    np.save("orimats/orimat1.npy", orimat_calc(or0, hkl0, or1, hkl1))
    print "saved orimat1"

    orimat = np.load("orimats/orimat1.npy")
    print "primary:", orimat.dot(qvec(*or0))
    print "secondary:", orimat.dot(qvec(*or1))

    ######## orimat2 ########
    ## (220) peak (primary):
    or0 = (67.240, 33.6134, 89.1, 0.)
    hkl0 = [2., 2., 0.]
    ## (112) peak:
    or1 = (57.3156, 30.7894, 143.922, 60.)
    hkl1 = [1., 1., 2.]

    np.save("orimats/orimat2.npy", orimat_calc(or0, hkl0, or1, hkl1))
    print "saved orimat2"

    orimat = np.load("orimats/orimat2.npy")
    print "primary:", orimat.dot(qvec(*or0))
    print "secondary:", orimat.dot(qvec(*or1))
