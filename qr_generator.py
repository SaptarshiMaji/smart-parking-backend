import qrcode
import os

def generate_qr(data, filename):

    folder = "qr_codes"

    if not os.path.exists(folder):

        os.makedirs(folder)

    path = f"{folder}/{filename}.png"

    img = qrcode.make(data)

    img.save(path)

    return path