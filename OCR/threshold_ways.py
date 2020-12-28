def THRESH_BINARY(im, threshold):
    img = im.point(lambda x: 255 if x > threshold else 0, '1')
    return img


def THRESH_BINARY_INV(im, threshold):
    img = im.point(lambda x: 0 if x > threshold else 255, '1')
    return img


def THRESH_TOZERO(im, threshold):
    img = im.point(lambda x: x if x > threshold else 0, '1')
    return img


def THRESH_TOZERO_INV(im, threshold):
    img = im.point(lambda x: 0 if x > threshold else x, '1')
    return img


threshold_ways = {
    'BINARY': THRESH_BINARY,
    'BINARY_INV': THRESH_BINARY_INV,
    'TOZERO': THRESH_TOZERO,
    'TOZERO_INV': THRESH_TOZERO_INV,
}
threshold_name = [i for i in threshold_ways]
