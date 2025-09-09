import cv2
import numpy as np
import os
import tempfile
from moviepy.editor import VideoFileClip

class SimpleVRProcessor:
    def __init__(self):
        pass
    
    def convert_to_vr180(self, input_path, progress_callback=None):
        """
        🔥 MAIN CONVERSION FUNCTION
        Converts 2D video to VR 180 stereoscopic format WITH AUDIO
        """
        
        # Create output path
        output_dir = tempfile.mkdtemp()
        output_path = os.path.join(output_dir, 'vr180_output.mp4')
        temp_video_path = os.path.join(output_dir, 'temp_video.mp4')
        
        try:
            # Step 1: Load video
            if progress_callback:
                progress_callback(10, "Loading video...", 0)
            
            cap = cv2.VideoCapture(input_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # VR 180 dimensions (side-by-side stereoscopic)
            vr_width = width * 2  # Double width for left+right eye
            vr_height = height
            
            # Video writer for output - NO AUDIO YET
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_video_path, fourcc, fps, (vr_width, vr_height))
            
            frame_count = 0
            
            # Process each frame
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Step 2: Estimate depth for this frame
                if progress_callback and frame_count % 30 == 0:
                    progress_callback(20 + (frame_count / total_frames) * 60, 
                                    "Analyzing depth...", 1)
                
                depth_map = self.simple_depth_estimation(frame)
                
                # Step 3: Create left and right eye views
                if progress_callback and frame_count % 30 == 0:
                    progress_callback(20 + (frame_count / total_frames) * 60, 
                                    "Creating stereo view...", 2)
                
                left_eye, right_eye = self.create_stereo_pair(frame, depth_map)
                
                # Step 4: Combine side-by-side for VR 180
                vr_frame = np.hstack([left_eye, right_eye])
                out.write(vr_frame)
                
                frame_count += 1
            
            cap.release()
            out.release()
            
            # Step 5: ADD AUDIO FROM ORIGINAL VIDEO
            if progress_callback:
                progress_callback(95, "Adding audio...", 3)
            
            # Use MoviePy to combine the processed video with original audio
            original_clip = VideoFileClip(input_path)
            processed_clip = VideoFileClip(temp_video_path)
            
            # Set the audio from original to processed video
            if original_clip.audio is not None:
                final_clip = processed_clip.set_audio(original_clip.audio)
                
                # Write final video with audio
                final_clip.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile='temp-audio.m4a',
                    remove_temp=True,
                    verbose=False,
                    logger=None
                )
                
                final_clip.close()
            else:
                # No audio in original, just move the temp file
                os.rename(temp_video_path, output_path)
            
            # Cleanup
            original_clip.close()
            processed_clip.close()
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
            
            if progress_callback:
                progress_callback(100, "Conversion complete!", 4)
            
            return output_path
            
        except Exception as e:
            # Cleanup on error
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
            raise Exception(f"Conversion failed: {str(e)}")
    
    def simple_depth_estimation(self, frame):
        """🧠 DEPTH ESTIMATION ENGINE"""
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur for smoothing
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Calculate gradients (edges usually = closer objects)
        grad_x = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
        
        # Gradient magnitude
        gradient_mag = np.sqrt(grad_x**2 + grad_y**2)
        
        # Brightness factor (brighter usually = closer)
        brightness_factor = gray.astype(np.float64) / 255.0
        
        # Combine gradient and brightness for depth
        depth = (gradient_mag * 0.7 + brightness_factor * 0.3)
        
        # Normalize and smooth
        depth = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX)
        depth = cv2.GaussianBlur(depth, (7, 7), 0)
        
        return depth.astype(np.uint8)
    
    def create_stereo_pair(self, frame, depth_map):
        """👁️ STEREOSCOPIC PAIR GENERATOR"""
        
        height, width = frame.shape[:2]
        
        # Normalize depth (0-1 range)
        depth_norm = depth_map.astype(np.float32) / 255.0
        
        # Create disparity map (how much to shift each pixel)
        max_disparity = 15  # Maximum pixel shift for depth effect
        disparity = depth_norm * max_disparity
        
        # Generate left and right eye views
        left_eye = self.shift_image(frame, disparity, direction=1)   # Shift right for left eye
        right_eye = self.shift_image(frame, disparity, direction=-1) # Shift left for right eye
        
        return left_eye, right_eye
    
    def shift_image(self, image, disparity, direction):
        """🔄 IMAGE DISPLACEMENT ENGINE"""
        
        height, width = image.shape[:2]
        
        # Create coordinate grids
        y_coords, x_coords = np.mgrid[0:height, 0:width]
        
        # Apply horizontal shift based on depth
        x_shifted = x_coords + (disparity * direction * 0.3)  # Subtle shift for natural effect
        x_shifted = np.clip(x_shifted, 0, width - 1)  # Keep within bounds
        
        # Remap the image with new coordinates
        shifted = cv2.remap(
            image,
            x_shifted.astype(np.float32),
            y_coords.astype(np.float32),
            cv2.INTER_LINEAR
        )
        
        return shifted
