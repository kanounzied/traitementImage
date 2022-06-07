import base64
import math
from io import BytesIO

import numpy as np
from PIL import Image
from matplotlib import image
from matplotlib import pyplot

VMAX = 255


def read_image(path: str):
    return Image.open(path)


def save_image(old_image: Image, new_data: list, name: str):
    buffered = BytesIO()
    new_image = Image.new(old_image.mode, old_image.size)
    new_image.putdata(new_data)
    new_image.save("static/output/" + name)
    new_image.save(buffered, format=old_image.format)
    return base64.b64encode(buffered.getvalue())


def moyenne(data: list):
    moyenne = 0
    for i in data:
        moyenne += i
    return round(moyenne / len(data), 3)


def moyenne_rgb(data: list):
    (r, g, b) = (0, 0, 0)
    data_len = len(data)
    for i in data:
        r += i[0]
        g += i[1]
        b += i[2]
    return round(r / data_len, 3), round(g / data_len, 3), round(b / data_len, 3)


def ecart_type(data: list):
    sigma_carre = 0
    moy = moyenne(data)
    for i in data:
        sigma_carre += (i - moy) ** 2
    return round(math.sqrt(sigma_carre / len(data)), 3)


def ecart_type_rgb(data: list):
    sigma_carre_r, sigma_carre_g, sigma_carre_b = (0, 0, 0)
    r, g, b = moyenne_rgb(data)
    data_len = len(data)
    for i in data:
        sigma_carre_r += (i[0] - r) ** 2
        sigma_carre_g += (i[1] - r) ** 2
        sigma_carre_b += (i[2] - r) ** 2
    return round(math.sqrt(sigma_carre_r / data_len), 3), round(math.sqrt(sigma_carre_g / data_len), 3), round(
        math.sqrt(sigma_carre_b / data_len), 3)


def histogramme(data: list, VMAX=255):
    histogram = np.zeros(VMAX + 1)
    for i in data:
        if i >= 0:
            histogram[i] += 1
        else:
            raise ValueError('image cannot contain negative data')
    return histogram


def histogramme_rgb(data: list):
    histogram = np.zeros(VMAX + 1)
    for (r, g, b) in data:
        rgb = (r + g + b) // 3
        histogram[rgb] += 1
    return histogram


def histogram_cumule(histogram: list):
    histogram_cumule = np.zeros(VMAX + 1)
    for i in range(len(histogram)):
        if i == 0:
            histogram_cumule[i] = histogram[i]
        else:
            histogram_cumule[i] = histogram[i] + histogram_cumule[i - 1]
    return histogram_cumule


def p(hist, img: Image):
    p = np.zeros(VMAX + 1)
    for i in range(len(hist)):
        p[i] = hist[i] / len(img.getdata())
    return p


def A(p):
    a = np.zeros(VMAX + 1)
    for i in range(len(p)):
        if i + 1 < len(p):
            p[i + 1] += p[i]
        a[i] = p[i] * VMAX
    return a


def egaliseur(hist, img: Image):
    a = A(p(hist, img))
    egaliseur = np.zeros(len(hist))
    new_data = np.zeros(len(img.getdata()))
    img_data = list(img.getdata())
    for i in range(len(a)):
        egaliseur[int(a[i])] += hist[i]
    for i in range(len(img.getdata())):
        print()
        new_data[i] = a[img_data[i]]
    return egaliseur, new_data


def transformation_lineaire(hist, img: Image):
    min = 0
    max = VMAX
    LUT = np.zeros(VMAX + 1)
    while hist[min] == 0: min += 1
    while hist[max] == 0: max -= 1
    for i in range(VMAX + 1):
        LUT[i] = VMAX * (i - min) / (max - min)
    return create_data(LUT, img)


def transformation_lineaire_saturee(img: Image, min, max):
    LUT = np.zeros(VMAX + 1)
    for i in range(VMAX + 1):
        if i < min:
            LUT[i] = 0
        elif i > max:
            LUT[i] = VMAX
        else:
            LUT[i] = VMAX * (i - min) / (max - min)
    return create_data(LUT, img)


def dilatation(img: Image, a: int, b: int):
    if a > VMAX or b > VMAX:
        print("\n a or b shouldnt be > than V max")
        return
    LUT = np.zeros(VMAX + 1)

    # si a > b ==> dilatation des zones claires
    # init look up table
    for i in range(VMAX + 1):
        if i < a:
            LUT[i] = droite1(i, a, b)
        else:
            LUT[i] = droite2(i, a, b, VMAX)
    return create_data(LUT, img)


