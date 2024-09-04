from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from PIL import Image
import io
from rembg import remove

app = FastAPI()

@app.post("/remove-background/")
async def remove_background(file: UploadFile = File(...)):
    # Read the image file
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert('RGB')

    # Remove background
    output = remove(image)

    # Save the output to a byte stream
    buf = io.BytesIO()
    output.save(buf, format="PNG")
    buf.seek(0)

    # Return the processed image
    return StreamingResponse(buf, media_type="image/png")

@app.get("/")
async def root():
    return {"message": "Welcome to the Background Removal API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) # choose the port where you can launch the app, here i chose 8000

# You can test this API using curl or Postman (for example), or simply go to the url on your localhost then access docs by FastAPI (eg. http://0.0.0.0:8000/docs)