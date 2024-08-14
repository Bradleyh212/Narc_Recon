#main page, will be full screen, not reziable
import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import messagebox

main_page_window = tk.Tk()
main_page_window.title("Narcotics Management System")

#Window setting
main_page_window.state('zoomed') #setting window to full screen before stopping the resizable to false

main_page_window.resizable(False, False) #This stops the user from resizing the screen for the login ui


#end of main_page_window setting




# Define a font
#****login_ui_font = font.Font(family="Inter", size=36, weight="bold") ******* Change font **********





#Running the program

main_page_window.mainloop()
