import datetime
import pandas as pd
from newsapi import NewsApiClient
from pandas import json_normalize
import os

#検索キーワード指定
key_word = 'iphone'
os.makedirs(key_word,exist_ok=True)

#ニュースソースを指定
news_source = 'reuters'

#4週間分の日付リスト作成
daylist = []
for k in range(28):
    day = datetime.date.today() + datetime.timedelta(days=29+k)
    daylist.append(day)

#　newsapiクライアントを初期化
newsapi = NewsApiClient(api_key='') #自分のAPI key

#条件指定したニュースを取得
#query: 検索キーワード
#sources：news_sources(ex. 'reuters')
#dayfrom: 指定日時(from)
#dayto：指定日時(to)
#page = pg
def news_json(query, news_sources, dayfrom, dayto,pg):
    news_res = newsapi.get_everything(
        q= query,
        sources= news_sources,
        from_param= dayfrom,
        to= dayto,
        page=pg
    )
    return news_res

#jsonから必要な情報のみピックアップ
def json2def(json):
    df = json_normalize(json['articles'])
    return df

def main():
    #１リクエストにつき100件（20件×5ページ）までしかニュースを読み込めない為、1日ごとにニュースを取得する
    for day in daylist:
        #検索ヒット数などの基本情報確認
        res_temp = news_json(key_word,news_source,day,day,1)

        #検索ヒット数が存在するかつ100件以内であれば以下を実行
        if( res_temp['totalResults'] > 0 and res_temp['totalResults']<=100):

            #1ページあたり20件なので検索ヒット数から最終ページを計算する
            page_total = -(-res_temp['totalResults'] //20) #切り上げを表現

            #1ページ目の処理
            df = json2def(res_temp)
            if(page_total>1):
                #2ページ目以降を取得
                for pg in range(page_total-1):
                    res = news_json(key_word,news_source,day,day,pg+2)
                    df_pg = json2def(res)
                    df = pd.concat([df,df_pg], axis= 0)
            #１ページのみであれば2ページ目以降処理不要のためスキップ
            else:
                pass

            #csvに出力
            csvname = key_word + '/' + day.strftime('%Y-%m-%d') + '.csv'
            #pandasのjson_normalizeにcsv出力機能があるんやな
            df.to_csv(csvname)

        #検索ヒット数が100件以上だと6ページ目以降を取得できないので、そのメッセージを出力する
        elif(res_temp['totalResults']>100):
            print(day.strftime('%Y-%m-%d')+ ': over 100 news exists')

        #検索が陽ッとしないとそもそも取得できないので、そのメッセージを出力
        else:
            print(day.strftime('%Y-%m-%d') + ': No news exists')
    return

if __name__ == "__main__":
    main()

