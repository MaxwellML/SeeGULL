# SeeGULL
Seeing Geography Using Local Line-of-sight viewshed algorithm written in Python for the Street View Sentinel application.

The algorithm works by sweeping rays centred at a given coordinate across a DEM and returning which regions
can be seen given the observer's altitude.

Inputs:
A location referenced via EPSG:4326
A GeoTIFF file

Output:
A heatmap corresponding to regions of visibility from a given location.
