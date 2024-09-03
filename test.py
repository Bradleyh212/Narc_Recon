import tkinter as tk

root = tk.Tk()

# Create an Entry widget with a white background
entry = tk.Entry(root, bg="black", fg="black")
entry.pack(pady=10)

# Set focus to the Entry widget so the cursor appears
entry.focus_set()

root.mainloop()