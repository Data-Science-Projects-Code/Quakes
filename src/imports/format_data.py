
def splitLatLonDepth(df):
    """
    Takes a single combined latitude/longitude/depth position, breaks into
    three columns, and gets rid of the old column.
    """
    df['longitude'] = df.coordinates.str[0]
    df['latitude'] = df.coordinates.str[1]
    df['depth'] = df.coordinates.str[2]
    df.drop("coordinates", axis=1, inplace=True)

    return df
