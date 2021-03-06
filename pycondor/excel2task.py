#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Script to output XCSoar, Google Earth, Google Maps
from spreadsheet file (Excel xls or xlsx)
"""

from constants import supported_output_formats
from constants_windows import paths_default

import os
import glob
import click
import pandas as pd
import decimal

from task import output_task_from_df, add_distance_bearing
from task_settings import SettingsTask, add_observation_zone

@click.command()
@click.argument('xls_filename')
# use out/default.xls but also wildcard filename like out/*.xls
@click.option('--output', default='kml',
        help="Output type in %s" % supported_output_formats)
@click.option('--outdir', default='',
        help="Output directory - default is 'script_directory\out'")
# --outdir {condor_path}/
@click.option('--disp/--no-disp', default=True)
def main(xls_filename, output, outdir, disp):
    basepath = os.path.dirname(__file__)
    #basepath = os.path.dirname(os.path.abspath(__file__))
    if outdir=='':
        outdir = os.path.join(basepath, 'out')
    xls_filename = xls_filename.format(**paths_default)
    outdir = outdir.format(**paths_default)
    for filename in glob.glob(xls_filename):
        print("Read '%s'" % filename)

        filename_base, filename_ext = os.path.splitext(os.path.basename(filename))
    
        df_task = pd.read_excel(filename)
        #print(df_task)
        #print(df_task.dtypes)
        d_convert = {
            "PosX": decimal.Decimal,
            "PosY": decimal.Decimal,
            "PosZ": decimal.Decimal,
            "Airport": int,
            "SectorType": int,
            "Radius": decimal.Decimal,
            "Angle": decimal.Decimal,
            "Altitude": decimal.Decimal,
            "Width": decimal.Decimal,
            "Height": decimal.Decimal,
            "Azimuth": decimal.Decimal,
        }
        for col, typ in d_convert.items():
            df_task[col] = df_task[col].astype(typ)

        settings_task = SettingsTask()

        df_task["Comment"] = ""
        df_task["Wpt_id"] = df_task.index.map(lambda i: "_" + str(i))

        df_task = add_distance_bearing(df_task)
        df_task = add_observation_zone(settings_task, df_task)

        if disp:
            print(df_task)
            print(df_task.dtypes)
            print("")

        output_task_from_df(df_task, filename_base, output, outdir, disp)

if __name__ == '__main__':
    main()
