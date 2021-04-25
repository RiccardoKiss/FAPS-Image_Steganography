import sys, getopt, time
from os import path
from PIL import Image


def printAllRGBvalues(img):
  print(f"pixel_values: {list(img.getdata())}")
  print(f"red_values: {list(img.getdata(0))}")
  print(f"green_values: {list(img.getdata(1))}")
  print(f"blue_values: {list(img.getdata(2))}")

def printIndexRGBvalues(img, index=0):
  print(f"pixel_value: {list(img.getdata())[index]}")
  print(f"red_value: {list(img.getdata(0))[index]}")
  print(f"green_value: {list(img.getdata(1))[index]}")
  print(f"blue_value: {list(img.getdata(2))[index]}")
  if img.mode == "RGBA":
    print(f"alpha_value: {list(img.getdata(3))[index]}")

def printPixelsRGBvalues(img, row=0, column=0):
  pixels = img.load()
  print(f"pixel_value: {pixels[column, row]}\n"
        f"red_value: {pixels[column, row][0]}\n"
        f"green_value: {pixels[column, row][1]}\n"
        f"blue_value: {pixels[column, row][2]}")
  if img.mode == "RGBA":
    print(f"alpha_value: {pixels[column, row][3]}")

def messageObjectType(msgObjectPath):
  messageObjectName = path.basename(msgObjectPath)
  file_type = messageObjectName[messageObjectName.index(".")+1:]
  #print(f"Message Object File Type: {file_type}")
  return file_type

def msgToBinaryArray(msg):
  binMsg = []
  for char in msg:
    binMsg.append(format(ord(char), '07b'))  # staci 7bitov, lebo posledne pismeno z = 0111 1010
  print(f"original message: {msg}\nbinary message  : {binMsg}")
  return binMsg

def msgToBinaryString(msg):
  binMsg = ""
  for char in msg:
    binMsg += format(ord(char), '07b')  # staci 7bitov, lebo posledne pismeno z = 0111 1010
  #print(f"original message: {msg}")
  #print(f"binary message  : {binMsg}")
  return binMsg

def leastSignificantBit_messageText(coverImg, binMsg, method=1):
  pixels = coverImg.load()
  img_size_X = coverImg.size[0]
  img_size_Y = coverImg.size[1]
  pixel_count = len(list(coverImg.getdata()))
  pixel_index = 0
  message_length = len(binMsg)
  print(f"count of pixels:{pixel_count}\nmessage length:{message_length}\n")
  
  row, column = 0, 0
  rgb_values = []
  for msg_index in range(0, message_length, 3*method):  # v kazdej iteracii prepisat jeden pixel
    rgb_values.clear()
    pixel_index += 1
    print(f"{pixel_index}.\nold pixel value: {pixels[column, row]}")

    for rgb in range(0, 3):  # 1 pixel
      color_value = "{0:b}".format(pixels[column, row][rgb])  # decimal int to binary string value
      #print(f"color_value:{color_value}")
      try:
        new_color_value = color_value[:8-method] + binMsg[msg_index+rgb*method : msg_index+rgb*method + method]
        #print(f"new_color_value:{new_color_value} = {color_value[:8-method]} + {binMsg[msg_index+rgb*method : msg_index+rgb*method + method]}")
        if len(new_color_value) < 8:
          new_color_value += color_value[len(new_color_value):]
        color_value = new_color_value
      except IndexError: 
        color_value = "{0:b}".format(pixels[column, row][rgb])
      #print(f"color_value:{color_value}")
      rgb_values.append(color_value)
      
    print(rgb_values)
    for i in range(0, len(rgb_values)):
      rgb_values[i] = int(rgb_values[i], 2)

    if coverImg.mode == "RGBA":
      alpha_value = pixels[column, row][3]
      rgb_values.append(alpha_value)
      
    pixels[column, row] = tuple(rgb_values)
    print(f"new pixel value: {pixels[column, row]}\n")
  
    column += 1
    if column >= img_size_X:
      row += 1
      column = 0
      
  return coverImg

