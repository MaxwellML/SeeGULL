from pathlib import Path
import tkinter as tk
from tkinter import messagebox

import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from pyproj import Transformer
import numpy as np
from matplotlib.colors import ListedColormap
from raycasting import cast_rays_360
from lineofsight import cells_crossed, line_of_sight

tif_path = Path(__file__).resolve().parent / "SZ49se_FZ_DSM_1m.tif"  # current DEM map is located in Isle of Wight, can be accessed via: https://environment.data.gov.uk/survey


def run_program(lon, lat, observer_height):
    with rasterio.open(tif_path) as src:

        t = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True) #construct CRS transformer.
        E, N = t.transform(lon, lat) #convert from ESPG to CRS.
        affine = src.transform #define world pixel conversion.
        fig, ax = plt.subplots() #create matplotlib figure and axes.
        show(src, ax=ax) #display DEM on axes.

        dem = src.read(1)

        L_region = 100
        h_region = L_region / 2

        left, right = E - h_region, E + h_region
        bottom, top = N - h_region, N + h_region
        #define region where plot will be zoomed in to.



        hits = cast_rays_360(E, N, square_size_m=L_region, n_rays=360, affine=affine) #cast rays.

        ray_results = []
        for (Eh, Nh) in hits:
            cells = cells_crossed(affine, src.width, src.height, E, N, Eh, Nh)
            if cells is None:
                continue
            vis = line_of_sight(cells, dem, affine, E, N, observer_height, nodata=src.nodata)
            ray_results.append((list(cells_crossed(affine, src.width, src.height, E, N, Eh, Nh)) , vis))

        ax.set_xlim(left, right)
        ax.set_ylim(bottom, top) #zoom in plot.

        vis_mask = np.full(dem.shape, -1, dtype=np.int8)  #create an array the same size as the DEM.

        for (cells, vis) in ray_results:  #for each ray.
            for (r, c), is_vis in zip(cells, vis): #...and its visibility.
                if is_vis:
                    vis_mask[r, c] = 1
                else:
                    if vis_mask[r, c] != 1: #if another ray hasnt marked it visible (to prevent overwriting).
                        vis_mask[r, c] = 0  #mark as visible or invisible on the map.


        overlay = np.ma.masked_where(vis_mask == -1, vis_mask) #convert into masked array.

        cmap = ListedColormap(["lightgrey", "limegreen"])  
        show(overlay, transform=affine, ax=ax, cmap=cmap, alpha=0.35, zorder=50) #display mask on axes.

        ax.plot(E, N, marker='x', linestyle='None', markersize=10, markeredgewidth=2, zorder=100) #add marker to centre.

        fig_dem, ax_dem = plt.subplots()
        ax_dem.set_xlim(left, right)
        ax_dem.set_ylim(bottom, top)
        show(src, ax=ax_dem)  #show unadulterated DEM map for reference.

        plt.show()


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

tk.Label(root, text="Latitude (EPSG:4326):").grid(row=3, column=0, padx=(12, 4), pady=8, sticky="w") #add text for latitude input box, push it to the left and add padding.
lat_entry = tk.Entry(root, width=22) #create the input box.
lat_entry.grid(row=1, column=1, pady=8, sticky="w") #place input box into grid.
lat_help = tk.Label(root, text="?", fg="blue", cursor="question_arrow") #create the helper widget and make the foreground blue.
lat_help.grid(row=1, column=2, padx=6, pady=8, sticky="w") #place helper widget into grid.

tk.Label(root, text="Observer height (m):").grid(row=5, column=0, padx=(12, 4), pady=8, sticky="w" #add text for observer height input box, push it to the left and add padding.
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
