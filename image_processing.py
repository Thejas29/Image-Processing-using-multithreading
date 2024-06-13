import tkinter as tk
from tkinter import filedialog
import cv2
import threading
from PIL import Image, ImageTk

# Global variables for image, number of threads, and metadata
input_image = None
output_image = None
num_threads = 4
image_metadata = {}

# Global variable to track metadata visibility
metadata_visible = True

# Load an image and display its metadata and image in the GUI
def load_image():
    global input_image, image_metadata
    try:
        file_path = filedialog.askopenfilename()
        if file_path:
            input_image = cv2.imread(file_path)
            if input_image is not None:
                # Get image metadata
                image_metadata = get_image_metadata(file_path)
                display_image(input_image)
                display_metadata(image_metadata)
            else:
                raise Exception("Invalid image file or format.")
        error_label.config(text="")
    except Exception as e:
        error_label.config(text="Error: " + str(e))

# Function to get image metadata
def get_image_metadata(file_path):
    image = Image.open(file_path)
    metadata = {
        "File Path": file_path,
        "Image Size": image.size,
        "Image Format": image.format,
         
    }
    return metadata

# Function to display image on the GUI
def display_image(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    photo = ImageTk.PhotoImage(image=Image.fromarray(image))
    canvas.create_image(0, 0, anchor=tk.NW, image=photo)
    canvas.image = photo


# Function to display metadata on the GUI
def display_metadata(metadata):
    metadata_text = "\n".join([f"{key}: {value}" for key, value in metadata.items()])
    metadata_label.config(text=metadata_text)

# Function to apply image processing operations using multiple threads
def process_image():
    if input_image is not None:
        try:
            global output_image
            output_image = input_image.copy()

            def process_image_range(start_row, end_row):
                for i in range(start_row, end_row):
                    for j in range(output_image.shape[1]):
                        pixel = output_image[i][j]
                        gray_value = sum(pixel) / 3
                        output_image[i][j] = [gray_value, gray_value, gray_value]

            rows, _, _ = output_image.shape
            step = rows // num_threads
            threads = []

            for i in range(0, rows, step):
                thread = threading.Thread(target=process_image_range, args=(i, i + step))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            display_image(output_image)
        except Exception as e:
            error_label.config(text="Error: " + str(e))

# Function to save the processed image
def save_image():
    if output_image is not None:
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".jpg")
            if file_path:
                cv2.imwrite(file_path, output_image)
                error_label.config(text="Image saved successfully.")
        except Exception as e:
            error_label.config(text="Error: " + str(e))

# Function to toggle metadata visibility
def toggle_metadata():
    global metadata_visible
    metadata_visible = not metadata_visible
    if metadata_visible:
        metadata_label.pack(pady=10)
    else:
        metadata_label.pack_forget()

# Create the GUI window
window = tk.Tk()
window.title("Enhanced Image Processing with Metadata")
window.geometry("800x600")

# Create and configure the canvas for displaying images
canvas = tk.Canvas(window, width=400, height=400)
canvas.pack()

# Create labels for displaying metadata and errors
metadata_label = tk.Label(window, text="", justify="left")
metadata_label.pack(pady=10)

error_label = tk.Label(window, text="", fg="red")
error_label.pack()

# Create buttons for image loading, processing, and saving
load_button = tk.Button(window, text="Load Image", command=load_image)
process_button = tk.Button(window, text="Process Image", command=process_image)
save_button = tk.Button(window, text="Save Image", command=save_image)

# Add a new button for toggling metadata visibility
toggle_metadata_button = tk.Button(window, text="Toggle Metadata", command=toggle_metadata)

load_button.pack()
process_button.pack()
save_button.pack()
toggle_metadata_button.pack()

# Run the Tkinter event loop
window.mainloop()