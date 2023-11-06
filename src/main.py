from data_munging remove_prefixes, drop_useless_cols
from transfer_data import check_for_data, get_quake_data, save_data

if __name__ == "__main__":
    if check_for_data():
        print("Recent data exists. Using that.")
    else:
        quake_data = get_quake_data()
        print("Fetching data")

        df = remove_prefixes(quake_data)
        print("Initial formatting done")

        df = drop_useless_cols(df)
        print("Data cleaned. This is what we'll be working with")
        print(df)

        save_data(df)
