from flask import Flask, render_template, request
import json
from pattern.en import wordnet
from watson_developer_cloud import VisualRecognitionV3

visual_recognition = VisualRecognitionV3('2016-05-20', api_key='c6f25fcfd00c3ad03ffa283a79eb2e5490874d02')

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('intro.html')

@app.route("/analyize", methods=['GET', 'POST'])
def img_upload():
    imageUrl = request.form['hiddenUrl']
    regc = json.dumps(visual_recognition.classify(images_url=str(imageUrl)), indent=2)
    return render_template('info.html', imgURL=str(imageUrl))

if __name__ == "__main__":
    app.run()
