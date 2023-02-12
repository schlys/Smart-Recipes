from flask import Flask, request, render_template, jsonify
from Speech.SpeechToText import speech_to_text
import Barcode.BarcodeScanner as BS
import ElasticSearch.elastic as es
import HelperMethods.HelperMethods as HM

app = Flask(__name__)
es.initialize()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        result = speech_to_text()
        esResult = es.search(' '.join(result))
        return render_template("list.html", items=esResult)
    return render_template("webpage.html")

@app.route('/scan-barcode', methods=['POST'])
def scan_barcode():
    image_binary = request.files['image'].read()

    # pass the image binary data to the BarcodeScanner function
    barcode = BS.BarcodeScanner(image_binary)
    barcode = HM.get_keyword(barcode)
    esResult = es.search(' '.join(barcode))

    return render_template("list.html", items=esResult)

@app.route('/login')
def login():
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)