#function g = gistGabor(img, w, G)
# 
# Input:
#   img = input image (it can be a block: [nrows, ncols, c, Nimages])
#   w = number of windows (w*w)
#   G = precomputed transfer functions
#
# Output:
#   g: are the global features = [Nfeatures Nimages], 
#                    Nfeatures = w*w*Nfilters*c
from pylab import *
from scipy import *
from scipy.fftpack import fft2, ifft2
from scipy.fftpack import fftshift
from copy import deepcopy



def gistGabor(img, w, G):
    nG, nG, Nfilters = shape(G);
    #raw_input()
    nP, nP, c = shape(img)

    W = w*w;
    g = zeros([W*Nfilters, c])*1.0;

    img2 = fft2(img, axes=(0, 1)); 
    
    k=0;
    for n in range(Nfilters):
        ix, iy, cN = shape(img2)
        Gcurr = zeros([len(G), len(G[0]), 3])*1.0
        Gcurr[:,:,0] = G[:,:,n]; Gcurr[:,:,1] = G[:,:,n]; Gcurr[:,:,2] = G[:,:,n];
        ig = abs(ifft2(img2*Gcurr, axes=(0,1))); 
        #figure()
        #gray()
        #print ig[30:40,30:40]


        #testim = ig-ig.min()

        #for l in range(3):
        #    print l
        #    testim[:,:,l] = testim[:,:,l]/testim[:,:,l].max();
        #print testim
        #imshow(testim)
        #savefig('output/'+ str(n)+"_im.png")
        
        #imshow(ig)
        #savefig('output/'+ str(n)+"_ig.png")
        v = downN(ig, w);

        #figure()
        #testim = v-v.min()
        #for l in range(3):
        #    testim[:,:,l] = testim[:,:,l]/testim[:,:,l].max();
        #imshow(testim, interpolation='nearest')

        #raw_input()

        g[k:k+W,:] = reshape(v, [W, c], order='F')
        k = k + W;

    #flatten may not do the right thing
    l1, l2 = shape(g)

    #print shape(g)
    return reshape(g, [l1*3, l2/3.0], order='F');
    #return g.flatten()



#
# G = createGabor(numberOfOrientationsPerScale, n);
#
# Precomputes filter transfer functions. All computations are done on the
# Fourier domain. 
#
# If you call this function without output arguments it will show the
# tiling of the Fourier domain.
#
# Input
#     numberOfOrientationsPerScale = vector that contains the number of
#                                orientations at each scale (from HF to BF)
#     n = imagesize (square images)
#
# output
#     G = transfer functions for a jet of gabor filters


def createGabor(orient, n):
    Nscales = len(orient);
    Nfilters = sum(orient)
    
    param = []
    for i in range(Nscales):
        for j in range(1,orient[i]+1):
            param.append([.35, 
                           .3/(1.85**(i)), 
                           16.0*orient[i]**2.0/32**2.0, 
                           pi/(orient[i])*(j-1)]);

    param = array(param)

    # Frequencies:
    fx, fy = mgrid[-n/2:n/2, -n/2:n/2];
    fr = fftshift(sqrt(fx**2+fy**2));
    t =  transpose(fftshift(angle(fx+sqrt(-1)*fy)));
    

    # Transfer functions:
    G=zeros([n, n, Nfilters])
    for i in range(Nfilters):
        tr=t+param[i,3]; 
        tr=tr + 2*pi*(tr<-pi) - 2*pi*(tr>pi);
        G[:,:,i]=exp(-10*param[i,0]*(fr/n/param[i,1]-1)**2 - 2*param[i,2]*pi*tr**2.0);
        
        #matlab says: 
        #    G(:,:,i)=exp(-10*param(i,1)*(fr/n/param(i,2)-1).^2-2*param(i,3)*pi*tr.^2);

    return G


#function y=downN(x, N)
# 
# averaging over non-overlapping square image blocks
#
# Input
#   x = [nrows ncols nchanels]
# Output
#   y = [N N nchanels]

def downN(x, N):
    lx, ly, lc = shape(x)
    nx = fix(linspace(0,lx,N+1));
    ny = fix(linspace(0,ly,N+1));
    y  = zeros((N, N, lc));
    for xx in range(N):
        for yy in range(N):
            v=mean(mean(x[nx[xx]:nx[xx+1], ny[yy]:ny[yy+1],:],0),0);
            y[xx,yy,:]=v;

    return y


