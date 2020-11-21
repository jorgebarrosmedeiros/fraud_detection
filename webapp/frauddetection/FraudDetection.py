import pickle
import pandas as pd
import numpy as np
import inflection

class FraudDetection( object ):
    def __init__(self):
        
        #load scalers
        self.amount_scaler = pickle.load(open("parameter/scaler_amount.pkl",'rb'))
        self.oldbalance_org_scaler = pickle.load(open("parameter/scaler_oldbalance_org.pkl",'rb'))
        self.newbalance_orig_scaler = pickle.load(open("parameter/scaler_newbalance_orig.pkl",'rb'))
        self.oldbalance_dest_scaler = pickle.load(open("parameter/scaler_oldbalance_dest.pkl",'rb'))
        self.newbalance_dest_scaler = pickle.load(open("parameter/scaler_newbalance_dest.pkl",'rb'))
        self.error_balance_orig_scaler = pickle.load(open("parameter/scaler_error_balance_orig.pkl",'rb'))
        self.error_balance_dest_scaler = pickle.load(open("parameter/scaler_error_balance_dest.pkl",'rb'))
        self.flow_orig_scaler = pickle.load(open("parameter/scaler_flow_orig.pkl",'rb'))
        self.flow_dest_scaler = pickle.load(open("parameter/scaler_flow_dest.pkl",'rb'))
        self.step_scaler = pickle.load(open("parameter/scaler_step.pkl",'rb'))
        self.day_scaler = pickle.load(open("parameter/scaler_day.pkl",'rb'))

    def data_cleaning(self, df1):
        
        ## 1.1. Rename Columns
        cols_old = ['step', 'type', 'amount', 'nameOrig', 'oldbalanceOrg', 'newbalanceOrig',
               'nameDest', 'oldbalanceDest', 'newbalanceDest','isFlaggedFraud']

        snakecase = lambda x: inflection.underscore(x)

        cols_new = list(map(snakecase,cols_old))
        cols_new

        #change columns names
        df1.columns = cols_new        
        return df1

    
    def feature_engineering(self, df2):
        
        ## 2.4. Feature Engineering

        #error balance 
        df2['error_balance_orig'] = np.round((df2['newbalance_orig'] + df2['amount'] - df2['oldbalance_org']),2)
        df2['error_balance_dest'] = df2['newbalance_dest'] + df2['amount'] - df2['oldbalance_dest']
        df2['flow_orig'] = df2['newbalance_orig'] - df2['oldbalance_org']
        df2['flow_dest'] = df2['newbalance_dest'] - df2['oldbalance_dest']

        #client
        df2['client_dest'] = df2['name_dest'].apply(lambda x: "Merchant" if "M" in x else "Costumer")
        df2['client_orig'] = df2['name_orig'].apply(lambda x: 'Merchant' if "M" in x else "Costumer")

        #step
        df2['day'] = df2['step'].apply(lambda x: int(x/24))

        #weekend
        df2['week_of_month'] = df2['day'].apply(lambda x: 1 if (x <=7) else 2 if (x <= 14) & (x>7) else 3 if (x > 14) & (x<=21) else 4)

        #weekend
        df2['weekend'] = df2['day'].apply(lambda x: 1 if (x == 7) or (x == 6) or (x == 14) or (x == 13) or (x == 20) or (x == 21) or (x == 27) or (x == 28) else 0)

        ##DATA FILTERING
        
        #removing features that will not necessary to us
        df2.drop(columns = ['name_orig','name_dest'], axis = 1, inplace = True)

        #amount
        df2 = df2[df2['amount'] < 2.108805e+06]

        #oldbalance_org
        df2 = df2[df2['oldbalance_dest'] < 9.384180e+06]
        
        return df2
    
    def data_preparation(self, df5):

        #RobustScaler
        df5['amount'] = self.amount_scaler.fit_transform(df5[['amount']])

        df5['oldbalance_org'] = self.oldbalance_org_scaler.fit_transform(df5[['oldbalance_org']])

        df5['newbalance_orig'] = self.newbalance_orig_scaler.fit_transform(df5[['newbalance_orig']])

        df5['oldbalance_dest'] = self.oldbalance_dest_scaler.fit_transform(df5[['oldbalance_dest']])

        df5['newbalance_dest'] = self.newbalance_dest_scaler.fit_transform(df5[['newbalance_dest']])

        df5['error_balance_orig'] = self.error_balance_orig_scaler.fit_transform(df5[['error_balance_orig']])

        df5['error_balance_dest'] = self.error_balance_dest_scaler.fit_transform(df5[['error_balance_dest']])

        df5['flow_orig'] = self.flow_orig_scaler.fit_transform(df5[['flow_orig']])

        df5['flow_dest'] = self.flow_dest_scaler.fit_transform(df5[['flow_dest']])


        #MinMaxScaler
        df5['step'] = self.step_scaler.fit_transform(df5[['step']])

        df5['day'] = self.day_scaler.fit_transform(df5[['day']])

        ##ENCODING
        client = {'Costumer':'0','Merchant':1}
        types = {"CASH_OUT":0,'PAYMENT':1,'CASH_IN':2, 'TRANSFER':3,'DEBIT':4}

        #encoding
        df5['client_dest'] = df5['client_dest'].map(client)
        df5['client_orig'] = df5['client_orig'].map(client)
        df5['type'] = df5['type'].map(types)

        ##features that will be really important to our model
        cols_selected = ['type','amount','oldbalance_org','newbalance_orig','oldbalance_dest','newbalance_dest','error_balance_orig','error_balance_dest','flow_orig','flow_dest','day']

        #creating a dataframe with selected columns
        df5 = df5[cols_selected]
        
        return df5
    
    def get_prediction( self, model, original_data, test_data ):
        # prediction
        pred = model.predict( test_data )
        
        # join pred into the original data
        original_data['prediction'] = pred
        
        return original_data.to_json( orient='records')
