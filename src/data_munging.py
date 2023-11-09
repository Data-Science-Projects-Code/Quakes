import re
import pandas as pd


def remove_prefixes(df):
    return df.rename(columns=lambda x: x
             .replace("properties.", "")
             .replace("geometry.", ""))


def drop_useless_cols(df):
    columns_to_drop = [
        "id", "type", "updated", "tz", "mmi", "detail", "felt", "cdi",
        "felt", "types", "nst", "type", "title"]
    return df.drop(columns=columns_to_drop)


def strip_commas(col1, col2):
    def process_column(col):
        # Remove leading and trailing commas
        col = col.str.lstrip(',')
        col = col.str.rstrip(',')
        col = col.apply(lambda x: re.sub(r'(\w),(\w)', r'\1, \2', x))
        return col

    col1 = process_column(col1)
    col2 = process_column(col2)

    return col1, col2


def convert_to_datetime(df):
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df['time'] = pd.to_datetime(df['time']).dt.strftime("%Y-%m-%d %H:%M")
    return df 
