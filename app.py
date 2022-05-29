import os

import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect
# from flask_bootstrap import Bootstrap5

from filters_handler import *
from image_handler import *

app = Flask(__name__)
app.secret_key = "secretkey"
app.config["DEBUG"] = True
# Bootstrap5(app)
image_env = {}
img_infos = {}


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


def allowed_file(filename):
    allowed_extensions = {'pgm', 'ppm', 'jpg', 'png'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        print('No file part')
        print("req:", len(request.files))
        return redirect(request.url)
    file = request.files["file"]
    if file.filename == "":
        print("No image selected for uploading")
        return redirect(request.url)
    if file and allowed_file(file.filename):
        file.save(os.path.join('static/uploads/', file.filename))
        print("Image successfully saved in uploads folder!")
        setup(file.filename)
        img_path = "static/uploads/" + file.filename
        metrics = {
            "histogramme_path": "static/output/histogramme.png",
            "histogramme_cumule_path": "static/output/histogramme_cumule.png",
            "egaliseur_path": "static/output/egaliseur.png",
            "moyenne": round(image_env["moyenne"], 3),
            "ecart": round(image_env["ecart_type"], 3)
        }
        return render_template("index.html", img_path=img_path, metrics=metrics)
    else:
        print("Image extension is not handeled")
        return redirect(request.url)


def setup(filename):
    image = read_image("static/uploads/" + filename)
    img_infos = {
        "format": image.format,
        "mode": image.mode,
        "size": image.size,
        "data": np.array2string(np.array(image.getdata())),
        "filename": filename
    }
    image_env.update({
        "image": image,
        "info": img_infos,
        "histogramme": histogramme(list(image.getdata())),
        "moyenne": moyenne(list(image.getdata())),
        "ecart_type": ecart_type(list(image.getdata()))
    })


@app.route('/histogramme')
def hist():
    histogram = histogramme(list(image_env.get("image").getdata()))
    fig = plt.figure()
    fig.set_tight_layout(False)
    ax = fig.add_axes([0, 0, 1, 1])
    langs = range(VMAX + 1)
    ax.bar(langs, histogram)
    plt.savefig("static/output/histogramme.png", bbox_inches='tight')
    plt.show()
    return 'histogramme'


@app.route('/hist_cumule')
def hist_cum():
    histogram = histogram_cumule(histogramme(list(image_env.get("image").getdata())))
    fig = plt.figure()
    fig.set_tight_layout(False)
    ax = fig.add_axes([0, 0, 1, 1])
    langs = range(VMAX + 1)
    ax.bar(langs, histogram)
    plt.savefig("static/output/histogramme_cumule.png", bbox_inches='tight')
    plt.show()
    return 'hist cum'


@app.route("/egaliser")
def egaliser():
    egal = egaliseur(histogramme(list(image_env.get("image").getdata())), image_env["image"])
    fig = plt.figure()
    fig.set_tight_layout(False)
    ax = fig.add_axes([0, 0, 1, 1])
    langs = range(VMAX + 1)
    ax.bar(langs, egal)
    plt.savefig("static/output/egaliseur.png", bbox_inches='tight')
    plt.show()
    return 'egaliseur'


@app.route('/linear')
def linear_trans():
    image = image_env["image"]
    hist = image_env["histogramme"]

    new_data = transformation_lineaire(hist, image)

    save_image(image, new_data, "lineartrans.jpg")
    return "success"


@app.route('/linear_sature/<min>/<max>')
def linear_trans_sat(min, max):
    image = image_env["image"]
    new_data = transformation_lineaire_saturee(image, int(min), int(max))

    save_image(image, new_data, "lineartranssat.jpg")
    return "success"


@app.route('/dilater/<a>/<b>')
def dilater(a, b):
    image = image_env["image"]
    new_data = dilatation(image, int(a), int(b))

    save_image(image, new_data, "imagedilatee.jpg")
    return "success"


@app.route('/dilater_milieu/<a>/<b>/<c>')
def dilater_milieu(a, b, c):
    image = image_env["image"]
    new_data = dilatation_milieu(image, int(a), int(b), int(c))

    save_image(image, new_data, "imagedilatee_milieu.jpg")
    return "success"


@app.route('/invert')
def invert_colors():
    image = image_env["image"]
    new_data = color_inversion(image)
    save_image(image, new_data, "couleursinverses.jpg")
    return "success"


@app.route('/make_some_noise')
def make_some_noise():
    image = image_env["image"]
    new_data = noise_maker(image)
    save_image(image, new_data, "filters/dog_noise.jpg")
    return "success"


@app.route('/filter/moyenne/<size>')
def filtrer_moyenne(size):
    image = read_image("output/filters/dog_noise.jpg")
    new_data = filtre_moyenne(image, int(size))
    save_image(image, new_data, "filters/dog_filtered" + str(size) + ".jpg")
    return "success"


@app.route('/filter/mediane/<size>')
def filtrer_mediane(size):
    image = read_image("output/filters/dog_noise.jpg")
    new_data = filtre_mediane(image, int(size))
    save_image(image, new_data, "filters/dog_filtered_mediane" + str(size) + ".jpg")
    return "success"


@app.route('/filter/rehausseur')
def filtrer_rehausseur():
    image = image_env["image"]
    new_data = filtre_rehausseur(image, 3)
    save_image(image, new_data, "filters/dog_filtered_rehausseur3.jpg")
    return "success"

@app.route('/viewdata')
def afficher_donnees():
    image = image_env.get("image")
    html = "    <div>        <h4>filename :</h4>  " + image.filename + "" \
                                                                       "        <h4>format :</h4> " + image.format + "" \
                                                                                                                     "        <h4>mode :</h4> """ + image.mode + "" \
                                                                                                                                                                 "        <h4>size :</h4> """ + str(
        image.size) + "  </div> "
    return html


if __name__ == '__main__':
    app.run(debug=True)
