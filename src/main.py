import os
import pandas as pd
from quake_data import get_quake_data


if __name__ == "__main__":
    df = get_quake_data()
    print(df)
