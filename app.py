from flask import Flask, render_template, request
import pickle
import pandas as pd
import os
import glob
cwd = os.getcwd()

app = Flask(__name__)
model = pickle.load(open(cwd+"\\price_predict.pkl","rb"))
df_item_n_cat_id = pd.read_excel(cwd +'\\reference.xlsx', sheet_name='items')
df_shop_id = pd.read_excel(cwd +'\\reference.xlsx', sheet_name='shops')

dict_item_id = df_item_n_cat_id.set_index('item_id').T.to_dict('list')
dict_shop_id = df_shop_id.set_index('shop_id').T.to_dict('list')

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/predict_file', methods=['POST','GET'])
def predict_file():
    if request.method == "GET":
        return render_template('main.html')
    else:
        file_address = request.form["file_address"]
        if(file_address==""):
            return render_template('main.html')
        os.chdir(file_address)
        extension = '.csv'
        all_filenames = [i for i in glob.glob('*{}'.format(extension))]
        df = pd.concat([pd.read_csv(f) for f in all_filenames ])
        df['date'] = pd.to_datetime(df.date)
        df['year'] = pd.DatetimeIndex(df['date']).year
        df['month'] = pd.DatetimeIndex(df['date']).month

        # df2 = df.loc[:, df.columns.intersection(['year','month','shop_id','item_id'])]
        df = df.merge(df_item_n_cat_id, on = 'item_id', how = 'left').merge(df_shop_id, on = 'shop_id', how = 'left')
        prediction = model.predict(df[['year','month','shop_id','item_id']])
        prediction=list(prediction)
        df['prediction'] = prediction
        df.to_csv(file_address+"\\output.csv",index=False)
        return render_template('main.html',TEXT = " Output generated ... ")

@app.route('/predict', methods=['POST','GET'])
def predict():
    if request.method == "POST":

        date_dep = request.form["mon_year"]
        months = int(pd.to_datetime(date_dep, format="%Y-%m-%dT%H:%M").month)
        years = int(pd.to_datetime(date_dep, format="%Y-%m-%dT%H:%M").year)

        
        Product_ID = int(request.form["Product"])
        if (Product_ID not in dict_item_id):
            return render_template('main.html',
                                   PRINT_TEXT = "PRODUCT / ITEM ID  not found try again !!! :- ",
                                   ITEM = "ITEM NAME   ->  {}".format("ITEM ID NOT FOUND"),
                                   ITEM_CATEGORY = "ITEM CATEGORY  ->  {}" .format("ITEM CATEGORY NOT FOUND"),
                                   SHOP = "SHOP NAME  ->  {}".format("N/A"),
                                   prediction_text="YOUR PRODUCT PRICE WILL BE  ->  $. {}".format("ERROR"))



        Shop_ID = int(request.form["Shop"])
        if (Shop_ID not in dict_shop_id):
            return render_template('main.html',
                                   PRINT_TEXT = "SHOP ID  not found try again !!! :- ",
                                   ITEM = "ITEM NAME   ->  {}".format(dict_item_id[Product_ID][0]),
                                   ITEM_CATEGORY = "ITEM CATEGORY  ->  {}" .format(dict_item_id[Product_ID][1]),
                                   SHOP = "SHOP NAME  ->  {}".format("SHOP NAME NOT FOUND"),
                                   prediction_text="YOUR PRODUCT PRICE WILL BE  ->  $. {}".format("ERROR"))



        prediction=model.predict([[years,months,Shop_ID,Product_ID]])

        output = round(prediction[0],3)

        return render_template('main.html',
                               PRINT_TEXT = "Your deatils are below :- ",
                               ITEM = "ITEM NAME   ->  {}".format(dict_item_id[Product_ID][0]),
                               ITEM_CATEGORY = "ITEM CATEGORY  ->  {}" .format(dict_item_id[Product_ID][1]),
                               SHOP = "SHOP NAME  ->  {}".format(dict_shop_id[Shop_ID][0]),
                               prediction_text="YOUR PRODUCT PRICE WILL BE  ->  $. {}".format(output))
    else:
        return render_template('main.html')

if __name__ == "__main__":
    app.run(debug=True)       

'''
http://127.0.0.1:5000/
'''