def dilatation_milieu(img: Image, a, b, c):
    if b >= a or a >= VMAX or c > 0 or c < -VMAX / 2:
        print("\n b should be < than a AND a should be < than V max AND c between -Vmax/2 and 0")
        return
    LUT = np.zeros(VMAX + 1)

    for i in range(VMAX + 1):
        d1 = droite1(i, a, b)
        d2 = droite2(i, b, a, VMAX)
        d3 = droite3_milieu(i, a, b, c, VMAX)
        if d1 >= d3:
            LUT[i] = d1
        else:
            LUT[i] = min(d3, d2)
    return create_data(LUT, img)


def color_inversion(img: Image):
    LUT = np.zeros(VMAX + 1)

    for i in range(VMAX + 1):
        LUT[i] = VMAX - i

    return create_data(LUT, img)


def create_data(LUT, img):
    new_data = np.zeros(img.size[0] * img.size[1])
    img_data = list(img.getdata())
    for i in range(img.size[0] * img.size[1]):
        new_data[i] = LUT[img_data[i]]
    return new_data


def droite1(x, a, b):
    return (b / a) * x


def droite2(x, a, b, v_max):
    return ((v_max - b) * x + v_max * (b - a)) / (v_max - a)


def droite3_milieu(x, a, b, c, v_max):
    return (v_max / 2) * ((x + c) / (c + (v_max / 2)))


def seuiller_et(img: Image, r, g, b):
    img_data = list(img.getdata())
    new_data = np.empty(img.size[0] * img.size[1], dtype=tuple)
    for i in range(len(img_data)):
        if img_data[i][0] > r and img_data[i][1] > g and img_data[i][2] > b:
            new_data[i] = (VMAX, VMAX, VMAX)
        else:
            new_data[i] = (0, 0, 0)
    return new_data


def seuiller_ou(img: Image, r, g, b):
    img_data = list(img.getdata())
    new_data = np.empty(img.size[0] * img.size[1], dtype=tuple)
    for i in range(len(img_data)):
        if img_data[i][0] > r or img_data[i][1] > g or img_data[i][2] > b:
            new_data[i] = (VMAX, VMAX, VMAX)
        else:
            new_data[i] = (0, 0, 0)
    return new_data


def seuiller_auto(img: Image, hist: list):
    img_data = list(img.getdata())
    new_data = np.empty(img.size[0] * img.size[1], dtype=tuple)
    threshold = estimate_threshold(hist, img.size[0] * img.size[1])
    print("estimated threshold", threshold)
    for i in range(len(img_data)):
        if (img_data[i][0] + img_data[i][1] + img_data[i][2]) > (threshold * 3):
            new_data[i] = (VMAX, VMAX, VMAX)
        else:
            new_data[i] = (0, 0, 0)
    return new_data


def estimate_threshold(hist: list, nb_pixels):
    thresholds = np.empty(len(hist))
    for i in range(len(hist)):
        thresholds[i] = calc_thresh(hist, i, nb_pixels)
    print("thresholds")
    print(thresholds)
    print(np.amax(thresholds))
    return np.argmax(thresholds)


def calc_thresh(hist: list, thresh_index, nb_pixels):
    wb = 0
    ub = 0
    nb_b = 0

    wf = 0
    uf = 0
    nb_f = 0

    for i in range(len(hist)):
        if i < thresh_index:
            wb += hist[i]
            ub += i * hist[i]
            nb_b += hist[i]
        else:
            wf += hist[i]
            uf += i * hist[i]
            nb_f += hist[i]

    wb /= nb_pixels
    wf /= nb_pixels

    if ub != 0:
        ub /= nb_b
    if uf != 0:
        uf /= nb_f

    return round(wb * wf * ((ub - uf) ** 2), 3)


def test1():
    image = Image.open("dog.pgm")
    print(image.format)
    print(image.mode)
    print(image.size)
    print(np.array(image.getdata()))
    # show the image
    image.show()


def test_2():
    # load image as pixel array
    data = image.imread("tactic.pgm")
    # summarize shape of the pixel array
    print(data.dtype)
    print(data.shape)
    # display the array of pixels as an image
    pyplot.imshow(data)
    pyplot.show()
