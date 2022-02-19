from flask import  Flask
from flask import request
import numpy as np
import pickle
import pandas as pd
import flasgger
from flasgger import Swagger
from flasgger import Swagger, LazyString, LazyJSONEncoder, swag_from



application=Flask(__name__)        # debut de l'app


# pas tres import: habillage det affivhage
application.json_encoder = LazyJSONEncoder

swagger_template = dict(
                      info = {
                          'title': LazyString(lambda: "Modèle d'authentification de billets de banque"),
                          'description': LazyString(lambda: " Les informations statistiques extraites nous permettra de savoir si les billets sont authentiques"),
                             },
                      host = LazyString(lambda: request.host)
                      )

swagger_config = {
                      "headers": [],
                      "specs": [
                          {
                              "endpoint": '',
                              "route": '/',
                              "rule_filter": lambda rule: True,
                              "model_filter": lambda tag: True,
                          }
                      ],
                      "static_url_path": "/flasgger_static",
                      "swagger_ui": True,
                      "specs_route": "/apidocs/"
                      
                  }

swagger= Swagger(application, template=swagger_template, config=swagger_config)
# Swagger(application)

# chargement du modèle
modele=pickle.load(open("model.pkl","rb"))

@application.route('/')
def welcome():
    return "Bienvenu dans le site d'authentification"





@application.route('/predict',methods=["Get"])
def predict_note_authentication():
    
    """Let's Authenticate the Banks Note 
    This is using docstrings for specifications.
    ---
    parameters:  
      - name: variance
        in: query
        type: number
        required: true
      - name: skewness
        in: query
        type: number
        required: true
      - name: curtosis
        in: query
        type: number
        required: true
      - name: entropy
        in: query
        type: number
        required: true
    responses:
        200:
            description: The output values
        
    """
    variance = request.args.get("variance")
    skewness = request.args.get("skewness")
    curtosis = request.args.get("curtosis")
    entropy = request.args.get("entropy")
    prediction = modele.predict([[variance, skewness, curtosis, entropy]])
    print(prediction)
    return "Alors vraissemblablement la réponse est "+str(prediction)

@application.route('/predict_file',methods=["POST"])


def predict_note_file():
    """Let's Authenticate the Banks Note 
    This is using docstrings for specifications.
    ---
    parameters:
      - name: file
        in: formData
        type: file
        required: true
      
    responses:
        200:
            description: The output values
        
    """
    df_test=pd.read_csv(request.files.get("file"))
    print(df_test.head())
    prediction=modele.predict(df_test)
    
    return str(list(prediction))

if __name__=='__main__':               #  si 1 est exécuté alors l'application (codé en bas) sera mis en exécution
    application.run()
    
    