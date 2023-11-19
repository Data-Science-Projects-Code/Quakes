from imports.transfer_data import check_for_data, get_quake_data, save_data
from imports.mung_data import remove_prefixes, drop_useless_cols, strip_commas, convert_to_datetime
from imports.format_data import splitLatLonDepth, fix_tsunami

if __name__ == "__main__":
    if check_for_data():
        print("Recent data exists. Using that.")
    else:
        quake_data = get_quake_data()
        print("Fetching data")

        df = remove_prefixes(quake_data)
        df = drop_useless_cols(df)
        df = fix_tsunami(df)
        df['ids'], df['sources'] = strip_commas(df['ids'], df['sources'])
        df = convert_to_datetime(df)
        df = splitLatLonDepth(df)
        print(df)
        print("Data cleaned. This is what we'll be working with")
        print(df)

        save_data(df)