def leastSignificantBit_messageImage(coverImg, msgImg, method=1):
  """
  loadnut coverImg a msgImg, prepisovat n-lsb v coverImg na n-msb z msgImg
  """
  pixels_coverImg = coverImg.load()
  pixels_msgImg = msgImg.load()
  rgb_values = []
  
  msgImg_size_X = msgImg.size[0]
  msgImg_size_Y = msgImg.size[1]
  pixel_index = 0

  for row in range(0, msgImg_size_Y):
    for column in range(0, msgImg_size_X):
      rgb_values.clear()
      #pixel_index += 1
      #if pixel_index <= 6:
        #print(f"old pixel value:{pixels_coverImg[column, row]}\tmsg pixel value:{pixels_msgImg[column, row]}")
      for rgb in range(0, 3):
        old_color_value = "{0:b}".format(pixels_coverImg[column, row][rgb])  # DECIMAL TO BINARY STRING
        msg_color_value = "{0:b}".format(pixels_msgImg[column, row][rgb])
        new_color_value = ""
        if len(old_color_value) > method:
          new_color_value += old_color_value[:-method] 
        new_color_value += msg_color_value[:method] 
        #if pixel_index <= 6:
          #print(f"new color value: {new_color_value}")
        rgb_values.append(new_color_value)
      
      #if pixel_index <= 6:
        #print(rgb_values)
      for i in range(0, len(rgb_values)):  # BINARY TO DECIMAL
        rgb_values[i] = int(rgb_values[i], 2)

      if coverImg.mode == "RGBA":
        alpha_value = pixels_coverImg[column, row][3]
        rgb_values.append(alpha_value)
      
      #if pixel_index <= 6:
        #print(rgb_values)
      pixels_coverImg[column, row] = tuple(rgb_values)
      #if pixel_index <= 6:
        #print(f"new pixel value: {pixels_coverImg[column, row]}\n")
  return coverImg

def getMessageText_From_StegoImage(img, method=1):
  pixels = img.load()
  stego_bin = ""
  stego_msg = ""
  img_size_X = img.size[0]
  img_size_Y = img.size[1]
  pixel_count = len(list(img.getdata()))
  row, column = 0, 0
  for pixel_index in range(0, pixel_count):
    #if pixel_index < 14:
      #print(f"{pixel_index+1}.")
    for rgb in range(0, 3):  # 1 pixel
      color_value = "{0:b}".format(pixels[column, row][rgb])
      if color_value == "0":
        color_value = color_value * method
      if len(color_value) < method:
        val = "0" * (method-len(color_value))
        val += color_value
        color_value = val
      """
      if pixel_index < 14:
        print(f"color_value:{color_value}")
        if rgb == 0:
          print(f"r:{color_value[len(color_value)-method:]}")
        if rgb == 1:
          print(f"g:{color_value[len(color_value)-method:]}")
        if rgb == 2:
          print(f"b:{color_value[len(color_value)-method:]}")
      """
      stego_bin += color_value[len(color_value)-method:]
    column += 1
    if column >= img_size_X:
      row += 1
      column = 0
  #print(f"stego_bin:{stego_bin}")
  for i in range(0, len(stego_bin), 7):
    steg_char = int(stego_bin[i:i+7], 2)  # BINARY TO DECIMAL
    steg_char = chr(steg_char)            # DECIMAL TO CHAR
    #print(f"steg_char:{steg_char}")
    if steg_char == '|':  # '|' as breaking point for stego message
      break
    if (steg_char >= 'A' and steg_char <= 'Z') or (steg_char >= 'a' and steg_char <= 'z'):
      stego_msg += steg_char

  print(f"stego_msg[{len(stego_msg)}]: {stego_msg}")
  return stego_msg

