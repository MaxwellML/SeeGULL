#2500 samples in a 5km x 5km square.
#Step 100m.
#Sample 100m x 100m square.
#Expect under 1s computation time.
#take coordinates as centre, use EPSG:4326

from pathlib import Path
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
from pyproj import Transformer

tif_path = Path(__file__).resolve().parent / "SZ49se_FZ_DSM_1m.tif"

lon = float(input("Enter longitude (e.g. -1.3276): "))
lat = float(input("Enter latitude  (e.g. 50.730251): "))

with rasterio.open(tif_path) as src:
    t = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
    E, N = t.transform(lon, lat) 
    fig, ax = plt.subplots()
    show(src, ax=ax)  

    ax.plot(E, N, marker="x", markersize=12, linewidth=2) 
    ax.set_xlabel("Easting (m)")
    ax.set_ylabel("Northing (m)")

    ax.annotate(f"E={E:.1f}, N={N:.1f}", (E, N), xytext=(6, 6), textcoords="offset points")  

    plt.show()