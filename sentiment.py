import warnings
warnings.simplefilter('ignore')
import os
import unidecode, json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.metrics import accuracy_score

from xgboost import XGBClassifier
from DBHelper import CassandraDB

from flask import Flask, request, jsonify


class Main:

    def __init__(self):

        # Initialize the model
        # dataset_path, separator = ["data/dataset.txt", "   "]    
        # Load and Train model
        # self.dataset = pandas.read_csv(dataset_path, names=['sentence', 'label'], sep=separator)
        self.dataset = CassandraDB()
        self.vectorizer = None
        self.score = None
        self.model = None
        self.train()

    def train(self):
        # Separate dataset and expected output // SELECT avis FROM dataset
        sentences = self.dataset.fetch_avis()
        # // SELECT note FROM dataset
        y = self.dataset.fetch_notes()

        # Split datasets // Overfitting
        sentences_train, sentences_test, y_train, y_test = train_test_split(sentences, y, test_size=0.25, random_state=1000)

        # Verctorization of training and testing data
        self.vectorizer = CountVectorizer()
        self.vectorizer.fit(sentences_train)
        X_train = self.vectorizer.transform(sentences_train)
        X_test  = self.vectorizer.transform(sentences_test)

        # Init model and fit it
        self.model = XGBClassifier(max_depth=2, n_estimators=30)
        self.model.fit(X_train, y_train)

    def predict(self, json_text):
        # predictions
        result = self.vectorizer.transform([unidecode.unidecode(json_text)])
        result = self.model.predict(result)

        if str(result[0]) == "0":
            sentiment = "NEGATIVE"

        elif str(result[0]) == "1":
            sentiment = "POSITIVE"

        return sentiment


model = Main()
# --------- FLASK SERVER

app = Flask(__name__)

@app.route("/")
def index():
   return "Sentiment analysis API"

@app.route('/predict', methods=['GET']) # .../predict?query="abcdefg"
def predict():
    text = request.args.get("query")
    sentiment = model.predict(text)
    return jsonify({'sentiment': sentiment})


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080) # -- avec le port 8080 tous les hebergeurs peruvent exc le code sans modif ext
