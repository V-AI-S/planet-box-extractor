from .geo_utils import boundingBox

import time

import PIL.Image
import urllib.request
import mercantile

import numpy as np

class PlanetBoxExtractor:
    """
    Download satellite images from Planet Tiles API
    
    @radius: distance from the center of the image to the edge in kilometers
    @zoom: level of zoom in the Mercantiles
    @map_id: url-id of the basemap from the Planet Tiles API, can be found in the Planet Explorer
    @api_key: Planet Tiles API Key 
    base_url: placeholder url of using the Planet Tiles API, containing the API_KEY

    IMGSIZE: the size of the images from the Planet Tiles API (256 default)
    locations: clockwise order of the tiles
    
    Usage:
    extractor = PlanetBoxExtractor(radius, zoom, map_id, API_KEY)
    image = extractor.Process(latitude, longitude)
    """
    def __init__(self, radius, zoom, map_id, api_key):
        self.radius = radius
        self.zoom = zoom
        self.base_url = 'https://tiles.planet.com/basemaps/v1/planet-tiles/' + map_id + '/gmap/{}/{}/{}.png?api_key=' + api_key
        self.IMGSIZE = 256
        self.locations = ['upleft', 'upright', 'downleft', 'downright']
        
    def Download(self, latitude, longitude):
        """
        Method to retrieve Mercartor tiles corresponding to the bounding box around longitude and latitude with radius self.radius
        Returns a list of 4 items, either the image of a tile or an empty object (None)
        
        Parameters
        ----------
        latitude: latitude coordinate of the center of the desired bounding box in degrees
        longitude: longitude coordinate of the center of the desired bounding box in degrees
        
        Returns
        -------
        images: list of PNG images corresponding to the Mercartor tiles
        """
        minLat, minLon, maxLat, maxLon = boundingBox(latitude, longitude, self.radius)
        tiles = [
            mercantile.tile(minLon, maxLat, self.zoom), # upleft
            mercantile.tile(maxLon, maxLat, self.zoom), # upright
            mercantile.tile(minLon, minLat, self.zoom), # downleft
            mercantile.tile(maxLon, minLat, self.zoom), # downright
        ]
        urls = []
        images = []
        for i, location in enumerate(self.locations):
            tile = tiles[i]
            url = self.base_url.format(tile.z, tile.x, tile.y)
            if url in urls:
                images.append(None)
            else:
                urls.append(urls.append(url))
                images.append(PIL.Image.open(urllib.request.urlopen(url)))
                time.sleep(0.2)
        return images
        
    def Stitch(self, images):
        """
        Method to place Mercartor tile images in correct order
        
        Parameters
        ----------
        images: list of images of tiles and empty objects (None) for empty tiles
        
        Returns
        -------
        img: stitched image with size (self.IMGSIZE * n) x (self.IMGSIZE * m) with n the number of tile rows and m the number of tile columns
        """
        total = [(img is not None) for i, img in enumerate(images)]
        if sum(total) == 1:
            padx, pady = 0, 0
            img = np.zeros((self.IMGSIZE, self.IMGSIZE, 3), 'uint8')
        elif sum(total) == 2:
            if sum(total[:2]) % 2 == 0:
                # up/down
                padx, pady = 0, self.IMGSIZE
                img = np.zeros((self.IMGSIZE, self.IMGSIZE * 2, 3), 'uint8')
            else:
                # left/right
                padx, pady = self.IMGSIZE, 0
                img = np.zeros((self.IMGSIZE * 2, self.IMGSIZE, 3), 'uint8')
        elif sum(total) == 4:
            padx, pady = self.IMGSIZE, self.IMGSIZE
            img = np.zeros((self.IMGSIZE * 2, self.IMGSIZE * 2, 3), 'uint8')
        #
        for location, image in zip(self.locations, images):
            if image is None:
                continue
            if location == 'upleft':
                img[:self.IMGSIZE, :self.IMGSIZE] = np.array(image)[:,:,:3]
            elif location == 'upright':
                img[:self.IMGSIZE, self.IMGSIZE:] = np.array(image)[:,:,:3]
            elif location == 'downright':
                img[self.IMGSIZE:, self.IMGSIZE:] = np.array(image)[:,:,:3]
            elif location == 'downleft':
                img[self.IMGSIZE:, :self.IMGSIZE] = np.array(image)[:,:,:3]    
        return img
        
    def coord2pixel(self, lon, lat, box):
        """
        Method to convert longitude and latitude to their corresponding pixel location given the bounding box of the Mercartor containing the coordinates
        Parameters
        ----------
        lon: longitude in degrees
        lat: latitude in degrees
        box: bounding box of the Mercartor tile containing the coordinates returned from mercantile.bounds()
        
        Returns
        -------
        tuple of 2 pixel locations corresponding to the given longitude and latitude
        """
        return int((lon - box.west)/(box.east - box.west)*self.IMGSIZE), int((lat - box.north)/(box.south - box.north)*self.IMGSIZE)
        
    def Bounds(self, latitude, longitude):
        """
        Method to calculate the pixel locations of the bounding box with a radius of self.radius given the center longitude and latitude coordinates
        
        Parameters
        ----------
        latitude: latitude coordinate of the center of the bounding box in degrees
        longitude: longitude coordinate of the center of the bounding box in degrees
        
        Returns
        -------
        minY: starting pixel location of the bounding box on the Y-axis
        maxY: ending pixel location of the bounding box on the Y-axis
        minX: starting pixel location of the bounding box on the X-axis
        maxX: ending pixel location of the bounding box on the X-axis
        """
        minLat, minLon, maxLat, maxLon = boundingBox(latitude, longitude, self.radius)
        minX, minY = self.coord2pixel(minLon, maxLat, mercantile.bounds(mercantile.tile(longitude, latitude, self.zoom)))
        maxX, maxY = self.coord2pixel(maxLon, minLat, mercantile.bounds(mercantile.tile(longitude, latitude, self.zoom)))
        if minY < 0:
            minY += self.IMGSIZE
            maxY += self.IMGSIZE
        if minX < 0:
            minX += self.IMGSIZE
            maxX += self.IMGSIZE
        return minY, maxY, minX, maxX
        
    def Crop(self, image, minY, maxY, minX, maxX):
        """
        Method to perform the cropping of the stitched image to return the bounding box region
        
        Parameters
        ----------
        image: stitched image of the Mercartor tiles
        minY: starting pixel location of the bounding box on the Y-axis
        maxY: ending pixel location of the bounding box on the Y-axis
        minX: starting pixel location of the bounding box on the X-axis
        maxX: ending pixel location of the bounding box on the X-axis
        
        Returns
        -------
        partial image corresponding to the bounding box region
        """
        return image[minY:maxY, minX:maxX]
        
    def Process(self, latitude, longitude):
        """
        Method that combines the main steps of the API to extract a bounding box image given a latitude and longitude
        
        Parameters
        ----------
        latitude: latitude coordinate of the center of the bounding box in degrees
        longitude: latitude coordinate of the center of the bounding box in degrees
        
        Returns
        -------
        image: partial image corresponding to the bounding box region
        """
        images = self.Download(latitude, longitude)
        stitched_image = self.Stitch(images)
        minY, maxY, minX, maxX = self.Bounds(latitude, longitude)
        image = self.Crop(stitched_image, minY, maxY, minX, maxX)
        return image
        
if __name__ == '__main__':
    latitude, longitude = 5, 20
    zoom = 15
    radius = 0.2
    API_KEY = ''
    map_id = ''
    
    extractor = PlanetBoxExtractor(radius, zoom, map_id, API_KEY)
    image = extractor.Process(latitude, longitude)
