#TODO: Generalize this code to be used for any workflow

from icecream import ic
import os
import requests
from urllib.parse import urlencode
from collections import OrderedDict

from db.models import Connector
from models.jobs import Job

from pybrapi import BrAPI
from pybrapi.authentication import BasicAuth
import pandas as pd

def transform_data(data: Job, connector: Connector):
    germplasm = next((brapi_data_parameter for brapi_data_parameter in data.brapiDataParameters if brapi_data_parameter.parameterId == 'germplasm'), None)
    if germplasm:
        listDbId = next((parameter.brapiParameterValue for parameter in germplasm.brapiParameters if parameter.brapiParameterName == 'listDbId'), None)
        germplasm_response = requests.get(
            url=f'{germplasm.brapiBaseURL}/{listDbId}',
            headers={
                'Authorization': germplasm.authToken
            }
        )
        germplasm_response.raise_for_status()
        germplasm_data = germplasm_response.json()['result']
        
        germplasm_list = germplasm_data['data'].split(',')
        
        df_germplasm = pd.DataFrame(columns=['germplasmDbId'])
        for germplasmDbId in germplasm_list:
            df_germplasm.loc[len(df_germplasm)] = [germplasmDbId]
        
        os.makedirs(data.jobDbId, exist_ok=True)
        
        df_germplasm['germplasmDbId'] = df_germplasm['germplasmDbId'].str.replace(' ', '_')
        
        observations = next((brapi_data_parameter for brapi_data_parameter in data.brapiDataParameters if brapi_data_parameter.parameterId == 'observations'), None)
        if observations:
            server = BrAPI(observations.brapiBaseURL+'/brapi/v2')
            parameters = {
                "observationVariableDbId": next((parameter.brapiParameterValue for parameter in observations.brapiParameters if parameter.brapiParameterName == 'observationVariableDbId'), None),
                "germplasmDbId": germplasm_data['data']
            }
            resp = server.get_observations(observationVariableDbId=parameters['observationVariableDbId'], germplasmDbId=parameters['germplasmDbId'])
            df = pd.DataFrame(columns=['germplasmDbId',parameters['observationVariableDbId']])
            for observation in resp:
                df.loc[len(df)] = [observation.germplasmDbId, observation.value]
            ic(df)
            grouped = df.groupby('germplasmDbId')
            result = pd.DataFrame(columns=['germplasmDbId', f'{parameters["observationVariableDbId"]}1', f'{parameters["observationVariableDbId"]}2'])
            for germplasmDbId, group in grouped:
                if len(group)==2:
                    result.loc[len(result)] = [germplasmDbId, group.iloc[0][parameters['observationVariableDbId']], group.iloc[1][parameters['observationVariableDbId']]]
                elif len(group)==1:
                    result.loc[len(result)] = [germplasmDbId, group.iloc[0][parameters['observationVariableDbId']], None]
            
            result['germplasmDbId'] = result['germplasmDbId'].str.replace(' ', '_')
            ic(result)
            
            df_observation = df_germplasm.merge(result, on='germplasmDbId', how='left')
            df_observation.rename(columns={'germplasmDbId': 'SAMPLE'}, inplace=True)
            
            available_germplasm = []
            with open(f'{data.jobDbId}/observations.tsv', 'w') as f:
                f.write(f'SAMPLE\t{parameters["observationVariableDbId"]}1\t{parameters["observationVariableDbId"]}2\n')
                for index, row in df_observation.iterrows():
                    if row["SAMPLE"] != "":
                        if not (pd.isna(row[parameters["observationVariableDbId"]+"1"]) and pd.isna(row[parameters["observationVariableDbId"]+"2"])):
                            f.write(f'{row["SAMPLE"]}\t{row[parameters["observationVariableDbId"]+"1"]}\t{row[parameters["observationVariableDbId"]+"2"]}')
                            available_germplasm.append(row["SAMPLE"])
                            ic(row["SAMPLE"])
                            if index != len(df_observation)-1:
                                f.write('\n')
                                
            with open(f'{data.jobDbId}/germplasm.tsv', 'w') as f:
                for line in available_germplasm:
                    f.write(line.replace(' ','_'))
                    if line != available_germplasm[-1]:
                        f.write('\n')