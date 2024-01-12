# flask run --debug

# Limitations.
# png_data_uri() / svg_data_uri() cannot use both scale and border at the same time if border = 0
# setting border = 0 resets qr code to its smallest size even when scale is greater than 1

import base64
import io
import secrets
from urllib.request import urlopen

import segno
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_wtf import CSRFProtect, FlaskForm
from wtforms import IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, NumberRange
from wtforms.widgets import ColorInput

app = Flask(__name__)
Bootstrap(app)

foo = secrets.token_urlsafe(16)
app.secret_key = foo

csrf = CSRFProtect(app)

DEFAULT_QRCODE_INFO = {
    "data": "",
    "gif_url": "",
    "color": "#000000",
    "color_acc": "#000000",
    "bg_color": "#fafafa",
    "bg_color_acc": "#fafafa",
    "border_size": 1,
    "scale": 10,
}


class QrCodeForm(FlaskForm):
    qrcode_data = TextAreaField(
        "STRING DATA", render_kw={"placeholder": "https://github.com/"}
    )
    qrcode_gif_url = TextAreaField(
        "GIF URL",
        render_kw={
            "placeholder": "https://media.giphy.com/media/du3J3cXyzhj75IOgvA/giphy.gif"
        },
    )
    qrcode_color = StringField("COLOR", widget=ColorInput())
    qrcode_color_hex = StringField("COLOR")
    qrcode_color_acc = StringField("COLOR ACCENT", widget=ColorInput())
    qrcode_color_acc_hex = StringField("COLOR ACCENT")
    qrcode_bg_color = StringField("BACKGROUND COLOR", widget=ColorInput())
    qrcode_bg_color_hex = StringField("BACKGROUND COLOR")
    qrcode_bg_color_acc = StringField("BACKGROUND COLOR ACCENT", widget=ColorInput())
    qrcode_bg_color_acc_hex = StringField("BACKGROUND COLOR ACCENT")
    qrcode_border_size = IntegerField(
        "BORDER SIZE", validators=[DataRequired(), NumberRange(min=1, max=10)]
    )
    qrcode_scale = IntegerField(
        "SCALE", validators=[DataRequired(), NumberRange(min=1, max=10)]
    )
    submit = SubmitField("Submit")


def make_qrcode_png(qrcode_info):
    qrcode = segno.make_qr(qrcode_info["data"])
    qrcode_png = qrcode.png_data_uri(
        dark=qrcode_info["color"],
        data_dark=qrcode_info["color_acc"],
        light=qrcode_info["bg_color"],
        data_light=qrcode_info["bg_color_acc"],
        border=qrcode_info["border_size"],
        scale=qrcode_info["scale"],
    )
    return qrcode_png


def make_qrcode(qrcode_info):
    buff = io.BytesIO()
    segno.make_qr(qrcode_info["data"]).save(
        buff,
        kind="png",
        dark=qrcode_info["color"],
        data_dark=qrcode_info["color_acc"],
        light=qrcode_info["bg_color"],
        data_light=qrcode_info["bg_color_acc"],
        border=qrcode_info["border_size"],
        scale=qrcode_info["scale"],
    )
    buff.seek(0)
    encoded_img_data = base64.b64encode(buff.getvalue())
    return encoded_img_data


def make_animated_qrcode(qrcode_info):
    qrcode = segno.make_qr(qrcode_info["data"])
    url = qrcode_info["gif_url"]
    animated_file = urlopen(url)
    buff = io.BytesIO()
    qrcode.to_artistic(
        background=animated_file,
        target=buff,
        kind="gif",
        dark=qrcode_info["color"],
        data_dark=qrcode_info["color_acc"],
        light=qrcode_info["bg_color"],
        data_light=qrcode_info["bg_color_acc"],
        border=qrcode_info["border_size"],
        scale=qrcode_info["scale"],
    )
    buff.seek(0)
    encoded_img_data = base64.b64encode(buff.getvalue())
    return encoded_img_data


@app.route("/", methods=["GET", "POST"])
def home():
    form = QrCodeForm()
    qrcode_info = {}

    if request.method == "POST":
        qrcode_info["data"] = request.values["qrcode_data"].strip()
        qrcode_info["gif_url"] = request.values["gif_url"].strip()
        qrcode_info["color"] = request.values["color"]
        qrcode_info["color_acc"] = request.values["color_acc"]
        qrcode_info["bg_color"] = request.values["bg_color"]
        qrcode_info["bg_color_acc"] = request.values["bg_color_acc"]
        qrcode_info["border_size"] = int(request.values["border_size"])
        qrcode_info["scale"] = int(request.values["scale"])
        if qrcode_info["gif_url"]:
            try:
                encoded_img_data = make_animated_qrcode(qrcode_info)
            except:
                print(
                    "Could not generate animated QR code. Generating regular QR code."
                )
                encoded_img_data = make_qrcode(qrcode_info)
        else:
            encoded_img_data = make_qrcode(qrcode_info)
        return encoded_img_data.decode("utf-8")

    form.qrcode_data.data = DEFAULT_QRCODE_INFO["data"]
    form.qrcode_gif_url.data = DEFAULT_QRCODE_INFO["gif_url"]
    form.qrcode_color.data = DEFAULT_QRCODE_INFO["color"]
    form.qrcode_color_hex.data = DEFAULT_QRCODE_INFO["color"]
    form.qrcode_color_acc.data = DEFAULT_QRCODE_INFO["color_acc"]
    form.qrcode_color_acc_hex.data = DEFAULT_QRCODE_INFO["color_acc"]
    form.qrcode_bg_color.data = DEFAULT_QRCODE_INFO["bg_color"]
    form.qrcode_bg_color_hex.data = DEFAULT_QRCODE_INFO["bg_color"]
    form.qrcode_bg_color_acc.data = DEFAULT_QRCODE_INFO["bg_color_acc"]
    form.qrcode_bg_color_acc_hex.data = DEFAULT_QRCODE_INFO["bg_color_acc"]
    form.qrcode_border_size.data = DEFAULT_QRCODE_INFO["border_size"]
    form.qrcode_scale.data = DEFAULT_QRCODE_INFO["scale"]
    if form.qrcode_gif_url.data:
        encoded_img_data = make_animated_qrcode(DEFAULT_QRCODE_INFO)
    else:
        encoded_img_data = make_qrcode(DEFAULT_QRCODE_INFO)
    return render_template(
        "home.html",
        qrcode_img_data=encoded_img_data.decode("utf-8"),
        form=form,
        qrcode_info=DEFAULT_QRCODE_INFO,
    )