def getMessageImage_From_StegoImage(img, method=1):
  """
  loadnut img, z kazdeho rgb vybrat n-lsb a ukladat ich do noveho img ako n-msb a zvysok lsb doplnic nulami 
  alebo v jednej instancii img zobrat n-lsb a dat ich ako n-msb a n-lsb potom prepisat na nuly
  """
  pixels = img.load()
  rgb_values = []
  
  img_size_X = img.size[0]
  img_size_Y = img.size[1]
  pixel_index = 0
  for row in range(0, img_size_Y):
    for column in range(0, img_size_X):
      rgb_values.clear()
      pixel_index += 1
      #if row == 61 and column in range(17, 32):#if pixel_index <= 6:
        #print(f"pixel value: {pixels[column, row]}")
      for rgb in range(0, 3):
        color_value = "{0:b}".format(pixels[column, row][rgb])  # DECIMAL TO BINARY STRING
        #if row == 61 and column in range(17, 32):#if pixel_index <= 6:
          #print(f"color_value:{color_value} | {color_value[-method:]}")
        msg_color_value = color_value[-method:]  # GET N-LSB FROM STEGO IMAGE WHICH ARE N-MSB OF MESSAGE IMAGE
        msg_color_value += "0" * (8-method)  # APPEND REST OF MESSAGE COLOR BITS WITH ZEROS
        #print(f"new color value: {msg_color_value}")
        rgb_values.append(msg_color_value)
      
      #if row == 61 and column in range(17, 32):#if pixel_index <= 6:
        #print(rgb_values)
      for i in range(0, len(rgb_values)):
        rgb_values[i] = int(rgb_values[i], 2)

      if img.mode == "RGBA":
        alpha_value = pixels[column, row][3]
        rgb_values.append(alpha_value)
      
      #if row == 61 and column in range(17, 32):#if pixel_index <= 6:
        #print(rgb_values)
      pixels[column, row] = tuple(rgb_values)
      #if row == 61 and column in range(17, 32):#if pixel_index <= 6:
        #print(f"new pixel value: {pixels[column, row]}\n")
  return img


