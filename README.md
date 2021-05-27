# Planet-Box-Extractor

## Description

Python tool to extract a bounding box of a given radius around a center location (longitude, latitude) using the [Planet Tiles API](https://developers.planet.com/docs/basemaps/tile-services/).

The bounding box is projected onto longitude and latitude using the [World Geodetic System 1984 WGS84](https://earth-info.nga.mil/index.php?dir=wgs84&action=wgs84).
The Planet Tiles API is indexed using [Spherical Mercator Projection](http://earth-info.nga.mil/GandG/wgs84/web_mercator/%28U%29%20NGA_SIG_0011_1.0.0_WEBMERC.pdf).

Images are prepared and processed as follows:

1. Prepare URLs by filling templates from Planet Tiles API with the corresponding tiles. A bounding box may lie on 1, 2, or 4 tiles.

2. The image data is downloaded from the URLs.

3. If the bounding box lies on more than one tile, these tiles are stitched together to form one image.

4. Calculate the bounds of the bounding box within the stitched image.

5. Crop the bounding box from the stitched image.


## Requiriments

- PIL

- urllib

- mercantile

- numpy


## Setup:

```
git clone https://github.com/V-AI-S/planet-box-extractor.git
cd planet-box-extractor
pip install --upgrade build
pip build .
pip install .
```

## Example Usage:

```
from planet_box_extractor import PlanetBoxExtractor

radius = 0.2
zoom = 15
map_id = '' # can be found in the Planet Explorer
API_KEY = '' # can be found in the user account

extractor = PlanetBoxExtractor(radius, zoom, map_id, API_KEY)
image = extractor.Process(latitude, longitude)
```

## Licesne

[MIT Licesne](LICENSE.md)
