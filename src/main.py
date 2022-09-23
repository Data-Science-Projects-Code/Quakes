import os
import pandas as pd
from quake_data import get_quake_data, remove_prefixes, remove_others 


if __name__ == "__main__":
    quake_data = get_quake_data()
    df = remove_prefixes(quake_data)
    print(df)
    #print(cleaned_data)

