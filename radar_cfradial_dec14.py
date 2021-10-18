import cartopy 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import glob
import pyart
import os
import warnings

#Ignore deprecated warnings
warnings.filterwarnings("ignore")


all_reports = {'lat':[ -32.201393],
               'lon':[-64.541380],
               'cities': ["Villa del Dique"],
               'date': ['Dec 13 18'],
               'time': ["02:20"]}
report = pd.DataFrame (all_reports, columns = ['lat','lon','cities','date','time'])


def add_cities(ax, report):

    df = report
    X, Y = df['lon'], df['lat']
    
    plt.scatter(X, Y, s=100, marker='*', transform=cartopy.crs.PlateCarree(),label=None, c='black', 
    linewidth=1, alpha=1)          
    

def cfrad(fname, report, save_path, swp):

    nc = Dataset(fname, 'r')

    import datetime

    time_var = nc.time_coverage_start
    iyear = time_var[0:4]
    imonth = time_var[5:7]

    import calendar

    cmonth = calendar.month_abbr[int(imonth)]
    iday = time_var[8:10]
    itime = time_var[11:19]
    itimehr = time_var[11:13]
    itimemn = time_var[14:16]

    cdate_string = (iyear + '/' + imonth + '/' + iday)
    ctime_string = (itimehr + ':' + itimemn + 'UTC')
    ctime_file_string = iyear + imonth + iday + '_' + itimehr + itimemn
 
    radar = pyart.io.read_cfradial(fname)

    #extent = [-65, -32.4, -63.6, -31.25]
    extent = [-65, -32.7, -63.6, -31.25]

    fig = plt.figure(figsize = [10,8])
    display = pyart.graph.RadarMapDisplay(radar)
    lat_0 = display.loc[0]
    lon_0 = display.loc[1]


    #Main difference! Cartopy forces you to select a projection first!
    projection = cartopy.crs.PlateCarree()
    #projection = cartopy.crs.Mercator(
    #                central_longitude=lon_0,
    #                min_latitude=extent[1], max_latitude=extent[3])

    #display.plot_ppi_map(
    #    'VEL', sweep = swp, colorbar_flag=False, cmap='jet',
    #    title=ctime_string,
    #    projection=projection,
    #    min_lon=extent[0], max_lon=extent[2], min_lat=extent[1], max_lat=extent[3],
    #    mask_outside=False)   
                 
    #DBZH
    display.plot_ppi_map(
        'DBZH', sweep = swp, colorbar_flag=True,
        projection=projection, colorbar_label = 'dBZ',
        min_lon=extent[0], max_lon=extent[2], min_lat=extent[1], max_lat=extent[3],
        mask_outside=False)

    #Mark the radar
    display.plot_point(lon_0, lat_0, label_text='Radar')

    #Range rings
    #display.plot_range_rings([50, 100])

    #Cross hairs
    #display.plot_line_geo(np.array([lon_0, lon_0]), np.array([35.5, 38]))
    #display.plot_line_geo(np.array([-99, -96]), np.array([lat_0, lat_0]))

    #Get the current axes and plot some lat and lon lines
    ax = plt.gca()
    gl = ax.gridlines(draw_labels=True,
                    linewidth=2, color='gray', alpha=0.5, linestyle='--')
    gl.xlabels_top = False
    gl.ylabels_right = False

    add_cities(ax, report)

    time = '02:00'

    fname1 = '/Volumes/Anthony_Drive/Masters_Publication/Dec13.shp'
    shape_feature = ShapelyFeature(Reader(fname1).geometries(),
                                    projection, edgecolor='black')
    ax.add_feature(shape_feature)

    plt.title(cdate_string + '\n' + 'Rad:' + ' ' + ctime_string + ' ' + 'Sat:' + ' ' + time + 'UTC', pad=10, ma='center', size=12, weight='bold')

    #plt.savefig(save_path + ctime_file_string + '_' + str(swp) + '_' + 'shp', bbox_inches='tight', pad_inches=0)

    plt.show()


############################################################################################################


file_path = os.getcwd() + '/'  
save_path = os.getcwd() + '/'  # Directory where figures will be saved
figures = 'single'  # Number of figures to create: 'single' (one data file) or 'multiple' (multiple data files)
file_name = 'cfrad.20181214_020345.000_to_20181214_020508.922_1_SUR.nc'  # For plotting a single file
swp = 2


if __name__ == "__main__":

    if figures == 'single':
        # Open single data file and set file name
        fname = file_path + file_name
        cfrad(fname, report, save_path, swp)
        print('Done!')

    if figures == 'multiple':
        # Collect all of the .nc files in specified directory
        file_list = sorted(glob.glob(file_path + '*.nc')) 
        # Loop through data files, making/saving a figure for each data file
        for fname in file_list:
            print(fname)
            cfrad(fname, report, save_path, swp)
        print('Done!')    

