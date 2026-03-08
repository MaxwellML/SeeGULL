from seegull import run_program
import tkinter as tk
from tkinter import messagebox

def start_gui(run_program): #entry point for the program.
    class ToolTip: #for each helper button
        def __init__(self, widget, text):
            self.widget = widget #widget the popup belongs to.
            self.text = text #text that should appear in popup.
            self.tip = None #start with no text showing.
            
            self.widget.bind("<Enter>", self.show_tip) #show text when mouse enters widget.
            self.widget.bind("<Leave>", self.hide_tip) #hide text when mouse leaves widget.
    
        def show_tip(self, event=None):
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + 20

            self.tip = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x}+{y}")

            label = tk.Label(
                tw,
                text=self.text,
                justify="left",
                background="#ffffe0",
                relief="solid",
                borderwidth=1,
                padx=6,
                pady=4
            )
            label.pack()

        def hide_tip(self, event=None):
            self.tip.destroy() #remove window.
            self.tip = None #...and the reference to it.


    def submit():
        try:
            lon = float(lon_entry.get()) #obtain longitude user has typed in.
            lat = float(lat_entry.get()) #obtain latitude user has typed in.
            observer_height = float(height_entry.get()) #obtain observer height user has typed in.
            run_program(lon, lat, observer_height) #run the main program with the three values.
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter valid numbers.") #handle invalid number input.
        except Exception as e:
            messagebox.showerror("Error", str(e)) #handle generic bad user input.


    root = tk.Tk() #create the GUI window.
    root.title("SeeGULL") #title the window.
    root.geometry("430x200") #default window size.
    root.resizable(True, True) #allow user to resize window.

    tk.Label(root, text="Longitude (EPSG:4326):").grid(row=0, column=0, padx=(12, 4), pady=(15, 8), sticky="w") #add text for longitude input box, push it to the left and add padding.
    lon_entry = tk.Entry(root, width=22) #create the input box.
    lon_entry.grid(row=0, column=1, pady=(15, 8), sticky="w") #place input box into grid.
    lon_help = tk.Label(root, text="?", fg="blue", cursor="question_arrow") #create the helper widget and make the foreground blue.
    lon_help.grid(row=0, column=2, padx=6, pady=(15, 8), sticky="w") #place helper widget into grid.

    tk.Label(root, text="Latitude (EPSG:4326):").grid(row=1, column=0, padx=(12, 4), pady=8, sticky="w") #add text for latitude input box, push it to the left and add padding.
    lat_entry = tk.Entry(root, width=22) #create the input box.
    lat_entry.grid(row=1, column=1, pady=8, sticky="w") #place input box into grid.
    lat_help = tk.Label(root, text="?", fg="blue", cursor="question_arrow") #create the helper widget and make the foreground blue.
    lat_help.grid(row=1, column=2, padx=6, pady=8, sticky="w") #place helper widget into grid.

    tk.Label(root, text="Observer height (m):").grid(row=2, column=0, padx=(12, 4), pady=8, sticky="w") #add text for observer height input box, push it to the left and add padding.
    height_entry = tk.Entry(root, width=22) #create the input box.
    height_entry.grid(row=2, column=1, pady=8, sticky="w") #place helper widget into grid.
    height_help = tk.Label(root, text="?", fg="blue", cursor="question_arrow") #create the helper widget and make the foreground blue.
    height_help.grid(row=2, column=2, padx=6, pady=8, sticky="w") #place helper widget into grid.

    submit_button = tk.Button(root, text="Submit", command=submit) #create a button that when clicked runs the submit function.
    submit_button.grid(row=3, column=0, columnspan=3, pady=(18, 10)) #place button into grid.

    #attach a tooltip to the longitude help widget.
    ToolTip(
        lon_help,
        "Enter the coordinate's longitude in EPSG:4326.\nExample: -1.3276"
    )

    #attach a tooltip to the latitude help widget.
    ToolTip(
        lat_help,
        "Enter the coordinate's latitude in EPSG:4326.\nExample: 50.730251"
    )

    #attach a tooltip to the observer height help widget.
    ToolTip(
        height_help,
        "Enter observer height above the ground in metres.\nExample: 1.5"
    )

    #start Tkinter event loop so it "listens" for user input.
    root.mainloop()
