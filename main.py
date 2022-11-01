from __future__ import print_function
from importlib.metadata import metadata
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow,QFileDialog,QMessageBox,QWidget
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from GUIFINAL import Ui_MainWindow
import qdarkstyle
from PyQt5.QtGui import QPixmap
from PIL import Image
from PIL.ExifTags import TAGS
import os.path
import os
#import scipy.misc
import imageio
from pydicom import dcmread
from pydicom.data import get_testdata_file
import numpy
from PIL.ImageQt import ImageQt
import cv2
import math
from mplwidget import MplWidget 
#from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
import random
import matplotlib.image as img

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #Variables
        self.data=[]
        self.greyImageArray=[]
        self.factor=0.1
        self.flag=1
        #self.allModes= {'1':1, 'L':8, 'P':8, 'RGB':24, 'RGBA':32, 'CMYK':32, 'YCbCr':24, 'I':32, 'F':32}
        self.allModes={"1": 1, "L": 8, "P": 8, "RGB": 24, "RGBA": 32, "CMYK": 32, "YCbCr": 24, "LAB": 24, "HSV": 24, "I": 32, "F": 32} #all image modes supported
       
        ##add the T image
        image = Image.open("TImage.jpg")#store the data and meta data of the image
        self.original_T_ImageArray=numpy.asarray(image).astype(int)
        #print(self.original_T_ImageArray)
        self.drawimage(0,self.original_T_ImageArray)
        #triggers and connections
        self.ui.actionBrowse_Image.triggered.connect(self.Browsefile) #button to call function browse
        self.ui.checkBox_nearest.stateChanged.connect(lambda: self.state_changed(0))
        self.ui.checkBox_linear.stateChanged.connect(lambda: self.state_changed(1))
        self.ui.lineEdit.returnPressed.connect(self.getfactor)
        self.ui.Angle_lineEdit.returnPressed.connect(self.getAngle)
        self.ui.comboBox.currentIndexChanged.connect(self.getAngle)
        self.ui.radioButton_positive.toggled.connect(lambda: self.ShearingHorizontally(0))
        self.ui.radioButton_negative.toggled.connect(lambda: self.ShearingHorizontally(1))

        





    def Browsefile(self):
        self.path = QFileDialog.getOpenFileName(self, 'Open a file', '') #open browse window
        if self.path != ('', ''):
            self.data = self.path[0]
            ###
            #testImage = img.imread(self.path)

            ###  #get the file path only from the openfilename
            if self.data.find(".dcm") !=-1: #test if it is dcm call readdata for dicom
                try: # test if somthing is wrong with the file display the msg if nothing wrong display the image
                    self.readdatadicom()
                except:
                    self.messagebox('Error Occured: this Image is Corrupted, Upload another image')
                    self.resettext()
                    self.greyImageArray.clear()
            else:
                ###self.readmetadata()#sheel dah law shghalt el try we el except
                try: # test if somthing is wrong with the file display the msg if nothing wrong display the image
                    self.readmetadata()
                except:
                    #self.ui.ImageDisplay_label.setText("This Image is Corrupted, Upload another image")
                    self.messagebox('Error Occured: this Image is Corrupted, Upload another image')
                    self.resettext()
                    self.greyImageArray.clear()  
                else:
                    self.displaymetadata() 

    def readmetadata(self):
        self.ui.ImageDisplay_label.setPixmap(QPixmap(self.data))#upload the image using Qpixmap function and set it as label background
        self.ui.ImageDisplay_label.setScaledContents(1)#scale the image to fill the label
        image = Image.open(self.data)#store the data and meta data of the image
        self.imgheight=image.height #get image height
        self.imgwidth=image.width   #get image width
        self.imgmode=image.mode     #get image mode
        self.originalimagearray=numpy.asarray(image).astype(float)
        self.bitsperpixel=round(numpy.log2((numpy.max(self.originalimagearray)-numpy.min(self.originalimagearray)))) #get the bitdepth from the array
        self.filesizeinbit=image.height*image.width*self.bitsperpixel #get the image mode from the image data and find the bitdepth from the all mode array and multiply by width and height 
        #self.ui.Before_graphicsView.canvas.axes.imshow(self.originalimagearray)
        #self.ui.Before_graphicsView.canvas.axes.draw(self)
        
        #self.filesizeinbit=os.path.getsize(self.data)*8
        #file_size = os.stat(str(self.data))
        #print("Size of file :", file_size.st_size*8, "bits")
        #self.bitsperpixel=self.allModes[image.mode] #get the bitdepth from the array
        if (image.mode=="RGB" or image.mode=="L" ):
            self.convert2grey(0)
            self.flag=1
        else:
            self.flag=0    
        # if (self.imgmode=="RGB"):
        #    self.greyImage=image.convert('L')
        #    self.greyImageArray=numpy.asarray(self.greyImage)

        #    ##### El Mafrood asheel kol dah lama a3rad ezay a7wel men Pil le Qpuxmap 3ala tool
        #    self.greyImage.save('erock_gray.jpg')
        #    self.ui.ImageDisplay_label.setPixmap(QPixmap('erock_gray.jpg'))#upload the image using Qpixmap function and set it as label background
        #    self.ui.ImageDisplay_label.setScaledContents(0)#scale the image to fill the label
        #    print(self.greyImageArray)
        #    print(self.greyImageArray.shape)
        #    self.nearest_interpolation()
 
  

    def displaymetadata(self):
        #display all you read from the image meta data you got from th readmetadata function 
        self.ui.IWdisplay_label.setText(str(self.imgwidth))    
        self.ui.IHdisplay_label.setText(str(self.imgheight))
        self.ui.ICdisplay_label.setText(str(self.imgmode))
        self.ui.ISdisplay_label.setText(str(self.filesizeinbit))
        self.ui.BDdisplay_label.setText(str(self.bitsperpixel))
        self.ui.MUdisplay_label.setText("Not Available")
        self.ui.PNdisplay_label.setText("Not Available")
        self.ui.PAdisplay_label.setText("Not Available")
        self.ui.BPdisplay_label.setText("Not Available")

    def resettext(self):
        # because when changing between corrupted and none corrupted images some meta data could be read but the image itself not so i must reset every thing
        self.ui.IWdisplay_label.setText("Not Available")
        self.ui.IHdisplay_label.setText("Not Available")
        self.ui.BDdisplay_label.setText("Not Available")
        self.ui.ICdisplay_label.setText("Not Available")
        self.ui.ISdisplay_label.setText("Not Available")
        self.ui.MUdisplay_label.setText("Not Available")
        self.ui.PNdisplay_label.setText("Not Available")
        self.ui.PAdisplay_label.setText("Not Available")
        self.ui.BPdisplay_label.setText("Not Available")    

    def readdatadicom(self):
        #self.datafordicom=self.data[self.data.rfind('/')+1:]
        #print(self.datafordicom)
        #fpath = get_testdata_file(str(self.data))
        #print(fpath)

        #new_image=self.ds.pixel_array.astype(float) #convert the array to float to not loose data
        #scaled_image=(np.maximum(new_image,0)/new_image.max())*(2^self.ds.BitsStored) #normalize the array from 0-255 
        #imageio.imwrite('outfile.bmp',new_image) #open a file and write the data you normalized in it

        self.ds = dcmread(self.data) #read all dicom file data
        #print(self.ds)
        imageio.imwrite('outfile.bmp',self.ds.pixel_array.astype(float)) #open a file and write the data you normalized in it
        self.ui.ImageDisplay_label.setPixmap(QPixmap('outfile.bmp'))#upload the image using Qpixmap function and set it as label background
        self.ui.ImageDisplay_label.setScaledContents(1)#scale the image to fill the label
        self.greyImageArray=numpy.asarray(self.ds.pixel_array.astype(float))#read data and put in an array to deal with it easily
        
        #try searching for each attribute if found display it if not display not found
        try:
            self.imgheight=self.ds.Columns
        except:
            self.ui.IHdisplay_label.setText(str("Columns Not Found")) 
        else:
            self.ui.IHdisplay_label.setText(str(self.imgheight))   

        try:
            self.imgwidth=self.ds.Rows
        except:
            self.ui.IWdisplay_label.setText(str("Rows Not Found"))
        else:
            self.ui.IWdisplay_label.setText(str(self.imgwidth))

        try:
            self.imgmode=self.ds.PhotometricInterpretation
        except:
            self.ui.ICdisplay_label.setText(str("Image Mode Not Found"))  
        else:
            self.ui.ICdisplay_label.setText(str(self.imgmode))

        try:
            self.bitsperpixel=self.ds.BitsStored
        except:
            self.ui.BDdisplay_label.setText(str("Bit depth Not Found"))
        else:
            self.ui.BDdisplay_label.setText(str(self.bitsperpixel))
        

        try:
            self.filesizeinbit=self.imgheight*self.imgwidth*self.ds.BitsStored
        except:
            self.ui.ISdisplay_label.setText(str("File Size Not Found"))
        else:
            self.ui.ISdisplay_label.setText(str(self.filesizeinbit))
        
        
        try:
            self.imgModalitity=self.ds.Modality
        except:
            self.ui.MUdisplay_label.setText(str("Modality Not Found"))
        else:
            self.ui.MUdisplay_label.setText(str(self.imgModalitity))        
        
        try:
            self.patientAge=self.ds.PatientAge
        except:
            self.ui.PAdisplay_label.setText(str("Age Not Found")) 
        else:
            self.ui.PAdisplay_label.setText(str(self.patientAge)) 

        try:
            self.patientName=self.ds.PatientName
        except:
            self.ui.PNdisplay_label.setText(str("Patient Name Not Found"))
        else:
            self.ui.PNdisplay_label.setText(str(self.patientName))                   

        #i found out that body part examined could be in bodypartexamined attribute or in study description so i test if found in body part display it if not try study description
        try:
            self.bodypartexamineted=self.ds.BodyPartExamined
        except:
            self.study_description()
        else:
            self.ui.BPdisplay_label.setText(str(self.bodypartexamineted))


    def  study_description(self):
        # to test if the study description found, if found display it if not display Body part Not found 
        try:
            self.bodypartexamineted=self.ds.StudyDescription
        except:
            self.ui.BPdisplay_label.setText(str("Bodypart Examineted Not Found"))
        else:
            self.ui.BPdisplay_label.setText(str(self.bodypartexamineted)) 

        #self.bodypartexamineted=self.ds.StudyDescription
        #self.bodypartexamineted=self.ds.BodyPartExamined

    #def displaymetadatadicom(self):
        #self.ui.IWdisplay_label.setText(str(self.imgwidth))    
        #self.ui.IHdisplay_label.setText(str(self.imgheight))
        #self.ui.ICdisplay_label.setText(str(self.imgmode))
        #self.ui.ISdisplay_label.setText(str(self.filesizeinbit))
        #self.ui.BDdisplay_label.setText(str(self.bitsperpixel))
        #self.ui.MUdisplay_label.setText(str(self.imgModalitity))
        #self.ui.PAdisplay_label.setText(str(self.patientAge))
        #self.ui.PNdisplay_label.setText(str(self.patientName))
        #self.ui.BPdisplay_label.setText(str(self.bodypartexamineted))
    def linear_interpolation(self):
        self.resizedArrayInterpolation=numpy.zeros((self.newdimention,self.newdimention))#initialize an array with zeros array of the new image
        self.resizedArrayInterpolation.fill(-1)#fill this array with a value out of range to make it unique

        if (self.factor>1):
            self.spacing=numpy.floor(self.factor)
            self.resizedArrayInterpolation[0][0]=self.greyImageArray[0][0]
            self.resizedArrayInterpolation[0][-1]=self.greyImageArray[0][-1]
            self.resizedArrayInterpolation[-1][0]=self.greyImageArray[-1][0]
            self.resizedArrayInterpolation[-1][-1]=self.greyImageArray[-1][-1]

        for i in range(1,len(self.greyImageArray)-1,self.spacing):
            for j in range(1,len(self.greyImageArray)-1,self.spacing):
                self.resizedArrayInterpolation[i][j]=1############

  

    def state_changed(self,x):
        if (x==0):
            if (self.ui.checkBox_nearest.isChecked()):
                self.ui.groupBox_6.hide()
            else:
                self.ui.groupBox_6.show()
        else:
            if (self.ui.checkBox_linear.isChecked()):
                self.ui.groupBox_7.hide()
            else:
                self.ui.groupBox_7.show() 

    def getfactor(self):
        #this means the image is not RGB
        if (self.flag==0):
            self.messagebox("ERORR: Upload an RGB/greyscale image")
            self.ui.lineEdit.clear()
            return
        #there must be an image to resize the factor on it 
        try:
            assert len(self.greyImageArray)!=0
        except:
            self.messagebox("ERORR: Upload the image first then add the factor")
            self.ui.lineEdit.clear()
        else:
            #factor can't be string such as alphabets and typos such as 0.1.1
            try:
                float(self.ui.lineEdit.text())
            except:
                self.messagebox("ERORR: Enter a float/int +ve number & zeros are not accepted")
                self.ui.lineEdit.clear()
            else:
                #factor can't be negative or zero
                try:
                    assert self.ui.lineEdit.text()>str(0)
                except:
                    self.messagebox("ERORR: Enter a +ve number & zeros are not accepted")
                    self.ui.lineEdit.clear()
                else:        
                    self.factor=float(self.ui.lineEdit.text())
                    self.ui.ImageDisplay_label.setScaledContents(0)#donot scale it to see the effect of zooming factor
                    #self.newdimention=int(self.greyImageArray.shape[0]*self.factor)
                    self.newXdimention=int(self.greyImageArray.shape[0]*self.factor)
                    self.newYdimention=int(self.greyImageArray.shape[1]*self.factor)
                    #self.nearest_interpolation()
                    self.nearest_Interpolation()
                    self.linear_Interpolation()

    def getAngle(self):
        try:
            float(self.ui.Angle_lineEdit.text())
        except:
            self.messagebox("ERORR: Enter a float/int +ve or -ve number ")
            self.ui.Angle_lineEdit.clear()
        else:
            self.Rotate(numpy.radians(float(self.ui.Angle_lineEdit.text())),self.original_T_ImageArray)
            if (float(self.ui.Angle_lineEdit.text())>0):
                newstring=str(self.ui.Angle_lineEdit.text())
                self.ui.NewImageDirection_label_display.setText("Left")
                self.ui.NewImageAngle_label_display.setText(newstring)
            elif(float(self.ui.Angle_lineEdit.text())<0):
                newstring=str(float(self.ui.Angle_lineEdit.text())*-1)
                self.ui.NewImageDirection_label_display.setText("Right")
                self.ui.NewImageAngle_label_display.setText(newstring)



    def convert2grey(self,x):
        if (x==0):
            image = Image.open(self.data)#store the data and meta data of the image
            if (image.mode=="RGB"):
                self.greyImage=image.convert('L')
                self.greyImageArray=numpy.asarray(self.greyImage)
            elif(image.mode=='L'):
                self.greyImageArray=numpy.asarray(image)
            else:
                self.messagebox("Please Add an RGB or grey scale image")    

    def roundForInterpolation(self,array):
        #print(len(array),array)
        for i in range(len(array)):
                frac,whole=math.modf(array[i])
                if (frac<=0.5):
                    array[i]=whole
                else:
                    array[i]=math.ceil(array[i])
        return array

    def nearest_Interpolation(self):

        # arr=[[0.5,0.56],[2.5,2.67]]
        # arr2=self.roundForInterpolation(arr)
        # print(arr2)
        

        arrangedXArray=numpy.arange(0,self.newXdimention)#initialize an array from 0-(width size)*factor array representing coordinates
        arrangedYArray=numpy.arange(0,self.newYdimention)#initialize an array from 0-(width size)*factor array representing coordinates

        #newpoints=numpy.around(arrangedArray/self.factor)#match each point in the second img with a point in the first img
        newXpoints=self.roundForInterpolation(arrangedXArray/self.factor)#match each point in the second img with a point in the first img
        newYpoints=self.roundForInterpolation(arrangedYArray/self.factor)#match each point in the second img with a point in the first img 
        self.resizedArray=numpy.zeros((self.newXdimention,self.newYdimention))#initialize an array with zeros array of the new image
        self.resizedArray.fill(-1)#fill this array with a value out of range to make it unique

        #self.distanceBetweenNumbers=numpy.zeros((self.greyImageArray.shape[0]*self.factor,self.greyImageArray.shape[1]*self.factor))#initialize an array with zeros
        #self.distanceBetweenNumbers.fill(100000000)#fill this array with a value out of range to make it unique

        for i in range(self.newXdimention):
            for j in range(self.newYdimention):
                if (0<=newXpoints[i]<self.greyImageArray.shape[0] and 0<=newYpoints[j]<self.greyImageArray.shape[1]):
                    #print(i,j)
                    self.resizedArray[i][j]=self.greyImageArray[int(newXpoints[i])][int(newYpoints[j])]  
                else:
                    pass

        self.negativeOnesIndecies=numpy.argwhere(self.resizedArray==-1)
        self.nonNegativeIndecies=numpy.argwhere(self.resizedArray!=-1)
        self.list=[]
        #print(self.negativeOnesIndecies)

        for i in range(len(self.negativeOnesIndecies)):
            for j in range(self.newXdimention):
            #self.list.append(self.nonNegativeIndecies[numpy.searchsorted(self.nonNegativeIndecies,self.negativeOnesIndecies[i])])

                # assume the image is made of 4 quads top-left is the 1st bottom left is the second 
                # bottom-right is the third and the top-right is the fourth
                # and we move diagonaly to search for a non negative value to fill the space with it
                # i chosed to move diagonaly since it is low probability that image data will be empty in the whole diagonal
                # but it can be easily empty for a vertical or horizontal lines
                # j is only used for an incremental to move up,down,left and right of the image

                if ((self.negativeOnesIndecies[i][0]<int((self.newXdimention-1)/2)) and (self.negativeOnesIndecies[i][1]<int((self.newYdimention-1)/2))):#1st quad
                    if (self.resizedArray[int(self.negativeOnesIndecies[i][0]+j)][int(self.negativeOnesIndecies[i][1]+j)]!=-1):
                        self.resizedArray[self.negativeOnesIndecies[i][0]][self.negativeOnesIndecies[i][1]]=self.resizedArray[int(self.negativeOnesIndecies[i][0]+j)][int(self.negativeOnesIndecies[i][1]+j)]
                        break
                elif ((self.negativeOnesIndecies[i][0]>int((self.newXdimention-1)/2)) and (self.negativeOnesIndecies[i][1]<int((self.newYdimention-1)/2))):#2nd quad
                    if (self.resizedArray[int(self.negativeOnesIndecies[i][0]-j)][int(self.negativeOnesIndecies[i][1]+j)]!=-1):
                        self.resizedArray[self.negativeOnesIndecies[i][0]][self.negativeOnesIndecies[i][1]]=self.resizedArray[int(self.negativeOnesIndecies[i][0]-j)][int(self.negativeOnesIndecies[i][1]+j)]
                        break
                elif ((self.negativeOnesIndecies[i][0]>int((self.newXdimention-1)/2)) and (self.negativeOnesIndecies[i][1]>=int((self.newYdimention-1)/2))):#3rd quad
                    if (self.resizedArray[int(self.negativeOnesIndecies[i][0]-j)][int(self.negativeOnesIndecies[i][1]-j)]!=-1):
                        self.resizedArray[self.negativeOnesIndecies[i][0]][self.negativeOnesIndecies[i][1]]=self.resizedArray[int(self.negativeOnesIndecies[i][0]-j)][int(self.negativeOnesIndecies[i][1]-j)]
                        break
                elif ((self.negativeOnesIndecies[i][0]<=int((self.newXdimention-1)/2)) and (self.negativeOnesIndecies[i][1]>int((self.newYdimention-1)/2))):#4th quad
                    if (self.resizedArray[int(self.negativeOnesIndecies[i][0]+j)][int(self.negativeOnesIndecies[i][1]-j)]!=-1):
                        self.resizedArray[self.negativeOnesIndecies[i][0]][self.negativeOnesIndecies[i][1]]=self.resizedArray[int(self.negativeOnesIndecies[i][0]+j)][int(self.negativeOnesIndecies[i][1]-j)]
                        break      
        self.negativeOnesIndecies=numpy.argwhere(self.resizedArray==-1)
        #print(self.negativeOnesIndecies)

        self.greyImageArrayResized=numpy.asarray(self.resizedArray)

           ##### El Mafrood asheel kol dah lama a3rad ezay a7wel men Pil le Qpuxmap 3ala tool
        imageio.imwrite('erock_gray_resized.jpg',self.greyImageArrayResized.astype(float))
        self.ui.Nearest_ImageDisplay.setPixmap(QPixmap('erock_gray_resized.jpg'))#upload the image using Qpixmap function and set it as label background
                     

    def linear_Interpolation(self):
    	#get dimensions of original image
        originalGreyImageArray = numpy.copy(self.greyImageArray)
        originalGreyImageHeight, originalGreyImageWidth = originalGreyImageArray.shape[:2]
        #create an array of the desired shape. 
        #We will fill-in the values later.
        resizedImageHeight = int(originalGreyImageHeight * self.factor)
        resizedImageWidth = int(originalGreyImageWidth * self.factor)
        resized = numpy.zeros((int(resizedImageHeight), int(resizedImageWidth)))
        #Calculate horizontal and vertical scaling factor
        #to get the value of the new image from the old image
        reseprocalfactor=1/self.factor 
        
        for i in range(resizedImageHeight):
            for j in range(resizedImageWidth):
                #map the coordinates back to the original image
                x = i * reseprocalfactor
                y = j * reseprocalfactor
                #calculate the coordinate values for 4 surrounding pixels.
                x_floor = math.floor(x)
                x_ceil = min( originalGreyImageHeight - 1, math.ceil(x))
                y_floor = math.floor(y)
                y_ceil = min(originalGreyImageWidth - 1, math.ceil(y))

                if (x_ceil == x_floor) and (y_ceil == y_floor):
                    newpointvalue = originalGreyImageArray[int(x), int(y)]
                elif (x_ceil == x_floor):
                    star1 = originalGreyImageArray[int(x), int(y_floor)]
                    star2 = originalGreyImageArray[int(x), int(y_ceil)]
                    newpointvalue = star1 * (y_ceil - y) + star2 * (y - y_floor)
                elif (y_ceil == y_floor):
                    star1 = originalGreyImageArray[int(x_floor), int(y)]
                    star2 = originalGreyImageArray[int(x_ceil), int(y)]
                    newpointvalue = (star1 * (x_ceil - x)) + (star2	 * (x - x_floor))
                else:
                    vertix1 = originalGreyImageArray[x_floor, y_floor]
                    vertix2 = originalGreyImageArray[x_ceil, y_floor]
                    vertix3 = originalGreyImageArray[x_floor, y_ceil]
                    vertix4 = originalGreyImageArray[x_ceil, y_ceil]

                    star1 = vertix1 * (x_ceil - x) + vertix2 * (x - x_floor)
                    star2 = vertix3 * (x_ceil - x) + vertix4 * (x - x_floor)
                    newpointvalue = star1 * (y_ceil - y) + star2 * (y - y_floor)

                resized[i,j] = newpointvalue
        imageio.imwrite('erock_gray_resized_Interpolate.jpg',resized.astype(float))
        self.ui.Linear_ImageDisplay.setPixmap(QPixmap('erock_gray_resized_Interpolate.jpg'))#upload the image using Qpixmap function and set it as label background
           
    def Rotate(self,angle,array):
        rotated = numpy.zeros((array.shape[0], array.shape[1]))
        centerX,centerY=int(array.shape[0]/2),int(array.shape[1]/2)
        for i in range(array.shape[0]):
            for j in range(array.shape[1]):
                newX=(i-centerX)*numpy.cos(angle)+(j-centerY)*numpy.sin(angle)+centerX
                newY=-(i-centerX)*numpy.sin(angle)+(j-centerY)*numpy.cos(angle)+centerY

                # if nearest do this
                if (self.ui.comboBox.currentIndex()==0):
                    #just Round using the nearest interpolation rounding method and thats it the nearest interpolation is done  
                    newX=self.roundforRotation(newX)
                    newY=self.roundforRotation(newY)
                    if (newX>=0 and newY>=0 and newX<array.shape[0] and  newY<array.shape[1]):
                        rotated[i,j]=array[int(newX),int(newY)] 
                else:
                    # if linear do this

                    # here we are trying to get the pixles before and after the pixle we got which is probably is a non integer number
                    x_floor = math.floor(newX)
                    x_ceil = min(array.shape[0] - 1, math.ceil(newX))
                    y_floor = math.floor(newY)
                    y_ceil = min(array.shape[1] - 1, math.ceil(newY))

                    # first thing is to check if it is between the boundaries or not
                    if (newX>=0 and newY>=0 and newX<array.shape[0] and  newY<array.shape[1]):
                        if (x_ceil == x_floor) and (y_ceil == y_floor):
                            # if it is int number get it from the array directly
                            newpointvalue = array[int(newX), int(newY)]
                        elif (x_ceil == x_floor):
                            # if the image has the same X so it is on the same horixontal axis so get the star from the vertical axis 
                            star1 = array[int(newX), int(y_floor)]
                            star2 = array[int(newX), int(y_ceil)]
                            newpointvalue = star1 * (y_ceil - newY) + star2 * (newY - y_floor)
                        elif (y_ceil == y_floor):
                            # if the image has the same Y so it is on the same Vertical axis so get the star from the horizontal axis 
                            star1 = array[int(x_floor), int(newY)]
                            star2 = array[int(x_ceil), int(newY)]
                            newpointvalue = (star1 * (x_ceil - newX)) + (star2	 * (newX - x_floor))
                        else:
                            #get all possible verticies and get from them the stars then use the stars to get the new point
                            vertix1 = array[x_floor, y_floor]
                            vertix2 = array[x_ceil, y_floor]
                            vertix3 = array[x_floor, y_ceil]
                            vertix4 = array[x_ceil, y_ceil]

                            star1 = vertix1 * (x_ceil - newX) + vertix2 * (newX - x_floor)
                            star2 = vertix3 * (x_ceil - newX) + vertix4 * (newX - x_floor)
                            newpointvalue = star1 * (y_ceil - newY) + star2 * (newY - y_floor)
                        # assign the new point you calculated to the array
                        rotated[i,j] = newpointvalue
                    
        self.drawimage(1,rotated.astype(int))
       

    def ShearingHorizontally(self,s):
        # since the angles are even -45 or 45 so this means the seharing hosizontally factor is equal one
        shear=1

        # if the user choosed the 45 deg
        if (s==0):

            # the new dimension will be the original array dimesion* shearing factor then fill it with zeros     
            newXdimension=round(shear*self.original_T_ImageArray.shape[0]+self.original_T_ImageArray.shape[1])
            sheared = numpy.zeros((self.original_T_ImageArray.shape[0], newXdimension))
            for i in range(self.original_T_ImageArray.shape[0]):
                for j in range(self.original_T_ImageArray.shape[1]):

                    # if it is +45 this means shearing factor equal to 1 so i used the rule, but with a slight differnce that the vertical axis 
                    # in the rule was increasing upwards and here in the image vertical is increasing downwards so i made it to increase upwards
                    newX=j + shear*(127-i)
                    newX=round(newX)
                    if (0<=newX<newXdimension):
                        sheared[i][newX]=self.original_T_ImageArray[i][j]
            self.ui.NewImageDirection_label_display.setText("Right")
            self.ui.NewImageAngle_label_display.setText("45")            
        else:

            # the new dimension will be the original array dimesion* shearing factor then fill it with zeros  
            newXdimension=round(shear*self.original_T_ImageArray.shape[0]+self.original_T_ImageArray.shape[1])
            sheared = numpy.zeros((self.original_T_ImageArray.shape[0], newXdimension))
            for i in range(self.original_T_ImageArray.shape[0]):
                for j in range(self.original_T_ImageArray.shape[1]):

                    # if it is -45 this means shearing factor equal to -1 so I used the rule, but with a slight differnce that the vertical axis 
                    # in the rule was increasing upwards and here in the image vertical is increasing downwards, so that mean the space that was supposed 
                    # supposed to be left from the leftside if the image vertical axis increases upward will be the same as the rightside of the image vertical axis increadsing doenward
                    newX=j + shear*(i)
                    newX=round(newX)
                    if (0<=newX<newXdimension):
                        sheared[i][newX]=self.original_T_ImageArray[i][j]  
            self.ui.NewImageDirection_label_display.setText("Left")
            self.ui.NewImageAngle_label_display.setText("-45")                                        

        self.drawimage(1,sheared.astype(int))

    def shearAlgorithm(self,image):
        Bx = 1
        # imread rows and columns
        rows = image.shape[0]
        cols = image.shape[1]
        shear_img = numpy.zeros((rows, cols + rows, 3))
        for i in range(0, rows):
            for j in range(0, cols):
                n = Bx * i
                k = image[i, j]
                if i >= 0 and i <= rows and j >= 0 and j <= cols:
                    shear_img[i, j - n + rows] = k
        scaled_image = (numpy.maximum(shear_img, 0) / shear_img.max()) * 255.0 #Rescaling the image
        scaled_image = numpy.uint8(scaled_image)
        final_image = Image.fromarray(scaled_image) #Displaying The Image

        self.drawimage(1,final_image)

    def shearLeft(image):
        Bx = 1
        # imread rows and columns
        rows = image.shape[0]
        cols = image.shape[1]
        shear_img = numpy.zeros((rows, cols + rows, 3))
        for i in range(0, rows):
            for j in range(0, cols):
                n = Bx * i
                k = image[i, j]
                if i >= 0 and i <= rows and j >= 0 and j <= cols:
                    shear_img[i, j + n] = k
        scaled_image = (numpy.maximum(shear_img, 0) / shear_img.max()) * 255.0 #Rescaling the image
        scaled_image = numpy.uint8(scaled_image)
        final_image = Image.fromarray(scaled_image) #Displaying The Image
        return final_image
    
    
    def drawimage(self,x,array):
        if (x==1): 
            self.ui.after.canvas.axes.clear()
            self.ui.after.canvas.axes.imshow(array,cmap="gray")#int is nesceray
            self.ui.after.canvas.draw()
        else:
            self.ui.before.canvas.axes.clear()
            self.ui.before.canvas.axes.imshow(array,cmap="gray")#int is nesceray
            self.ui.before.canvas.draw()
        

    def roundforRotation(self,x):
        frac,whole=math.modf(x)
        if (frac<=0.5):
            x=whole
        else:
            x=math.ceil(x)
        return x    

    def messagebox(self,x):    
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(x)
        msg.setWindowTitle('ERROR')
        msg.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())        