from flask import Flask, render_template, flash, redirect, request, url_for
from flask.json import jsonify
from validator_reg import RegistrationForm, LoginForm

app = Flask(__name__)

app.config['SECRET_KEY'] = '0eb70a4c38502c60943698c824c98b20'

app.static_folder = 'static'

@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/register", methods = ['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        return jsonify(request.form)
    return render_template('signup.html', title = 'Register', form = form)

@app.route("/login", methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == 'adminblog' and form.password.data == 'password':
            return jsonify(request.form)
        else:
            return 'Login unsuccessful'
    return render_template('login.html', title = 'Login', form = form)



if __name__ == "__main__":
    app.run(debug=True)