# flask run --debug

# Limitations.
# png_data_uri() / svg_data_uri() cannot use both scale and border at the same time if border = 0
# setting border = 0 resets qr code to its smallest size even when scale is greater than 1

from flask import Flask, render_template, request, send_file, abort, Response
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, TextAreaField, IntegerField, SubmitField
from wtforms.widgets import ColorInput
from wtforms.validators import DataRequired, Length, NumberRange
from urllib.request import urlopen
from urllib.error import HTTPError
import segno
import io
import base64
import secrets

app = Flask(__name__)
Bootstrap(app)

foo = secrets.token_urlsafe(16)
app.secret_key = foo

csrf = CSRFProtect(app)

default_qrcode_info = {
    'data': '',
    'gif_url': '',
    'color': 'black',
    'color_acc': 'black',
    'bg_color': '#FAFAFA',
    'bg_color_acc': '#FAFAFA',
    'border_size': 1,
    'scale': 10,
}


class QrCodeForm(FlaskForm):
    qrcode_data = TextAreaField('STRING DATA',
                              render_kw={'placeholder': 'https://github.com/'})
    qrcode_gif_url = TextAreaField('GIF URL',
                                 render_kw={'placeholder': 'https://media.giphy.com/media/du3J3cXyzhj75IOgvA/giphy.gif'})
    qrcode_color = StringField('COLOR', widget=ColorInput())
    qrcode_color_acc = StringField('COLOR ACCENT', widget=ColorInput())
    qrcode_bg_color = StringField('BACKGROUND COLOR', widget=ColorInput())
    qrcode_bg_color_acc = StringField('BACKGROUND COLOR ACCENT',widget=ColorInput())
    qrcode_border_size = IntegerField('BORDER SIZE', validators=[DataRequired(), NumberRange(min=1, max=10)])
    qrcode_scale = IntegerField('SCALE', validators=[DataRequired(), NumberRange(min=1, max=10)])
    submit = SubmitField('Submit')


def make_qrcode_png(qrcode_info):
    qrcode = segno.make_qr(qrcode_info['data'])
    qrcode_png = qrcode.png_data_uri(
        dark=qrcode_info['color'],
        data_dark=qrcode_info['color_acc'],
        light=qrcode_info['bg_color'],
        data_light=qrcode_info['bg_color_acc'],
        border=qrcode_info['border_size'],
        scale=qrcode_info['scale'],
    )
    return qrcode_png


def make_qrcode(qrcode_info):
    buff = io.BytesIO()
    segno.make_qr(qrcode_info['data']) \
        .save(
            buff,
            kind='png',
            dark=qrcode_info['color'],
            data_dark=qrcode_info['color_acc'],
            light=qrcode_info['bg_color'],
            data_light=qrcode_info['bg_color_acc'],
            border=qrcode_info['border_size'],
            scale=qrcode_info['scale'],
    )
    buff.seek(0)
    encoded_img_data = base64.b64encode(buff.getvalue())
    return encoded_img_data


def make_animated_qrcode(qrcode_info):
    qrcode = segno.make_qr(qrcode_info['data'])
    url = qrcode_info['gif_url']
    animated_file = urlopen(url)
    buff = io.BytesIO()
    qrcode.to_artistic(
        background=animated_file,
        target=buff,
        kind='gif',
        dark=qrcode_info['color'],
        data_dark=qrcode_info['color_acc'],
        light=qrcode_info['bg_color'],
        data_light=qrcode_info['bg_color_acc'],
        border=qrcode_info['border_size'],
        scale=qrcode_info['scale'],
    )
    buff.seek(0)
    encoded_img_data = base64.b64encode(buff.getvalue())
    return encoded_img_data


@app.route('/', methods=['GET', 'POST'])
def home():
    form = QrCodeForm()
    qrcode_info = {}

    if request.method == 'POST':
        qrcode_info['data'] = request.values['qrcode_data'].strip()
        qrcode_info['gif_url'] = request.values['gif_url'].strip()
        qrcode_info['color'] = request.values['color']
        qrcode_info['color_acc'] = request.values['color_acc']
        qrcode_info['bg_color'] = request.values['bg_color']
        qrcode_info['bg_color_acc'] = request.values['bg_color_acc']
        qrcode_info['border_size'] = int(request.values['border_size'])
        qrcode_info['scale'] = int(request.values['scale'])
        if qrcode_info['gif_url']:
            try:
                encoded_img_data = make_animated_qrcode(qrcode_info)
            except:
                print('Could not generate animated QR code. Generating regular QR code.')
                encoded_img_data = make_qrcode(qrcode_info)
        else:
            encoded_img_data = make_qrcode(qrcode_info)
        return encoded_img_data.decode('utf-8')

    form.qrcode_data.data = default_qrcode_info['data']
    form.qrcode_gif_url.data = default_qrcode_info['gif_url']
    form.qrcode_color.data = default_qrcode_info['color']
    form.qrcode_color_acc.data = default_qrcode_info['color_acc']
    form.qrcode_bg_color.data = default_qrcode_info['bg_color']
    form.qrcode_bg_color_acc.data = default_qrcode_info['bg_color_acc']
    form.qrcode_border_size.data = default_qrcode_info['border_size']
    form.qrcode_scale.data = default_qrcode_info['scale']
    if form.qrcode_gif_url.data:
        encoded_img_data = make_animated_qrcode(default_qrcode_info)
    else:
        encoded_img_data = make_qrcode(default_qrcode_info)
    return render_template('home.html',
                           qrcode_img_data=encoded_img_data.decode('utf-8'),
                           form=form)
