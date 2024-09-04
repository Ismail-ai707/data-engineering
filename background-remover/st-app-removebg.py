# # Using YOLOv8
# import streamlit as st
# from ultralytics import YOLO
# import numpy as np
# from PIL import Image
# import io

# # Load YOLOv8 model
# @st.cache_resource
# def load_model():
#     model = YOLO('yolov8n-seg.pt')  # Load the smallest segmentation model
#     return model
# # Remove background
# def remove_background(image, model):
#     # Perform inference
#     results = model(image)
    
#     # Get the mask of detected objects
#     masks = results[0].masks
#     if masks is None:
#         st.warning("No objects detected in the image.")
#         return image
    
#     composite_mask = np.zeros((image.height, image.width), dtype=np.uint8)
#     for mask in masks:
#         mask_array = mask.data[0].numpy()
#         mask_image = Image.fromarray(mask_array).resize((image.width, image.height))
#         composite_mask = np.logical_or(composite_mask, np.array(mask_image))
    
#     # Create a new image with transparent background
#     result = Image.new("RGBA", image.size, (0, 0, 0, 0))
#     image_rgba = image.convert("RGBA")
#     composite_mask_image = Image.fromarray((composite_mask * 255).astype(np.uint8))
#     result.paste(image_rgba, (0, 0), composite_mask_image)
    
#     return result

# # Streamlit app
# st.title("Automatic Background Removal App (YOLOv8)")

# model = load_model()

# uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# if uploaded_file is not None:
#     image = Image.open(uploaded_file).convert('RGB')
#     st.image(image, caption="Original Image", use_column_width=True)
    
#     if st.button("Remove Background"):
#         result = remove_background(image, model)
#         st.image(result, caption="Image with Background Removed", use_column_width=True)
        
#         # Provide download button for the processed image
#         buf = io.BytesIO()
#         result.save(buf, format="PNG")
#         byte_im = buf.getvalue()
#         st.download_button(
#             label="Download Processed Image",
#             data=byte_im,
#             file_name="processed_image.png",
#             mime="image/png"
#         )

import streamlit as st
from PIL import Image
import io
from rembg import remove

@st.cache_data
def remove_background(image):
    return remove(image)

# Streamlit app
st.title("Background Removal App")

# List of accepted image file extensions
ACCEPTED_EXTENSIONS = ["png", "jpg", "jpeg", "webp", "bmp", "tiff", "gif"]

uploaded_file = st.file_uploader("Choose an image...", type=ACCEPTED_EXTENSIONS)

if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file).convert('RGB')
        st.image(image, caption="Original Image", use_column_width=True)
        
        if st.button("Remove Background"):
            with st.spinner('Removing background... This may take a while.'):
                # Remove background
                output = remove_background(image)
            
            st.image(output, caption="Image with Background Removed", use_column_width=True)
            
            # Provide download button for the processed image
            buf = io.BytesIO()
            output.save(buf, format="PNG")
            byte_im = buf.getvalue()
            st.download_button(
                label="Download Processed Image",
                data=byte_im,
                file_name="processed_image.png",
                mime="image/png"
            )
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")