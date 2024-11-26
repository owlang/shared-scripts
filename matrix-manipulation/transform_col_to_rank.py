import argparse
import pandas as pd

def getParams():
    '''Parse parameters from the command line'''
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('-i','--input', metavar='tsv_file', required=True, help='tab-delimited file of column values to be replaced with rank')
    parser.add_argument('-o','--output', metavar='tsv_file', required=True, help='tab-delimited transformed matrix')

    args = parser.parse_args()
    return(args)

def replace_with_rank(df):
    """
    Replace each column in a pandas DataFrame with its rank-sorted values.

    Parameters:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with rank-sorted values for each column.
    """
    # Apply rank() to each column
    ranked_df = df.rank(method="average")
    return ranked_df

if __name__ == "__main__":

    args = getParams()

    # Load data
    df = pd.read_csv(args.input, sep="\t", header=0, index_col=0)

    print("Original DataFrame:")
    print(df)

    # Replace columns with rank-sorted values
    ranked_df = replace_with_rank(df)
    print("\nDataFrame with Rank-Sorted Values:")
    print(ranked_df)

    # Write data
    ranked_df.to_csv(args.output, sep="\t")
