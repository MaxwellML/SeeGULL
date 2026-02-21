#find direction vector for a given angle.
#cast ray along vector until bounding box edge hit.
#repeat incrementally across 2pi radians.

import math
from typing import Optional, Tuple, List
from rasterio.transform import rowcol



def ray_hit_square(
    E0: float,
    N0: float,
    half_size_m: float,
    theta_rad: float,
    eps: float = 1e-12,
):
    
    eps = 1e-12
    dE = math.cos(theta_rad)
    dN = math.sin(theta_rad) #create unit vector from N and E components.

    L = half_size_m * 2
    half = L / 2
    Emin, Emax = E0 - half, E0 + half
    Nmin, Nmax = N0 - half, N0 + half #define region of interest.

    candidates: List[Tuple[float, float, float]] = []  #define list for candidate intersection points. (prevents overshotting)

    if abs(dE) > eps: #if we are on course for a vertical wall.
        for E_side in (Emin, Emax): #for either side of the square.
            t = (E_side - E0) / dE #find distance needed to travel to hit wall.
            if t > 0: #a negative value indicates we'd travel backwards to reach the wall, not valid.
                N = N0 + t * dN
                if Nmin - 1e-9 <= N <= Nmax + 1e-9:
                    candidates.append((t, E_side, N)) #store potential wall hit.

    if abs(dN) > eps: #if we are on course for a horizontal wall.
        for N_side in (Nmin, Nmax): #for either side of the square.
            t = (N_side - N0) / dN  #find distance needed to travel to hit wall.
            if t > 0: #a negative value indicates we'd travel backwards to reach the wall, not valid.
                E = E0 + t * dE
                if Emin - 1e-9 <= E <= Emax + 1e-9:
                    candidates.append((t, E, N_side)) #store potential wall hit.

    if not candidates:
        return None

    t_hit, E_hit, N_hit = min(candidates, key=lambda x: x[0]) #minimum t corresponds to actual wall hit.
    
    return (E_hit, N_hit)


def cast_rays_360(
    E0: float,
    N0: float,
    square_size_m: float = 100.0,
    n_rays: int = 360,
    affine: affine=affine
):

    r, c = rowcol(affine, E0, N0) #define row and column of centre.
    half = square_size_m / 2
    hits: List[Tuple[float, float]] = []

    for k in range(n_rays):
        theta = 2 * math.pi * (k / n_rays) #convert to radians.
        hit = ray_hit_square(E0, N0, half, theta, affine) #find ray for a given angle.
        if hit is None:
            continue
        Eh, Nh = hit #find point of intersection.
        hits.append((Eh, Nh))

    return hits


def cells_crossed(
    affine: Affine,
    width: int,
    height: int,
    E0: float,
    N0: float,
    E1: float,
    N1: float,
    eps: float = 1e-12,
):

    dE = E1 - E0
    dN = N1 - N0 #define direction vector given start and end points.

    r, c = rowcol(affine, E0, N0) #define r,c of start point
    r_end, c_end = rowcol(affine, E1, N1) #define r,c of end point

    if not (0 <= r < height and 0 <= c < width):
        return #do not allow indexing outside the raster grid.

    yield (r, c) #output starting cell, then continue.
  
    resE = affine.a
    resN = -affine.e  #find the width and height of a single pixel as defined by the raster file.

    step_c = 1 if dE > 0 else (-1 if dE < 0 else 0) #find if ray points east or west.
    step_r = 1 if dN < 0 else (-1 if dN > 0 else 0) #find if ray points north or south.

    x_left, y_top = affine * (c, r)
    x_right = x_left + resE
    y_bottom = y_top - resN #find rectangle bounds of current cell as world coordinates.

    def safe_div(num: float, den: float) -> float:
        return num / den if abs(den) > eps else math.inf #avoid division by 0 if we are perfectly horizontal or vertical.

    if step_c > 0:
        tMaxX = safe_div(x_right - E0, dE)
    elif step_c < 0:
        tMaxX = safe_div(x_left - E0, dE)
    else:
        tMaxX = math.inf

    #find how far we would need to travel to hit a horizontal border.

    if step_r > 0:
        tMaxY = safe_div(y_bottom - N0, dN)
    elif step_r < 0:
        tMaxY = safe_div(y_top - N0, dN)
    else:
        tMaxY = math.inf

    #find how far we would need to travel to hit a vertical border.

    tDeltaX = abs(resE / dE) if abs(dE) > eps else math.inf #set jump size for vertical boundary lines.
    tDeltaY = abs(resN / dN) if abs(dN) > eps else math.inf #set jump size for horiztontal boundary lines.

    while (r, c) != (r_end, c_end): #until we hit the boundary line.
        if tMaxX + eps < tMaxY: #if we will hit a vertical boundary first, move into neighbouring column.
            c += step_c
            tMaxX += tDeltaX
        elif tMaxY + eps < tMaxX: #if we will hit a vertical boundary first, move into neighbouring row.
            r += step_r
            tMaxY += tDeltaY
        else: #if we will hit a corner, move into diagonally neighbouring square.
            c += step_c
            r += step_r
            tMaxX += tDeltaX
            tMaxY += tDeltaY

        yield (r, c) #output new cell we have moved into.