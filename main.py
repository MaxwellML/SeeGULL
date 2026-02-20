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

from raycasting import cast_rays_360

tif_path = Path(__file__).resolve().parent / "SZ49se_FZ_DSM_1m.tif"

lon = float(input("Enter Longitude (e.g. -1.3276): "))
lat = float(input("Enter Latitude  (e.g. 50.730251): "))

with rasterio.open(tif_path) as src:

    t = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
    E, N = t.transform(lon, lat)

    fig, ax = plt.subplots()
    show(src, ax=ax)

    L_square = 100
    h_square = L_square / 2
    ax.add_patch(
        Rectangle(
            (E - h_square, N - h_square),
            L_square, L_square,
            fill=True,
            linewidth=2,
            zorder=10
        )
    )

    L_region = 1000
    h_region = L_region / 2

    left, right = E - h_region, E + h_region
    bottom, top = N - h_region, N + h_region

    ax.add_patch(Rectangle((left, bottom), L_region, L_region, fill=False, linewidth=2, zorder=10))

    hits = cast_rays_360(E, N, square_size_m=L_region, n_rays=360)

    cmap = plt.get_cmap("hsv")
    n_rays = len(hits)

    for k, (Eh, Nh) in enumerate(hits):
        color = cmap(k / n_rays)
        ax.plot([E, Eh], [N, Nh], color=color, linewidth=1, alpha=0.8, zorder=9)


    ax.set_xlim(left, right)
    ax.set_ylim(bottom, top)
    plt.show()