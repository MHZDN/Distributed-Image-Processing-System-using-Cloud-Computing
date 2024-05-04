import pyopencl as cl
import numpy as np
def process_grey_B(self, B, height, width, grey_kernel):
  """
  Process a single channel for grayscale conversion using OpenCL
  """
  channel_flat = B.reshape(-1)
  empty_matrix = np.empty_like(channel_flat)

  channel_buff = cl.Buffer(self.ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=channel_flat)
  result_buff = cl.Buffer(self.ctx, cl.mem_flags.WRITE_ONLY, size=empty_matrix.nbytes)

  grey_kernel = """__kernel void grayscale(__global float* channel, __global float* result) {
            int i = get_global_id(0);
            result[i] = channel[i];
        }"""

  prg = cl.Program(self.ctx, grey_kernel).build()
  prg.grayscale(self.queue, (height * width,), None, channel_buff, result_buff)

  result = np.empty_like(channel_flat)
  cl.enqueue_copy(self.queue, result, result_buff).wait()

  return result.reshape(height, width)
def apply_intensity_kernel_B(self, B, value, bright_kernel, dark_kernel):
        """
        Apply brightness/darkness adjustment to a single channel using OpenCL kernel
        """        
        channel_flat = B.reshape(-1)
        empty_matrix = np.empty_like(channel_flat)

        channel_buff = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR, hostbuf=channel_flat)
        result_buff = cl.Buffer(self.ctx, cl.mem_flags.WRITE_ONLY, size=empty_matrix.nbytes)

        if value == 1:
            prg = cl.Program(self.ctx, bright_kernel).build()
            prg.bright(self.queue, channel_flat.shape, None, channel_buff)
        else:
            prg = cl.Program(self.ctx, dark_kernel).build()
            prg.dark(self.queue, channel_flat.shape, None, channel_buff)
                

        result = np.empty_like(channel_flat)
        cl.enqueue_copy(self.queue, result, channel_buff).wait()

        return result.reshape(B.shape)
def apply_intensity_kernel_grey(self, channel, value, bright_kernel, dark_kernel):
        """
        Apply brightness/darkness adjustment to a single channel using OpenCL kernel
        """
        channel_flat = channel.reshape(-1)
        empty_matrix = np.empty_like(channel_flat)

        channel_buff = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR, hostbuf=channel_flat)
        result_buff = cl.Buffer(self.ctx, cl.mem_flags.WRITE_ONLY, size=empty_matrix.nbytes)

        if value == 1:
            prg = cl.Program(self.ctx, bright_kernel).build()
            prg.bright(self.queue, channel_flat.shape, None, channel_buff)
        else:
            prg = cl.Program(self.ctx, dark_kernel).build()
            prg.dark(self.queue, channel_flat.shape, None, channel_buff)
                

        result = np.empty_like(channel_flat)
        cl.enqueue_copy(self.queue, result, channel_buff).wait()

        return result.reshape(channel.shape)