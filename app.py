from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from Speech.SpeechToText import speech_to_text
import Barcode.BarcodeScanner as BS
import Databases.elastic as es
import Databases.user_db as db
from Databases.models import User
import HelperMethods.HelperMethods as HM
from Speech.TextToSpeech import text_to_speech
import json
import items
import AI_Rec
import Camera.CameraCapture as Camera
from functools import wraps

import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key = secrets.token_bytes(32)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



es.initialize()
db.initialize()


# Decorators
def login_required(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if 'logged_in' in session:
      return f(*args, **kwargs)
    else:
      return redirect('/')
  return wrap


@app.route('/', methods=["GET", "POST"])
def login():
    error = None

    if request.method == 'POST':
        option = int(request.form['type'])
        username = request.form['username']
        password = request.form['password']

        if option == 1:
            error, user_data = db.signup(username, password)
        else:
            error, user_data = db.login(username, password)
        
        if not error:
                User().start_session(user_data)
                return redirect(url_for('home'))
       
    return render_template('login.html', error=error)


@app.route('/signout', methods=['POST'])
@login_required
def signout():
    User().signout()
    return redirect('/')


#Home, Team, and User Feedback route
@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    return render_template("home.html", items={'username':User().username()})

@app.route("/team", methods=["GET", "POST"])
def team():
    return render_template("team.html")

@app.route("/feedback", methods=["GET", "POST"])
@login_required
def feedback():
    return render_template("feedback.html")


#Input Data Route
@app.route('/scan-barcode', methods=['GET', "POST"])
@login_required
def scan_barcode():
    image_binary = request.files['image'].read()

    # pass the image binary data to the BarcodeScanner function
    barcode = BS.BarcodeScanner(image_binary)
    barcode = HM.get_keyword(barcode)
    
    User().add_ingredient(barcode)
    db.update_doc(User().username())
    return [barcode]

    items.addItem(barcode)
    newItems = items.returnItems()
    return newItems

# Input Data Route


@app.route('/ai-rec/', methods=['GET', "POST"])
def ai_rec():
    file = request.files['image']
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    print("AI Recognizing...")
    # items.addItem(barcode)
    # newItems = items.returnItems()

    AI = AI_Rec.AI_recognition.AIRec(ViT_path='./AI_Rec/ViTmodel/ViTmodel.pth')
    img = AI.load_pil_img(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    box_list = AI.inference(img)
    img_pil = AI.draw_box_output(img, box_list)
    # AI.show_pil_img(img_pil)
    AI.save_pil_img(img_pil, os.path.join(app.config['UPLOAD_FOLDER'],"out.png"))
    return AI.box_list_to_text_list(box_list)

@app.route("/speech", methods=["GET", 'POST'])
@login_required
def speech():
    result = speech_to_text()
    for item in result:
        User().add_ingredient(item)
    
    db.update_doc(User().username())
    return result

@app.route('/text', methods=['GET', 'POST'])
@login_required
def text():
    ingredient = request.json.get('ingredients')

    User().add_ingredient(ingredient)
    db.update_doc(User().username())
    return jsonify([ingredient])

@app.route('/savePicture', methods=['GET', 'POST'])
@login_required
def savePicture():
    Camera.takePic()
    return ""

@app.route('/removeItems', methods=['POST'])
@login_required
def removeItems():
    items = request.json.get('ingredients')

    for item in items:
        User().remove_ingredient(item)

    db.update_doc(User().username())
    return User().get_ingredients()

#Return items route
@app.route('/searchItems', methods=['POST'])
@login_required
def searchItems():
    ingredients = request.json.get('ingredients')
    return redirect(url_for('recipes', items=json.dumps(ingredients)))

#Page Reader Route
@app.route('/read-page', methods=['POST'])
def read_page():
    webpage = request.json.get('webpage')
    text_to_speech(webpage)

@app.route('/recipes', methods=['GET', 'POST'])
@login_required
def recipes():
    items = json.loads(request.args['items'])
    esResult = es.search(items)
    return render_template('results.html', items=esResult)



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
