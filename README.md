# Planet-Downloader

A tool to extract a bounding box of a given radius around a center location (longitude, latitude) using the [Planet Tiles API](https://developers.planet.com/docs/basemaps/tile-services/).

## Setup:

```git clone https://github.com/V-AI-S/planet-data-processing.git
cd planet-data-processing
pip install --upgrade build
pip build .
pip install .
```

## Example Usage:

```from planet_downloader import PlanetDownloader

radius = 0.2
zoom = 15
map_id = '' # can be found in the Planet Explorer
API_KEY = '' # can be found in the user account

planetapi = PlanetDownloader(radius, zoom, map_id, API_KEY)
image = planetapi.Process(latitude, longitude)
```