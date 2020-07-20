import configparser
from PIL import Image, ImageFont, ImageDraw, ImageOps
import shutil
import os
import textwrap
import numpy as np
import random
import sys

class main:
    def __init__(self):
        folders = ["squares", "grids", "Finished Boards"]
        for folder in folders:
            if os.path.exists(folder):
                shutil.rmtree(folder)
            os.mkdir(folder)

        # Parse the config
        cfgParse = configparser.ConfigParser()
        cfgParse.read("./config.txt")
        optionsStr = cfgParse['options']['options']
        self.options = optionsStr.split("|")  # Everything in options should be separated by pipes
        self.options = [x.strip(' ') for x in self.options]  # Get all options as a clean list

        # Magic Numbers
        self.TEXTWIDTH = int(cfgParse['config']['TextWidth'])
        self.FONTSIZE = int(cfgParse['config']['FontSize'])
        self.STARTINGHEIGHT = int(cfgParse['config']['StartingHeight'])
        self.BORDERSIZE = int(cfgParse['config']['BorderSize'])
        self.TEXTCOLOR = cfgParse['config']['TextColor']
        self.BORDERCOLOR = cfgParse['config']['BorderColor']
        self.TEXTFONT = cfgParse['config']['TextFont']
        self.FREESPACE = cfgParse['config']['FreeSpace']
        self.BOARDSTOMAKE = int(cfgParse['config']['BoardsToMake'])
        self.PASTELOCATION = [int(i) for i in cfgParse['config']['PasteLocation'].split(",")]

        self.baseSquare = "square.png"

    def progress(self, count, total):
        # Draw a progress bar for things that take forever, like updating status
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))

        percents = round(100.0 * count / float(total), 1)
        bar = '=' * filled_len + '-' * (bar_len - filled_len)

        sys.stdout.write('[%s] %s%s \r' % (bar, percents, '%'))
        sys.stdout.flush()

    def createSquares(self):
        self.options.insert(0, self.FREESPACE)

        for iteration, phrase in enumerate(self.options):
            text = textwrap.wrap(phrase, width=self.TEXTWIDTH)
            out_img = "squares/%s.png" % iteration

            MAX_W, MAX_H = 200, 200
            im = Image.new('RGBA', (MAX_W, MAX_H), (0, 0, 0, 0))
            draw = ImageDraw.Draw(im)
            font = ImageFont.truetype(self.TEXTFONT, self.FONTSIZE)

            current_h, pad = self.STARTINGHEIGHT, 10
            for line in text:
                w, h = draw.textsize(line, font=font)
                draw.text(((MAX_W - w) / 2, current_h), line, 'black', font=font)
                current_h += h + pad

            imgBorder = ImageOps.expand(im, border=self.BORDERSIZE, fill='black')
            imgBorder.save(out_img)

    def randomizeImages(self):
        fileNames = []
        for file in os.listdir("squares"):
            if not file == "0.png":
                fileNames.append("squares/" + file)
        random.shuffle(fileNames)
        fileNames.insert(12, "squares/0.png")  # Force 1.png (Free space) into the 13th space (Center)
        allFileNames = []

        for i in range(0, 25, 5):
            allFileNames.append(fileNames[i:i + 5])  # Split file names by chunks of 5, max of 25 for 5 rows

        return allFileNames

    def createGrid(self, allRows, iteration):
        grid = []
        for row in allRows:
            list_im = row
            imgs = [Image.open(i) for i in list_im]
            # pick the image which is the smallest, and resize the others to match it (can be arbitrary image shape here)
            min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]
            imgs_comb = np.hstack((np.asarray(i.resize(min_shape)) for i in imgs))

            # save that beautiful picture
            imgs_comb = Image.fromarray(imgs_comb)
            grid.append(imgs_comb)
            #imgs_comb.save('rows/%s.png' % iteration)
        # Create grid

        imgs = grid
        # pick the image which is the smallest, and resize the others to match it (can be arbitrary image shape here)
        min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]

        imgs_comb = np.vstack((np.asarray(i.resize(min_shape)) for i in imgs))
        imgs_comb = Image.fromarray(imgs_comb)
        imgs_comb.save('grids/%s.png' % iteration)

    def boardOntoBkg(self, iteration):
        bkg = Image.open('background.png')
        grid = Image.open('grids/%s.png' % iteration)
        bkgCopy = bkg.copy()
        gridCopy = grid.copy()
        bkgCopy.paste(gridCopy, self.PASTELOCATION, gridCopy)
        bkgCopy.save('Finished Boards/%s.jpg' % iteration, quality=95)


if __name__ == "__main__":
    Main = main()
    print("Generating bingo boards, please wait...")
    for board in range(Main.BOARDSTOMAKE):
        Main.createSquares()
        allImages = Main.randomizeImages()
        Main.createGrid(allImages, board)
        Main.boardOntoBkg(board)
        Main.progress(board, Main.BOARDSTOMAKE)

    print("Finished! Check out your completed bingo boards in the Finished Boards folder.")
