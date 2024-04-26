from CL_For_Image import CL_Image_Preprocessing
import cv2

img = cv2.imread("Bird.jpg")

CL = CL_Image_Preprocessing()

gray = CL.To_gray_pyopencl(img)

bright =CL.Intensity_pyopencl(gray,1)

cv2.imshow("gray",gray)
cv2.imshow("bright",bright)

cv2.waitKey(0)
cv2.destroyAllWindows()

