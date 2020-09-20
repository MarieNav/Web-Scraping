import json                         #import all librairies we'll need
import requests as r
import pandas as pd
import time

url='https://search.ubisoft.com/api/v2/search'          #define our 3 global variables
headers = """Cache-Control: no-cache
Connection: keep-alive
Content-Length: 205
Content-Type: application/json
Host: search.ubisoft.com
Origin: https://www.ubisoft.com
Pragma: no-cache
Referer: https://www.ubisoft.com/fr-fr/games
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-site
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"""
headers=dict(i.split(': ') for i in headers.split('\n'))
payload="""{"appId":"f35adcb5-1911-440c-b1c9-48fdc1701c68","fields":["title"],"from":0,"languages":["fr-fr"],"size":15,"sorts":[{"field":"createdAt","direction":"desc"}],"channels":["ubisoftportal"],"types":["game"]}"""

def get_df0():
    """return 15 lines of data corresponding to 15 first games"""
    resp = r.post(url, headers=headers, data=payload)       # collects datas
    result = resp.json()
    df0 = pd.DataFrame(result)           # get array with empty boxes except one which contains our dataframe
    df = pd.DataFrame(df0.iloc[4, 3])    # takes the data out of the aforementioned box
    return df

def get_df(df, payload=payload):
    """add 15 more lines of data corresponding to 15 other games"""
    dct = json.loads(payload)
    while dct['from'] < 400:        #
        dct['from'] += 15           #
        payload = str(dct)          # increases the variable used to call the next page
        resp = r.post(url, headers=headers, data=payload)   #
        result = resp.json()                                #
        df1 = pd.DataFrame(result)                          # get data from next page
        df1 = pd.DataFrame(df1.iloc[4, 3])                  #
        df = pd.concat([df, df1])           # add the new collected rows to the array
        time.sleep(0.5)                       # wait 1 sec before next request (not to be blocked by website)
    return df

def clean(df):
    """Data manipulation for a better reading of our datas"""
    df = df.reset_index(drop=True)                          # Order the index
    flattened_source = pd.DataFrame(dict(df['_source'])).T      # get data stored in dictionary form in a single column
    df = pd.concat([df, flattened_source], axis=1)              #  "
    df.drop('_source', axis=1, inplace=True)                # drop the aforementioned column
    df.drop(['platformInfoList', 'gameInfo'], axis=1,
            inplace=True)                               # Drop columns containing soup of info which doesn't interest us
    df.drop('_score', axis=1, inplace=True)             # Drop empty column
    df.drop(['_index', '_type', 'channel', 'language'], axis=1,
            inplace=True)                                   # Drop columns which contains same value in all their lines
    df.drop(['_id', 'name', 'friendlyUrl', 'mdmInstallment'], axis=1,
            inplace=True)                           # Drop twins columns (or containing almost same info between them)
    df = df.rename(columns={'mdmBrand': 'brandTeam', 'boxshotLink': 'link_picture1', 'mDMRating': 'minumumAge',
                            'metaKeyword': 'keywords', 'thumbnail': 'link_picture2', 'link': 'link-website',
                            'createdAt': 'releaseDate', 'metaDescription': 'description'})
    df = df[['title', 'id', 'releaseDate', 'sort', 'minumumAge', 'genre', 'link_picture1', 'link_picture2',
             'link-website','developers', 'brandTeam', 'keywords', 'description']]
    return df

df = get_df0().pipe(get_df).pipe(clean)
df