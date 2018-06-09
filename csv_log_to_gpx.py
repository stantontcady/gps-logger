
from gpxpy.gpx import GPX, GPXTrack, GPXTrackSegment, GPXTrackPoint
from pandas import read_csv, to_datetime

basename = '2018-06-07'

df = read_csv('{0}.csv'.format(basename))
df['timestamp']= to_datetime(df.time)

gpx_obj = GPX()

gpx_track = GPXTrack()
gpx_obj.tracks.append(gpx_track)

gpx_segment = GPXTrackSegment()
gpx_track.segments.append(gpx_segment)

gpx_segment.points.extend(
    (
        GPXTrackPoint(
            time=row.timestamp,
            latitude=row.latitude,
            longitude=row.longitude
        ) for row in df.itertuples()
    )
)

with open('{0}.gpx'.format(basename), 'w') as gpx_file:
    gpx_file.write(gpx_obj.to_xml())
