import random

import numpy as np
from PIL import Image

VMAX = 255


def noise_maker(img: Image):
    data = list(img.getdata())
    new_data = np.zeros(img.size[0] * img.size[1])

    for i in range(len(data)):
        nb = random.randint(0, 20)
        if nb == 0:
            new_data[i] = 0
        elif nb == 20:
            new_data[i] = VMAX
        else:
            new_data[i] = data[i]
    return new_data


def filtre_moyenne(img: Image, size=3):  # dans les bord on ignore les cases non existantes
    data = np.array(list(img.getdata())).reshape((img.size[0], img.size[1]))
    new_data = np.zeros((img.size[0], img.size[1]))
    # points_counter = 0
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            sum = 0
            added_numbers = 0

            if data[i][j] == 0 or data[i][j] == VMAX:
                for k in range(-(size - 1) // 2, (size // 2) + 1):
                    for l in range(-(size - 1) // 2, (size // 2) + 1):
                        try:
                            # if i == 2 and j == 2:
                            # print(str(i + k) + " " + str(j + l), "k= ", k, "l= ", l)
                            sum += data[i + k][j + l]
                            added_numbers += 1
                        except IndexError:
                            pass
                new_data[i][j] = int(sum // added_numbers)
            else:
                new_data[i][j] = data[i][j]
            # if 700 < points_counter < 800:
            #     print(i, j, "old value: ", data[i][j], "new value: ", new_data[i][j])
            # points_counter += 1
    return new_data.reshape((img.size[0] * img.size[1],))


def filtre_mediane(img: Image, size=3):
    data = np.array(list(img.getdata())).reshape((img.size[0], img.size[1]))
    new_data = np.zeros((img.size[0], img.size[1]))

    for i in range(img.size[0]):
        for j in range(img.size[1]):
            added_numbers = 0
            queue = np.zeros(9)
            if data[i][j] == 0 or data[i][j] == VMAX:
                for k in range(-(size - 1) // 2, (size // 2) + 1):
                    for l in range(-(size - 1) // 2, (size // 2) + 1):
                        try:
                            queue[added_numbers] = data[i + k][j + l]
                            added_numbers += 1
                        except IndexError:
                            pass
                queue[::-1].sort()
                new_data[i][j] = queue[(added_numbers - 1) // 2]
            else:
                new_data[i][j] = data[i][j]
    return new_data.reshape((img.size[0] * img.size[1],))


def filtre_rehausseur(img: Image, size=3):
    data = np.array(list(img.getdata())).reshape((img.size[0], img.size[1]))
    new_data = np.zeros((img.size[0], img.size[1]))
    filtre = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            cell_value = 0
            # added_numbers = 0
            exception_occ = False
            for k in range(-(size - 1) // 2, (size // 2) + 1):
                for l in range(-(size - 1) // 2, (size // 2) + 1):
                    try:
                        cell_value += data[i + k][j + l] * filtre[k + 1][l + 1]
                        # added_numbers += 1
                    except IndexError:
                        exception_occ = True
                        pass
            if exception_occ:
                new_data[i][j] = 0
            else:
                new_data[i][j] = cell_value
    return new_data.reshape((img.size[0] * img.size[1],))


# offset = len(filtre) // 2
#     for i in range(offset, img.size[0] - offset):
#         for j in range(offset, img.size[1] - offset):
#             cell_value = 0
#             # added_numbers = 0
#             for k in range(len(filtre)):
#                 for l in range(len(filtre)):
#                     try:
#                         cell_value += data[i + k - offset][j + l - offset] * filtre[k][l]
#                         # added_numbers += 1
#                     except IndexError:
#                         pass
#             new_data[i][j] = cell_value


def apply_filter(img: Image, filtre):
    size = filtre.shape[0]
    data = np.array(list(img.getdata())).reshape((img.size[0], img.size[1]))
    new_data = np.zeros((img.size[0], img.size[1]))
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            cell_value = 0
            added_numbers = 0
            for k in range(-(size - 1) // 2, (size // 2) + 1):
                for l in range(-(size - 1) // 2, (size // 2) + 1):
                    try:
                        cell_value += data[i + k][j + l] * filtre[k + 1][l + 1]
                        added_numbers += 1
                    except IndexError:
                        pass
            new_data[i][j] = cell_value // added_numbers
    return new_data.reshape((img.size[0] * img.size[1],))


def erosion(img: Image, size=3):
    data = np.array(img.getdata()).reshape((img.size[0], img.size[1], 3))
    new_data = np.zeros((img.size[0], img.size[1]), dtype=tuple)
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            appartient = True
            for k in range(-(size - 1) // 2, (size // 2) + 1):
                for l in range(-(size - 1) // 2, (size // 2) + 1):
                    try:
                        if data[i + k][j + l][0] == VMAX and data[i + k][j + l][1] == VMAX and data[i + k][j + l][2] == VMAX:
                            appartient = False
                    except IndexError:
                        pass
            new_data[i][j] = (0, 0, 0) if appartient else (VMAX, VMAX, VMAX)
    return new_data.reshape((img.size[0] * img.size[1]))
