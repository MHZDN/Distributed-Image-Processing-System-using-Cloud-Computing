from CL_For_Image import CL_Image_Preprocessing



#operations=["Gray","Brighten","Darken","Threshold"]

class guiAPI:
    def __init__(self):
        self.CL = CL_Image_Preprocessing()
        
    def gray(self,img):
        return self.CL.To_gray_pyopencl(img)
    def threshold(self,img):
        return self.CL.Threshhold(img)
    def bright(self,img):
        return self.CL.Intensity_pyopencl(img,1)
    def dark(self,img):
        return self.CL.Intensity_pyopencl(img,0)
    
    def processImage(self,inputImage,op):
        if op=="Gray":
            return self.gray(inputImage)
        elif op=="Brighten":
            return self.bright(inputImage)
        elif op=="Darken":
            return self.dark(inputImage)
        elif op=="Threshold":
            return self.threshold(inputImage)
            