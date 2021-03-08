#these scripts use some of the functions from the genmod notebooks, but in a newer version of gdal

def make_grid(NCOL, NROW, gt, proj, nodata=-9999.0):
    import numpy as np
    import gdal
    mem_drv = gdal.GetDriverByName('MEM')

    grid_ras = mem_drv.Create('', NCOL, NROW, 1, gdal.GDT_Float32)
    grid_ras.SetGeoTransform(gt)
    grid_ras.SetProjection(shapeproj)
    band = grid_ras.GetRasterBand(1)
    band.SetNoDataValue(nodata)
    array = np.zeros((NROW,NCOL))
    band.WriteArray(array)
    return grid_ras
	
def process_raster_data(src, outFile, conversion=1.0):
    import os
    import gdal
    import numpy as np
    
    print(gdal.VersionInfo())
    gdal.UseExceptions()
    '''
    Takes a raster data source (ESRI grid, GeoTiff, .IMG and many other formats)
    and returns a numpy array. Arrangment of pixels is given as input and may 
    correspond to a MODFLOW grid.
    
    src : string
        complete path to raster data source
    method : string
        gdal method for interpolation. Choices are:
            gdal.GRA_NearestNeighbour 
                Nearest neighbour (select on one input pixel)
            gdal.GRA_Bilinear
                Bilinear (2x2 kernel)
            gdal.GRA_Cubic
                Cubic Convolution Approximation (4x4 kernel)
            gdal.GRA_CubicSpline
                Cubic B-Spline Approximation (4x4 kernel)
            gdal.GRA_Lanczos
                Lanczos windowed sinc interpolation (6x6 kernel)
            gdal.GRA_Average
                Average (computes the average of all non-NODATA contributing pixels)
            gdal.GRA_Mode
                Mode (selects the value which appears most often of all the sampled points)
            gdal.GRA_Max
                Max (selects maximum of all non-NODATA contributing pixels)
            gdal.GRA_Min
                Min (selects minimum of all non-NODATA contributing pixels)
            gdal.GRA_Med
                Med (selects median of all non-NODATA contributing pixels)
            gdal.GRA_Q1
                Q1 (selects first quartile of all non-NODATA contributing pixels)
            gdal.GRA_Q3
                Q3 (selects third quartile of all non-NODATA contributing pixels)

    conversion : float
        factor to be applied to raw data values to change units

    requires global variables (for now):
    NCOL, NROW : number of rows and columns
    gt : geotransform list
    shapeproj : coordinate reference system of NHDPlus (or other desired projection)
    hnoflo : to be used as missing data value (from model_spec.py)

    returns:
    2D array of raster data source projected onto model grid. 
    Returns a zero array with the correct shape if the source does not exist.
    '''
    if os.path.exists(src):
        rast = gdal.Open(src)

        dest = make_grid(NCOL, NROW, gt, shapeproj)

        gdal.ReprojectImage(rast, dest, rast.GetProjection(), shapeproj, gdal.GRA_Min)

        grid = dest.GetRasterBand(1).ReadAsArray()

        grid = grid * conversion

        dest = None
        rast = None
    else:
        grid = np.ones((NROW, NCOL)) * hnoflo
        print('Data not processed for\n{}\n Check that the file exists and path is correct'.format(src))
    
    print(outFile)

    np.savetxt(outFile,grid)
    return grid
        
    
#######################
## If the script is called from the command line
if __name__ == "__main__":
    import sys

    gt = [float(x) for x in sys.argv[4][1:-1].split(",")]
    shapeproj = sys.argv[5]
    NCOL = int(sys.argv[6])
    NROW = int(sys.argv[7])
    hnoflo = float(sys.argv[3])    
    process_raster_data(sys.argv[1],sys.argv[2])
