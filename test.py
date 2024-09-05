import tkinter as tk
from PIL import ImageTk, Image

# Create the main application window
root = tk.Tk()
root.title("Narc Recon")

# Define a function to open the main app
def open_app():
    # Logic to open the Narc Recon app window
    main_app_window = tk.Toplevel(root)
    main_app_window.title("Narc Recon - Main App")
    tk.Label(main_app_window, text="Welcome to Narc Recon").pack()

# Load the logo image and make it clickable
logo_image = Image.open("logo_nr.png")  # Replace with the path to your logo
logo_image = logo_image.resize((200, 200))  # Resize logo as needed
logo_photo = ImageTk.PhotoImage(logo_image)

# Create a button with the logo that opens the app on click
logo_button = tk.Button(root, image=logo_photo, command=open_app)
logo_button.pack()

# Start the application
root.mainloop()