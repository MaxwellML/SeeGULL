from pathlib import Path
import rasterio
from pyproj import Transformer
from rasterio.windows import from_bounds
from rasterio.plot import show
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

tif_path = Path(__file__).resolve().parent / "SZ49se_FZ_DSM_1m.tif"

lon = float(input("Enter Longitude (e.g. -1.3276): "))
lat = float(input("Enter Latitude  (e.g. 50.730251): "))

with rasterio.open(tif_path) as src:
    t = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
    E, N = t.transform(lon, lat)

    L1 = 1000
    h1 = L1 / 2
    left1, right1 = E - h1, E + h1
    bot1, top1     = N - h1, N + h1

    win = from_bounds(left1, bot1, right1, top1, transform=src.transform)
    arr = src.read(1, window=win)
    win_transform = src.window_transform(win)

    fig, ax = plt.subplots()
    show(arr, transform=win_transform, ax=ax)

    ax.add_patch(Rectangle((left1, bot1), L1, L1, facecolor="none", linewidth=2))

    L2 = 100
    h2 = L2 / 2
    left2, bot2 = E - h2, N - h2
    ax.add_patch(Rectangle((left2, bot2), L2, L2, fill=True, alpha=0.3, linewidth=2))

    ax.set_xlim(left1, right1)
    ax.set_ylim(bot1, top1)

    plt.show()