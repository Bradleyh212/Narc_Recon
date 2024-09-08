""" Using this page to keep my function to make working on the ui easier on main page
def search(search):
    search_narcs()
main_page_window.bind('<Return>', search)

def search_narcs(): #function to find the meds in meds.py
    search_input = meds_ent.get()
    if len(search_input) == 12:
        tup = find_narcs_upc(search_input)
    elif len(search_input) == 8:
        tup = find_narcs_din(search_input)
    else:
        messagebox.showerror("Error", "Drug not found")
        remove_qty_ent.focus_set() #This brings the focus out of the med entry
        meds_ent.focus_set() # This brings back the focus to med entry
        return

    if len(tup) == 1:
#There will always be only 1 tuple in the list when looking with upc, will but another constraint, "if len(din) > 1" when lookin with din
        name_lbl_output.config(text = tup[0][1])
        din__med_output.config(text = tup[0][0])
        strength_lbl_output.config(text = tup[0][4])
        drug_form_output.config(text = tup[0][5])
        pack_med_output.config(text = tup[0][6])
        qty_med_output.config(text = find_quantity(tup[0][3])) #functions from the meds file to find the qty directly from the database
    elif len(tup) > 1:
        #I will output a choice for which pack size they want
        choice_windw = tk.Toplevel(main_page_window)
        choice_windw.title("Choose Pack Size")
        #Creating the place and the size of the window
        w = 400 
        h = 100

        window_width = choice_windw.winfo_screenwidth()  # screen centering code from https://stackoverflow.com/questions/14910858/how-to-specify-where-a-tkinter-window-opens
        window_height = choice_windw.winfo_screenheight()

        x = (window_width/2) - (w/2)
        y = (window_height/2) - (h/0.1)
        choice_windw.geometry('%dx%d+%d+%d' % (w, h, x, y))

        choice_windw.wm_attributes("-topmost", True) #Will keep the choice_windw on top
        tk.Label(choice_windw, text="Choose the pack size:").pack()

        pack_size = tk.StringVar()
        pack_size_dropdown = ttk.Combobox(choice_windw, textvariable=pack_size)
        pack_size_dropdown['values'] = [f"{item[6]} units - {item[4]} {item[5]}" for item in tup]
        pack_size_dropdown.pack()

        def on_select_pack_size():
            global selected_pack
            selected_index = pack_size_dropdown.current()
            selected_pack = tup[selected_index]
            name_lbl_output.config(text=selected_pack[1])
            din__med_output.config(text=selected_pack[0])
            strength_lbl_output.config(text=selected_pack[4])
            drug_form_output.config(text=selected_pack[5])
            pack_med_output.config(text=selected_pack[6])
            qty_med_output.config(text=find_quantity(selected_pack[3]))
            print(selected_pack)
            choice_windw.destroy()

        select_btn = tk.Button(choice_windw, text="Select", command=on_select_pack_size)
        select_btn.pack()
    else:
        messagebox.showerror("Error", "Drug not found")
        remove_qty_ent.focus_set() #This brings the focus out of the med entry
        meds_ent.focus_set() # This brings back the focus to med entry
"""