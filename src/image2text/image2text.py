from img import Img

def main():
    img = Img("in.png")
    img.resizePercent(0.6, 0.2) # 修正 英文/半角 字符较为细长导致的变形
    tmp = open("out.txt","w")
    tmp.write(img.toText())
    tmp.close()

if __name__ == "__main__":
    main()