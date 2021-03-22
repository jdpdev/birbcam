def calculate_exposure(image):
    luminance = cvtColor(image, COLOR_BGR2GRAY)
    histogram = calcHist([luminance], [0], None, [256], [0,255])
    data = np.int32(np.around(histogram))

    max = data.max()
    average = 0
    total = 0

    for x, y in enumerate(data):
        average += y * x
        total += y

    return int(average / total)