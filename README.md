# SeeGULL
Seeing Geography Using Local Line-of-sight viewshed algorithm written in Python for the Street View Sentinel application.

The algorithm works by sweeping rays centred at a given coordinate across a DEM until a maximum distance and returning which terrain cells can be seen given the observer's height above the ground.

Inputs:
A location referenced via EPSG:4326
A GeoTIFF file

Output:
A heatmap corresponding to regions of visibility from a given location.

How to run:
1) Clone the repo
'''bash
git clone <https://github.com/MaxwellML/SeeGULL.git>
cd SeeGULL

2) Place DEM GeoTIFF in the same folder as SeeGULL.

3) Run:
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

4) Run:
pip install -r requirements.txt

5) Enter when prompted into the window:
Latitude (EPSG:4326)
Longitude (EPSG:4326)
Observer height (metres)

6) Click submit to run the LoS calculation.


