import pandas as pd
import json
import requests
import re

GITHUB_REPO_URL = "https://api.github.com/repos/fivethirtyeight/russian-troll-tweets/contents/"

def main():
    #Get file list from github repo
    response = requests.get(GITHUB_REPO_URL)
    #Create master DF we'll dump the individual files into
    master_df = pd.DataFrame()

    for item in json.loads(response.text):
        #Check last 3 characters to see if it's a CSV file, skip loop if it isn't
        if item["download_url"][-3:] != "csv":
            continue

        #Concat master df with new file
        master_df = pd.concat(
            [
                master_df,
                load_df(item["download_url"])
            ]
        )
    
    #For each account category, export a dataframe for it.
    for account_category in master_df["account_category"].unique():
        export_str(
            master_df[
                master_df["account_category"] == account_category
            ]["content"].str.cat(sep='\n'),
            f"{account_category} - Combined.txt"
        )

def load_df(url):
    print(f"Loading file: {url}")
    #Returnes a processed dataframe which has been read from the csv url
    #Drops most columns to reduce amount of data.
    return process_df(pd.read_csv(
        url,
        usecols=[
            "content",
            "language",
            "account_category"
        ]
    ))

def process_df(df):
    #Filter only english results
    return df[df["language"] == "English"]

def export_str(col_str, filename):
    #UTF-8 encoding is important, for emojis/etc.
    #regex is used here to filter out ALL urls
    with open(filename, "w", encoding="utf-8") as f:
        f.write(re.sub(
            r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', 
            '', 
            col_str,
            flags=re.MULTILINE
        ))

if __name__ == "__main__":
    #Run main function
    main()