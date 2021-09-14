import sys
import os
import tkinter as tk
import numpy as np 
import io
import base64
from PIL import Image 
from fpdf import FPDF 
import pyscreenshot as pys 
from PIL import ImageGrab 
from PyQt5.QtWidgets import QFileDialog, QScrollArea, QWidget, QHBoxLayout, QMenuBar, QVBoxLayout, QPushButton, QApplication, QSizePolicy,  QMainWindow, QMenu, QAction, QLabel
from PyQt5.QtGui import QPalette, QImage, QBrush, QPainter, QPen, QColor, QIcon, QCursor, QPixmap
from PyQt5.QtCore import  QBuffer, QByteArray, QFileInfo, QPoint, Qt, QRectF, QSize
from PyQt5.QtPrintSupport import QPrinter

global isSnipping 
isSnipping = True 

class PastWindow(QWidget): 
    def __init__(self): 
        super().__init__()

        global imgArray
        global nameImgArray

        self.setWindowTitle('History')
        self.scroll = QScrollArea()
        self.widget = QWidget()
        self.box = QVBoxLayout()

        tempImg = np.array([[]])

        for i in range(nameImgArray):
            tempImg = np.append(tempImg, QImage(imgArray[i]))

        for i in range(nameImgArray):  
            self.image = QPixmap(tempImg[i])
            self.label = QLabel()
            self.label.setPixmap(self.image) 
            self.box.addWidget(self.label)
            
        self.widget.setLayout(self.box)

        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        scroll_lay = QVBoxLayout()
        scroll_lay.addWidget(self.scroll)
        self.setLayout(scroll_lay)
        self.show()

class AppendWindow(QMainWindow): 
    def __init__(self): 
        super().__init__() 
        self.latestSnip()
     
    def _createMenuBar(self): 
        menuBar = QMenuBar()
        self.setMenuBar(menuBar)
        
        optionMenu = QMenu("&File", self)
        menuBar.addMenu(optionMenu)
    
        self.printPreview = QAction("&Print", self)
        self.displayHistoryOption = QAction("&History", self)

        optionMenu.addAction(self.printPreview)
        optionMenu.addAction(self.displayHistoryOption)
        
        self.printPreview.triggered.connect(self.printHistory)
        self.displayHistoryOption.triggered.connect(self.displayHistory)

    def printHistory(self): 
        global imgArray
        global printImgArray
        global nameImgArray

        image_list = []
       
        for x in range(nameImgArray):
            data = QByteArray()
            buf = QBuffer(data)
            imgArray[x].save(buf, 'PNG')
            sixtyFour = data.toBase64()
            data = base64.b64decode(sixtyFour)
            img = Image.open(io.BytesIO(data))
            img = img.convert('RGB')
            image_list.append(img)

        pdf = FPDF() 

        fn, _ = QFileDialog.getSaveFileName(self, 'Export PDF', None, 'PDF files (.pdf);;All Files()')
        
        if fn != '':
            if QFileInfo(fn).suffix() == "": fn += '.pdf'
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(fn)
            pdf.output(fn, "F")
            image_list[0].save(fn, save_all=True,append_images=image_list[1:])


    def displayHistory(self): 
        print("History is displayed!\n")
        self.historyWindow = PastWindow()
        self.historyWindow.show()


    def latestSnip(self):
        if(os.path.isfile("clip.png")):
            self._createMenuBar()
          
            global imgArray
            global printImgArray
            global nameImgArray

            img = QImage('clip.png')   
            imgArray = np.append(imgArray, img)
            testImg = np.array(['clip.png'])
            printImgArray = np.append(printImgArray, testImg)

            self.resize(img.size()) # Set Dimmensions to Image Dimmensions 
            self.setWindowTitle("Snippilation")
            palette = QPalette()

            palette.setBrush(QPalette.Window, QBrush(img))
            self.setPalette(palette)    
            self.show()

        else: 
            print('no image')

