import pyopencl as cl
import numpy as np
import cv2

class CL_Image_Preprocessing:

    def __init__(self) -> None:
        self.ctx = cl.create_some_context()
        self.queue = cl.CommandQueue(self.ctx)

    def To_gray_pyopencl(self,img):

        gray = (img.shape == 2)
        
        if gray:

            return img

        img = img.astype(np.float32)

        original_height, original_width, channels = img.shape

        B,G,R=cv2.split(img)

        B_flat = B.reshape(-1)
        G_flat = G.reshape(-1)
        R_flat = R.reshape(-1)

        empty_matrix = np.empty((original_height* original_width), dtype=np.float32)

        

        grey_kernel="""__kernel void grayscale(__global float* B, __global float* G, __global float* R, __global float* Grey) {
            int i = get_global_id(0);
            Grey[i]= 0.2125f * R[i] + 0.7154f * G[i] + 0.0721f * B[i];
        

        }
        """


        

        B_buff=cl.Buffer(self.ctx,cl.mem_flags.READ_ONLY,size=B_flat.nbytes)
        G_buff=cl.Buffer(self.ctx,cl.mem_flags.READ_ONLY,size=G_flat.nbytes)
        R_buff=cl.Buffer(self.ctx,cl.mem_flags.READ_ONLY,size=R_flat.nbytes)
        Grey_buff=cl.Buffer(self.ctx,cl.mem_flags.WRITE_ONLY,size=empty_matrix.nbytes)



        cl.enqueue_copy(self.queue , B_buff ,B_flat)
        cl.enqueue_copy(self.queue , G_buff ,G_flat)
        cl.enqueue_copy(self.queue , R_buff ,R_flat)

        prg=cl.Program(self.ctx,grey_kernel).build()
        prg.grayscale(self.queue,empty_matrix.shape,(1,),B_buff,G_buff,R_buff,Grey_buff)

        
        cl.enqueue_copy(self.queue , empty_matrix ,Grey_buff)



        Grey_img = empty_matrix.reshape(original_height,original_width)
        Grey_img = Grey_img.astype(np.uint8)

        # we could extend this to save the image rat5her than returned 

        return Grey_img
    
    def Intensity_pyopencl(self ,img , value):

        img = img.astype(np.float32)
        

        gray = (len(img.shape) == 2)

        if gray :

            original_height, original_width = img.shape

            v_flat = img.reshape(-1)

        else:

            original_height, original_width , channels = img.shape

            HSV = cv2.cvtColor(img , cv2.COLOR_BGR2HSV)

            h, s, v =cv2.split(HSV)

            v_flat = v.reshape(-1)
        
    

        bright_kernel="""__kernel void bright(__global float* V) {
        int i = get_global_id(0);
        if (V[i]+60.0f<=255.0f)
        {V[i]=V[i]+60.0f;}
        else
        {V[i]=255.0f;}       
    }
    """
        
        Dark_kernel="""__kernel void Dark(__global float* V) {
        int i = get_global_id(0);
        if (V[i]-60.0f>=0.0f)
        {V[i]=V[i]-60.0f;}
        else
        {V[i]=0.0f;}       
    }
    """
    
        V_buff=cl.Buffer(self.ctx,cl.mem_flags.READ_WRITE,size=v_flat.nbytes)

        cl.enqueue_copy(self.queue , V_buff ,v_flat)

        if value==0:
            prg=cl.Program(self.ctx,Dark_kernel).build()
            prg.Dark(self.queue,v_flat.shape,(1,),V_buff)
        else:
            prg=cl.Program(self.ctx,bright_kernel).build()
            prg.bright(self.queue,v_flat.shape,(1,),V_buff)

        cl.enqueue_copy(self.queue , v_flat ,V_buff)
        

        if gray:

            bright_image = v_flat.reshape((original_height,original_width))

        else:
            v = v_flat.reshape((original_height,original_width))

            bright_image = cv2.merge((h , s, v))

            bright_image = cv2.cvtColor(bright_image , cv2.COLOR_HSV2BGR)


        bright_image = bright_image.astype(np.uint8)

        return bright_image