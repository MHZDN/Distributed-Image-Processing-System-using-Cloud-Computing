import pyopencl as cl
import numpy as np
import cv2


def To_gray_pyopencl(img):


  if img.shape[-1] == 3:  # Check if it has 3 channels
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

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
  ctx=cl.create_some_context()
  queue=cl.CommandQueue(ctx)



  B_buff=cl.Buffer(ctx,cl.mem_flags.READ_ONLY,size=B_flat.nbytes)
  G_buff=cl.Buffer(ctx,cl.mem_flags.READ_ONLY,size=G_flat.nbytes)
  R_buff=cl.Buffer(ctx,cl.mem_flags.READ_ONLY,size=R_flat.nbytes)
  Grey_buff=cl.Buffer(ctx,cl.mem_flags.WRITE_ONLY,size=empty_matrix.nbytes)



  cl.enqueue_copy(queue , B_buff ,B_flat)
  cl.enqueue_copy(queue , G_buff ,G_flat)
  cl.enqueue_copy(queue , R_buff ,R_flat)

  prg=cl.Program(ctx,grey_kernel).build()
  prg.grayscale(queue,empty_matrix.shape,(1,),B_buff,G_buff,R_buff,Grey_buff)

  cl.enqueue_copy(queue , empty_matrix ,Grey_buff)


  Grey_img = empty_matrix.reshape(original_height,original_width)
  Grey_img = Grey_img.astype(np.uint8)

  # we could extend this to save the image rat5her than returned 

  return Grey_img


img = cv2.imread("Bird.jpg").astype(np.float32)
Grey_img = To_gray_pyopencl(img)
cv2.imshow("img",Grey_img)
cv2.waitKey(0)