def doProcess(INPATH):
    import pandas as pd
    import numpy as np
    import seaborn as sns
    import warnings
    warnings.filterwarnings("ignore")
    
    from sklearn.model_selection import train_test_split
    from sklearn.model_selection import GridSearchCV
    from sklearn.ensemble import RandomForestRegressor

    # INPATH = r"C:\Users\emuimds\Pictures\EasyAI\all\\"
    print("started...///")
    trans_dict = {
            u'А': u'A',
            u'Б': u'B',
            u'В': u'V',
            u'Г': u'G',
            u'Д': u'D',
            u'Е': u'E',
            u'Ё': u'E',
            u'Ж': u'Zh',
            u'З': u'Z',
            u'И': u'I',
            u'Й': u'Y',
            u'К': u'K',
            u'Л': u'L',
            u'М': u'M',
            u'Н': u'N',
            u'О': u'O',
            u'П': u'P',
            u'Р': u'R',
            u'С': u'S',
            u'Т': u'T',
            u'У': u'U',
            u'Ф': u'F',
            u'Х': u'H',
            u'Ц': u'Ts',
            u'Ч': u'Ch',
            u'Ш': u'Sh',
            u'Щ': u'Sch',
            u'Ъ': u'',
            u'Ы': u'Y',
            u'Ь': u'',
            u'Э': u'E',
            u'Ю': u'Yu',
            u'Я': u'Ya',
            u'а': u'a',
            u'б': u'b',
            u'в': u'v',
            u'г': u'g',
            u'д': u'd',
            u'е': u'e',
            u'ё': u'e',
            u'ж': u'zh',
            u'з': u'z',
            u'и': u'i',
            u'й': u'y',
            u'к': u'k',
            u'л': u'l',
            u'м': u'm',
            u'н': u'n',
            u'о': u'o',
            u'п': u'p',
            u'р': u'r',
            u'с': u's',
            u'т': u't',
            u'у': u'u',
            u'ф': u'f',
            u'х': u'h',
            u'ц': u'ts',
            u'ч': u'ch',
            u'ш': u'sh',
            u'щ': u'sch',
            u'ъ': u'',
            u'ы': u'y',
            u'ь': u'',
            u'э': u'e',
            u'ю': u'yu',
            u'я': u'ya'
        }
    trans_table ="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz".maketrans(trans_dict)
    
    
    df_sales = pd.read_csv(INPATH+"\\inputs\\sales_train.csv")
    df_sales['date'] = pd.to_datetime(df_sales.date,format="%d.%m.%Y")
    df_item_categories = pd.read_csv(INPATH+"\\inputs\\item_categories.csv")
    df_items = pd.read_csv(INPATH+"\\inputs\\items.csv")
    df_shops = pd.read_csv(INPATH+"\\inputs\\shops.csv")
    
    train_final = df_sales.merge(df_items, on = 'item_id', how = 'left').merge(df_item_categories, on = 'item_category_id', how = 'left').merge(df_shops, on = 'shop_id', how = 'left')
    
    
    train_final["shop_name"] = train_final["shop_name"].str.translate(trans_table)
    train_final["item_name"] = train_final["item_name"].str.translate(trans_table)
    train_final["item_category_name"] = train_final["item_category_name"].str.translate(trans_table)
    
    
    train_final["shop_name"] = train_final["shop_name"].str.replace('[^a-zA-Z()-]', '')
    train_final["item_name"] = train_final["item_name"].str.replace('[^a-zA-Z()-]', '')
    train_final["item_category_name"] = train_final["item_category_name"].str.replace('[^a-zA-Z()-]', '')
    
    train_final.to_csv(INPATH+"working data set.csv")
    
    ''' for flask '''
    
    df_items = df_items.merge(df_item_categories, on = 'item_category_id', how = 'left')
    df_items = df_items.drop(['item_category_id'],axis=1)
    
    df_shops["shop_name"] = df_shops["shop_name"].str.translate(trans_table)
    df_items["item_name"] = df_items["item_name"].str.translate(trans_table)
    df_items["item_category_name"] = df_items["item_category_name"].str.translate(trans_table)
    
    
    df_shops["shop_name"] = df_shops["shop_name"].str.replace('[^a-zA-Z()-]', '')
    df_items["item_name"] = df_items["item_name"].str.replace('[^a-zA-Z()-]', '')
    df_items["item_category_name"] = df_items["item_category_name"].str.replace('[^a-zA-Z()-]', '')
    
    with pd.ExcelWriter(INPATH +'\\reference.xlsx') as writer:
        
        df_items.to_excel(writer, sheet_name="items",index=False)
        df_shops.to_excel(writer, sheet_name="shops",index=False)
    
    writer.save()
    
    
    '''  done '''
    print('Total Rows Before Removing Duplicate : ', train_final.shape[0])
    print('Total Duplicate Rows : ',train_final.duplicated().sum())
    train_final = train_final[~train_final.duplicated()]
    print('Total Rows After Removing Duplicate : ',train_final.shape[0])
    
    # train_final.to_csv(INPATH+"INPUT.csv",index=False)
    
    train_final['year'] = pd.DatetimeIndex(train_final['date']).year
    train_final['month'] = pd.DatetimeIndex(train_final['date']).month
    train_final.head()
    
    print('before train shape:', train_final.shape)
    train_final = train_final[(train_final.item_price > 0) & (train_final.item_price < 300000)]
    print('after train shape:', train_final.shape)
    
    for a in range(0,101,10) :
        print(f'{a}th percentile value for item_price is {np.percentile(train_final["item_price"],a)}')
        
    for a in range(90,100,1) :
        print(f'{a}th percentile value for item_price is {np.percentile(train_final["item_price"],a)}')
        
    final = train_final[(train_final['item_price'] > 0)&(train_final['item_price']<train_final['item_price'].quantile(0.90))]
    final.shape
    
    monthly_item_cnt = final.groupby(['year','month','shop_id','item_id'])['item_price'].sum().reset_index()
    monthly_item_cnt.head()
    
    sns.heatmap(monthly_item_cnt.corr(), annot=True)
    
    
    ''' GridsearchCV Random Forest '''
    
    reg_rf = RandomForestRegressor()
    
    x,y = monthly_item_cnt[['year','month','shop_id','item_id']], monthly_item_cnt['item_price']
    
    xtrain, xtest, ytrain, ytest = train_test_split(x,y,test_size=0.25,random_state=42)
    
    rf_random = GridSearchCV(estimator=reg_rf,param_grid={'max_depth': [25],'n_estimators': [20]}, scoring='r2',n_jobs=-1)
    print("executed")
    
    rf_random.fit(xtrain,ytrain)
    rf_random.best_params_
        
    import pickle
    file = open(INPATH+'price_predict.pkl', 'wb')
    
    pickle.dump(rf_random, file)

if __name__ == '__main__':
    import os
    INPATH=os.getcwd()
    doProcess(INPATH)
