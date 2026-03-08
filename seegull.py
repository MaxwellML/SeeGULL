from pathlib import Path
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from pyproj import Transformer
import numpy as np
from matplotlib.colors import ListedColormap
from raycasting import cast_rays_360
from lineofsight import cells_crossed, line_of_sight
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

tif_path = Path(__file__).resolve().parent / "GeoTIFF" / "SZ49se_FZ_DSM_1m.tif" # current DEM map is located in Isle of Wight, can be accessed via: https://environment.data.gov.uk/survey


def run_program(lon, lat, observer_height):
    with rasterio.open(tif_path) as src:

        t = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True) #construct CRS transformer.
        E, N = t.transform(lon, lat) #convert from ESPG to CRS.
        if not (src.bounds.left <= E <= src.bounds.right and src.bounds.bottom <= N <= src.bounds.top):
            raise ValueError("These coordinates are outside the loaded GeoTIFF area.") #if user enters coordinates that are out of range, raise an error.

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
                
        ax.set_xlabel("Easting (m)") # axis labels
        ax.set_ylabel("Northing (m)")

      
        ax.set_title("Line-of-sight visibility") # axis title.

        legend_handles = [
            mpatches.Patch(color="limegreen", alpha=0.35, label="Visible"),
            mpatches.Patch(color="lightgrey", alpha=0.35, label="Invisible"),
            Line2D([0], [0], marker='x', linestyle='None', markersize=10,
                markeredgewidth=2, label="Observer")
        ] # axis legend.

        ax.legend(handles=legend_handles, loc="upper left", bbox_to_anchor=(1.02, 1)) # move legend off grid to avoid overlapping.
        fig_dem, ax_dem = plt.subplots()
        ax_dem.set_xlim(left, right)
        ax_dem.set_ylim(bottom, top)
        show(src, ax=ax_dem)  #show unadulterated DEM map for reference.

        plt.show()


