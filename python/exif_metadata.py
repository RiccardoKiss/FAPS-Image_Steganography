from os import path
from PIL import Image, ExifTags

"""
samples   : https://github.com/ianare/exif-samples/tree/master/jpg
exif tags : https://www.exiv2.org/tags.html

"""

def printExifMetadata(img):
  exif_data = img.getexif()
  #print(exif_data)
  if exif_data is None or len(exif_data) == 0:
    print("Image has no Exif metadata.")
  else:
    for tag, val in exif_data.items():
      if tag in ExifTags.TAGS:
        print(f"{ExifTags.TAGS[tag]:30}: {val}")


def printImageData(filePath):
  print('-' * 50)
  img_name = path.basename(filePath)
  print(f"file: {img_name}")
  try:
    img = Image.open(filePath)
    print(f"image_format: {img.format}\nimage_mode: {img.mode}")
    if img.format == "PNG":
      img.load()
    #img.show() # zobrazi preview obrazka v .PNG
    print(f"info: {img.info}")
    #print(f"data: {list(img.getdata(0))}") # vypise tuple rgb hodnot kazdeho pixelu
    #print(f"color_palette: {img.getpalette()}")
    #print(f"histogram: {img.histogram()}")
    
    printExifMetadata(img)
  except FileNotFoundError:
    print(f"No such file: {img_name} !")

if __name__ == "__main__":
  #printImageData("../img/Canon_PowerShot_S40.jpg")
  #printImageData("../img/a.jpg")
  #printImageData("../img/pog.png")
  printImageData("../img/pngtest16rgba.png")
  printImageData("../img/pngtest16rgba_stego_2.png")
  printImageData("../img/msg_cross_32_32.png")
  printImageData("../img/msg_cross_32_32_stego_2_msg.png")
  #printImageData("../img/pngtest16rgba_stego_python.png")
  printImageData("../img/test.png")
  printImageData("../img/blackbuck_512x512.bmp")
  printImageData("../img/meadow_1280x853.bmp")