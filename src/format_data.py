def splitLatLonDepth(df):
    """
    Takes a single combined latitude/longitude/depth position, breaks into
    three columns, and gets rid of the old column.
    """

    df = df.join(df["coordinates"].str.split(expand=True)).rename(
        columns={0: "latitude", 1:"longitude", 2:"depth"}
    )
    df.drop("coordinates", axis=1, inplace=True)

    return df


def dms2dd(field) -> float:
    """
    Converts postition from Degrees, Minutes, Seconds (DMS) to decimal degrees.
    """

    degrees, minutes, seconds, direction = re.split("[°'\"]+", field)
    dd = float(degrees) + float(minutes) / 60 + float(seconds) / (60 * 60)
    if direction in ("S", "W"):
        dd *= -1

    return dd


def conv_to_dd(df):
    """
    Sends latitude and longitude columns to dms2dd function for conversion to
    decimal degrees.
    """

    df["latitude"] = df["latitude"].apply(dms2dd)
    df["longitude"] = df["longitude"].apply(dms2dd)

    return df
