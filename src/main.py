import os
from quake_data import get_quake_data, remove_prefixes, drop_useless_cols

if __name__ == "__main__":
    quake_data = get_quake_data()
    print("Data fetched")

    df = remove_prefixes(quake_data)
    print("Initial formatting done")

    df = drop_useless_cols(df)
    print("Data cleaned. This is what we'll be working with")
    print(df)
