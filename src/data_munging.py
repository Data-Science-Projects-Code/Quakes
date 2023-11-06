def remove_prefixes(df):
    return df.rename(columns=lambda x: x
             .replace("properties.", "")
             .replace("geometry.", ""))


def drop_useless_cols(df):
    columns_to_drop = [
        "id", "type", "updated", "tz", "mmi", "detail", "felt", "cdi",
        "felt", "types", "nst", "type", "title"]
    return df.drop(columns=columns_to_drop)