def main(argv):
  coverImage = ""
  messageObject = ""
  method = 1
  try:
    opts, args = getopt.getopt(argv, "hM:c:m:", ["help", "method=", "coverImage=", "messageObject="])
    print(f"opts: {opts}")
    for opt, arg in opts:
      if opt in ("-h", "--help"):
        print("SYNOPSIS"
              "\n\tpython lsb.py [-M <method>] -c <coverImage> -m <messageObject>\n"
              "DESCRIPTION"
              "\n\t-h, --help\n\t\tprint example of running script and description of arguments\n"
              "\n\t-M, --method=[1,2,4,6] (optional argument)\n\t\tto set LSB method to use (DEFAULT=1)"
              "\n\t\t\t1 = standard LSB method by altering ONE least significant bit of each RGB channel (suggested for text)"
              "\n\t\t\t2 = TWO least significant bits of RGB channels are used for message object (suggested for longer text)"
              "\n\t\t\t4 = FOUR least significant bits of RGB channels are used for message object (suggested for message image)"
              "\n\t\t\t6 = SIX least significant bits of RGB channels are used for message object (not suggested)"
              "\n\t-c, --coverImage=FILEPATH (required argument)\n\t\tset path to the image (PNG, BMP) used as cover image"
              "\n\t-m, --messageObject=FILEPATH (required argument)\n\t\tset path to the file (TXT, PNG, BMP) used as message object or write message string (e.g., -m \"this is message\")\n"
              "EXIT STATUS:"
              "\n\t0\tif OK,"
              "\n\t1\tif minor problems (e.g., cannot access subdirectory),"
              "\n\t2\tif serious trouble (e.g., cannot access command-line argument).")
        sys.exit(0)
      elif opt in ("-M", "--method"):
        method = int(arg)
        print(f"Method: {method} Least Significant Bits")
      elif opt in ("-c", "--coverImage"):
        coverImagePath = arg
        coverImageName = path.basename(coverImagePath)
        print(f"Cover Image: {coverImagePath} | {coverImageName}")
      elif opt in ("-m", "--messageObject"):
        messageObjectPath = arg
        messageObjectName = path.basename(messageObjectPath)
        print(f"Message Object: {messageObjectPath} | {messageObjectName}")

    try:
      coverImage = Image.open(coverImagePath)
      pixels = coverImage.load()
      print(f"Cover Image Size: {coverImage.size[0]}x{coverImage.size[1]}")
      if messageObjectType(messageObjectPath) in ("png", "bmp"):
        messageImage = Image.open(messageObjectPath)
        pixels = messageImage.load()
        print(f"Message Image Size: {messageImage.size[0]}x{messageImage.size[1]}")
        if messageImage.size[0] > coverImage.size[0] or messageImage.size[1] > coverImage.size[1]:
          print("Message Image too large!")
        else:
          start = time.perf_counter()
          stego_img = leastSignificantBit_messageImage(coverImage, messageImage, method)
          end = time.perf_counter()

          print(f"Elapsed time:{end-start:0.4f}s\n{coverImagePath[:-4]}_stego_{method}{coverImagePath[-4:]}")
          try:
            stego_img.save(f"{coverImagePath[:-4]}_stego_{method}{coverImagePath[-4:]}")
          except OSError:
            print(f"File {coverImageName} could not be written!")
          
          start = time.perf_counter()
          msg_img = getMessageImage_From_StegoImage(coverImage, method)  # optional - presunut potom do zvlast scriptu
          end = time.perf_counter()

          print(f"Elapsed time:{end-start:0.4f}s\n{messageObjectPath[:-4]}_stego_{method}_msg{messageObjectPath[-4:]}")
          try:
            msg_img.save(f"{messageObjectPath[:-4]}_stego_{method}_msg{messageObjectPath[-4:]}")
          except OSError:
            print(f"File {messageObjectName} could not be written!")

      elif messageObjectType(messageObjectPath) == "txt":
        with open(messageObjectPath, "r") as messageObjectFile:
          fileMsg = messageObjectFile.read()
          print(f"Message from TXT file: {fileMsg}")
          fileMsg += "|"
          binMsg = msgToBinaryString(fileMsg)
          
          message_length = len(binMsg)
          pixel_count = len(list(coverImage.getdata()))
          if message_length > pixel_count*3*method:  
            print("Message too long!")
          else:
            start = time.perf_counter()
            stego_img = leastSignificantBit_messageText(coverImage, binMsg, method)
            end = time.perf_counter()

            print(f"Elapsed time:{end-start:0.4f}s\n{coverImagePath[:-4]}_stego_{method}{coverImagePath[-4:]}")
            try:
              stego_img.save(f"{coverImagePath[:-4]}_stego_{method}{coverImagePath[-4:]}")
            except OSError:
              print(f"File {coverImageName} could not be written!")

            start = time.perf_counter()
            msg_text = getMessageText_From_StegoImage(coverImage, method)  # optional - presunut potom do zvlast scriptu
            end = time.perf_counter()

            print(f"Elapsed time:{end-start:0.4f}s\n{messageObjectPath[:-4]}_stego_msg{messageObjectPath[-4:]}")
            with open(f"{messageObjectPath[:-4]}_stego_msg{messageObjectPath[-4:]}", "w") as stego_msg:
              stego_msg.write(msg_text)
      
    except FileNotFoundError:
      print(f"No such file: {coverImageName} !")
  except getopt.GetoptError:
    print("Try using -h or --help!")
    sys.exit(2)

  
if __name__ == "__main__":
  main(sys.argv[1:])
"""
  filePath = "../img/pngtest16rgba.png"
  imgName = path.basename(filePath)
  
  try:
    img = Image.open(filePath)
    pixels = img.load()
    print(f"pixels: \n{pixels[0,0]}\n{pixels[0,1]}\n{pixels[0,2]}\n{pixels[0,3]}\n{pixels[0,4]}\n{pixels[0,5]}\n{pixels[0,6]}")
    print(f"image size: {img.size[0]}x{img.size[1]}")
    printIndexRGBvalues(img) # optional
    #gsm = msgToBinaryArray("py")
    msg = msgToBinaryString("python")
    old_msg = getMessageTextFromStegoImage(img)  # optional - presunut potom do zvlast scriptu
    a = leastSignificantBit_messageText(img, msg)
    steg_msg = getMessageTextFromStegoImage(img)  # optional - presunut potom do zvlast scriptu
    try:
      img.save("../img/pngtest16rgba_stego_python_alpha255.png")
    except OSError:
      print(f"File {imgName} could not be written!")
  
  except FileNotFoundError:
    print(f"No such file: {imgName} !")
  """
  