# New Window Popup for Snipping 
class SnipperWindow(QWidget):
    def __init__(self):
        # Main Window Constructor
        super().__init__()
        # Set layout window 
        layout = QVBoxLayout()
        # Create Palette
        palette = QPalette()
        # Add layout to window
        self.setLayout(layout)

        # Take Screenshot
        screenshot = pys.grab()

        # Save Screenshot 
        screenshot.save("screenshot.png") 

        # Grab the image 
        img = QImage("screenshot.png")     

        # Initalize w/ not snipping 
        global isSnipping 
        isSnipping = True

        # self.isSnipping = True 
        self.numberSnips = 0 
         
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight() 
        self.setGeometry(0, 0, screen_width, screen_height)

        # Mouse Position is initalize to 0
        self.begin = QPoint()
        self.end = QPoint()

        # Add to palette
        palette.setBrush(QPalette.Window, QBrush(img))

        # Set window to smaller opacity
        self.setWindowOpacity(.2) 

        # Add palette to window
        self.setPalette(palette)

        # Maximize window
        self.showMaximized()

        # Window is frameless
        self.setWindowFlags(Qt.FramelessWindowHint)

    def getSnippingValue(self):
        return self.isSnipping

    # Drawing Rectangle
    def paintEvent(self, event): 
        # When Snipping
        global isSnipping 
        # if self.isSnipping: 
        if isSnipping: 
            lw = 3 # 1
            opacity = 1
            brush_color = (128, 128, 255, 100)

        else: 
            brush_color = (0, 0, 0, 0)
            lw = 0
            opacity = 0

        self.setWindowOpacity(opacity)

         # QPainter Initalize
        qp = QPainter(self) 
        qp.setPen(QPen(QColor('black'),lw))
        qp.setBrush(QColor(*brush_color))
        rect = QRectF(self.begin, self.end)
        
        qp.drawRect(rect)

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()
    
    def mouseReleaseEvent(self, event): 
        global isSnipping 
        isSnipping = False 
        QApplication.restoreOverrideCursor()
        self.repaint() 

        x1 = min(self.begin.x(), self.end.x())
        y1 = min(self.begin.y(), self.end.y())
        x2 = max(self.begin.x(), self.end.x())
        y2 = max(self.begin.y(), self.end.y())
        
        QApplication.processEvents()

        print(x1, y1, x2, y2)
        
        QApplication.processEvents()

        img = ImageGrab.grab(bbox = (x1, y1, x2, y2)) 
        img.save('clip.png')   
        self.close()

        global nameImgArray
        nameImgArray+=1
        self.main = AppendWindow()

# Main Application that runs the Snipping Tool
class MainApplication(QWidget):
    # Main function
    def __init__(self):
        # Main Window Constructor
        super().__init__()

        # Title Window 
        self.setWindowTitle("Snipping Tool")

        # Initalize the program to specific dimmentions 
        self.resize(300, 100)

        # Disable Full Screen Mode W/Out Close Button Disabled, and Window will always be the first application running on top
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowStaysOnTopHint)
       
        # Create Snip Button 
        self.snip_button = QPushButton('Snip')
        
        # Window adjusts, snip button resizes 
        self.snip_button.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        # Add Image for Snipping Icon 
        self.snip_button.setIcon(QIcon('SnippingToolLogo.png'))

        # Set dimmension size both for Snip & Cancel Icons
        self.snip_button.setIconSize(QSize(50,50))
        
        # Add Main Layout
        main_layout = QHBoxLayout()

        # Add layout to main frame 
        self.setLayout(main_layout)

        main_layout.addWidget(self.snip_button)

        # Connect the two functions into the two buttons 
        self.snip_button.clicked.connect(self.clickSnip)

        # End of Main UI Code
        self.show()

    # When User click on Snipping Button
    def clickSnip(self): 
        # Minimized Snipping Window 
        self.showMinimized()

        # Initalize the Object and Screenshot the background
        self.anotha = SnipperWindow()
        # Bring back the Snipping Window 
        self.showNormal()

        # Display the Gray Window 
        self.anotha.show()

        # Override cursor to be a cross cursor   
        QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))
       

# Main Function 
if __name__ == '__main__':
    if(os.path.isfile("clip.png")):
        os.remove("clip.png")
    
    if(os.path.isfile("screenshot.png")):
        os.remove("screenshot.png")
    
    app = QApplication(sys.argv)

    imgArray = np.array([[]])
    printImgArray = np.array([[]])

    nameImgArray = 0
    mw = MainApplication()
    sys.exit(app.exec())