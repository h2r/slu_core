#function output = prefilt(img, fc)
# ima = prefilt(img, fc);
# fc  = 4 (default)
# 
# Input images are double in the range [0, 255];
# You can also input a block of images [ncols nrows 3 Nimages]
#
# For color images, normalization is done by dividing by the local
# luminance variance.
from pylab import *
from scipy.fftpack import fftshift
from scipy import *
from PIL import Image


def prefilter_image(img, fc=4):
    #if nargin == 1:
    #    fc = 4; # 4 cycles/image
    w = 5;
    
    #img = img/(1.0*img.max())
    img = img*1.0;
    s1 = fc/sqrt(log(2.0));
    
    # Pad images to reduce boundary artifacts
    img = log(img+1.0);
    img = padarray3D(img, w);
    
    sn, sm, c = shape(img);

    if(sn != sm):
        print "not equal size"
        return None

    # Filter
    fx, fy = mgrid[-sn/2.0:sn/2.0, -sm/2.0:sm/2.0]*1.0;
    gf = fftshift(exp(-1.0*(fx*fx+fy*fy)/(s1**2.0)));

    #ic, jc = shape(gf)
    gfPr = zeros(shape(img))*1.0
    gfPr[:,:,0]=gf;    gfPr[:,:,1]=gf;    gfPr[:,:,2]=gf;

    # Whitening
    output = img - real(ifft2(fft2(img, axes=(0,1))*gfPr, axes=(0,1)));

    # Local contrast normalization
    gimage = mean(output, 2)
    localstd = sqrt(abs(ifft2(fft2(gimage*gimage, axes=(0,1))*gf, axes=(0,1)))); 
    output[:,:,0] = output[:,:,0]/(0.2+localstd);
    output[:,:,1] = output[:,:,1]/(0.2+localstd);
    output[:,:,2] = output[:,:,2]/(0.2+localstd);

    # Crop output to have same size than the input
    output = output[w:sn-w, w:sm-w,:];

    return output


#pad a 3D array
def padarray3D(myarray, numpad): 
    if(len(shape(myarray)) < 3):
        return None
    
    #get the number of channels
    channels = shape(myarray)[2]
    
    #create the new shape
    myshape = array(shape(myarray))
    myshape[0] += 2*numpad
    myshape[1] += 2*numpad

    #iterate through each channel and pad it
    retIm = zeros(myshape)*1.0#, dtype='uint8')
    for i in range(channels):
        retIm[:,:,i] = padarray2D(myarray[:,:,i], numpad)
    
    return retIm


#pad an array with stuff
def padarray2D(myarray, numpad):
    myimSP = myarray
    rtleftim = fliplr(myarray)
    topbottomim = flipud(myarray)
    bothim = flipud(rtleftim)
    
    #get the 
    myshape = shape(myimSP)
    newarr = zeros([myshape[0]+2*numpad, myshape[1]+2*numpad])*1.0#, dtype='uint8');
    newarr[numpad:numpad+myshape[0], numpad:numpad+myshape[1]] = myimSP;
    
    #top 
    newarr[0:numpad, numpad:numpad+myshape[1]] = topbottomim[myshape[0]-numpad:, :]
    #bottom
    newarr[myshape[0]+numpad:, numpad:numpad+myshape[1]] = topbottomim[0:numpad, :]
    #left
    newarr[numpad:numpad+myshape[0], 0:numpad] = rtleftim[:, myshape[1]-numpad:]
    #right
    newarr[numpad:numpad+myshape[0], myshape[1]+numpad:] = rtleftim[:, 0:numpad]

        
    #fill in the corners
    newarr[myshape[0]+numpad:, myshape[1]+numpad:] = bothim[0:numpad, 0:numpad]
    newarr[0:numpad, 0:numpad] = bothim[myshape[0]-numpad:,
                                        myshape[1]-numpad:];
    newarr[myshape[0]+numpad:, 0:numpad] = bothim[0:numpad, 
                                                  myshape[1]-numpad:];
    newarr[0:numpad, myshape[1]+numpad:] = bothim[myshape[0]-numpad:,
                                                  0:numpad];

    return newarr

def test1():
    testIm = Image.open('test.jpg');

    #pad the array and plot it
    retVal = padarray3D(array(testIm), 120);
    imshow(array(retVal, dtype='uint8'))
    
    #show the test image
    figure()
    imshow(array(testIm))

    #show the prefiltered test image
    figure()
    output = prefilt(array(testIm))
    o = array(128+128*output/abs(output).max(), dtype='uint8');
    imshow(output)
    show()


if __name__ == "__main__":
    test1()
