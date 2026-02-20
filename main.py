#2500 samples in a 5km x 5km square.
#Step 100m.
#Sample 100m x 100m square.
#Expect under 1s computation time.
#take coordinates as centre, use EPSG:4326

from pathlib import Path
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt

tif_path = Path(__file__).resolve().parent / "SZ49se_FZ_DSM_1m.tif"

with rasterio.open(tif_path) as src:
    show(src) 
    plt.show()
    