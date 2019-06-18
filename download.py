import itertools
import io
import os
import sys
import urllib.request
import urllib.error

import numpy as np
from scipy.misc import imread, imsave

baseURL = r"https://digitalcollections.tcd.ie/content/14/pages/MS58_%03i%s/image_files/12/%i_%i.jpg"


def make_url(pgNum, vr, xC, yC):
    return baseURL % (pgNum, vr, xC, yC)


def show_or_fail(url):
    from pylab import imshow, title, show
    data = image_url_to_array(url)
    title(data.shape)
    imshow(data)
    show()


def image_url_to_array(url):
    bio = io.BytesIO(urllib.request.urlopen(url).read())
    return imread(bio)


def get_tile(pgNum, vr, xC, yC):
    u = make_url(pgNum, vr, xC, yC)
    return image_url_to_array(u)


def probe_dimensions(pgNumber, vr):
    x = 0
    while True:
        try:
            i = get_tile(pgNumber, vr, x, 0)
        except urllib.error.HTTPError:
            break
        x += 1

    y = 0
    while True:
        try:
            i = get_tile(pgNumber, vr, 0, y)
        except urllib.error.HTTPError:
            break
        y += 1
        
    return x, y
        

def retrieve_page(pgNumber, vr):
    print("Retrieving page:", pgNumber, vr)
    ystripes = []    
    print("\tProbing Size -> ", end="")
    sys.stdout.flush()
    xm, ym = probe_dimensions(pgNumber, vr)
    print((xm, ym))
    from tqdm import tqdm

    with tqdm(total=xm * ym) as pbar:
        for x in range(xm):
            xstripe = []
            for y in range(ym):
                xstripe.append(get_tile(pgNumber, vr, x, y))
                sys.stdout.flush()
            ystripes.append(np.vstack(xstripe))
            pbar.update(1)

    return np.hstack(ystripes)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default="download")
    parser.add_argument("--start_page", type=int, default=1)

    args = parser.parse_args()

    if os.path.isabs(args.path):
        base_dir = os.path.isabs(args.path)
    else:
        base_dir = os.path.abspath(args.path)

    if not os.path.exists(base_dir):
        print("Creating directory: " + base_dir)
        os.mkdir(base_dir)

    print(os.listdir(base_dir))
    for pn in itertools.count(args.start_page):
        suffixes = "vr"
        for vr in suffixes:
            save_path = os.path.join(base_dir, "%03i%s.png" % (pn, vr))
            if os.path.exists(save_path):
                continue
            result = retrieve_page(pn, vr)
            imsave(save_path, result)
        pn += 1
