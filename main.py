#2500 samples in a 5km x 5km square.
#Step 100m.
#Sample 100m x 100m square.
#Expect under 1s computation time.
#take coordinates as centre, use EPSG:4326

from pathlib import Path
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from pyproj import Transformer
import numpy as np
from matplotlib.colors import ListedColormap
from raycasting import cast_rays_360

tif_path = Path(__file__).resolve().parent / "SZ49se_FZ_DSM_1m.tif"

lon = float(input("Enter Longitude (e.g. -1.3276): "))
lat = float(input("Enter Latitude  (e.g. 50.730251): "))

with rasterio.open(tif_path) as src:

    t = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True) #construct CRS transformer.
    E, N = t.transform(lon, lat) #convert from ESPG to CRS.
    affine = src.transform #define world pixel conversion.
    fig, ax = plt.subplots() #create matplotlib figure and axes.
    show(src, ax=ax) #display DEM on axes.

    L_region = 100
    h_region = L_region / 2

    left, right = E - h_region, E + h_region
    bottom, top = N - h_region, N + h_region
    #define region where plot will be zoomed in to.



    hits = cast_rays_360(E, N, square_size_m=L_region, n_rays=360) #cast rays.

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


    plt.show()