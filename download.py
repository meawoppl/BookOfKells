import itertools, io, sys, urllib
import urllib.error
import numpy as np
from scipy.misc import imread, imsave

baseURL = r"http://digitalcollections.tcd.ie/content/14/pages/MS58_%03i%s/image_files/12/%i_%i.jpg"


def makeURL(pgNum, vr, xC, yC):
    return baseURL % (pgNum, vr, xC, yC)


def showOrFail(url):
    from pylab import imshow, title, show
    imgData = retrieveToImg(url)
    title(imgData.shape)
    imshow(imgData)
    show()

def retrieveToImg(url):
    bio = io.BytesIO(urllib.request.urlopen(url).read())
    return imread(bio)

def getTile(pgNum, vr, xC, yC):
    u = makeURL(pgNum, vr, xC, yC)
    return retrieveToImg(u)

def probeDimensions(pgNumber, vr):
    x = 0
    while True:
        try:
            i = getTile(pgNumber, vr, x, 0)
        except urllib.error.HTTPError:
            break
        x += 1

    y = 0
    while True:
        try:
            i = getTile(pgNumber, vr, 0, y)
        except urllib.error.HTTPError:
            break
        y += 1
        
    return x, y
        

def retrievePage(pgNumber, vr):
    print("Retrieving page:", pgNumber, vr)
    ystripes = []    
    print("\tProbing Size ", end="")
    sys.stdout.flush()
    xm, ym = probeDimensions(pgNumber, vr)
    print(xm, ym)
    
    print("\tDownloading", end="")
    for x in range(xm):
        xstripe = []
        for y in range(ym):
            xstripe.append(getTile(pgNumber, vr, x, y))
            print(".", end="")
            sys.stdout.flush()
        ystripes.append(np.vstack(xstripe))
    print("\n\tDone.")
    return np.hstack(ystripes)

if __name__ == "__main__":
    import os
    baseDir = os.path.join("/media", 
                           "meawoppl",
                           "3d9277ad-2580-4d78-aaa8-5ebfdfda51ca",
                           "pages")

    baseDir = "pages"

    print(os.listdir(baseDir))
    pn = 270
    while True:
        suffixes = "vr"
        if pn == 36:
            suffixes = ["ar", "av", "br", "bv"]
        for vr in suffixes:
            pagePath = os.path.join(baseDir, "%03i%s.png" % (pn, vr))
            if os.path.exists(pagePath):
                continue
            result = retrievePage(pn, vr)
            imsave(pagePath, result)
        pn += 1
