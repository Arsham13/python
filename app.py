from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user,logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 't8h1e6s3e4c5r2e7t0k9e@y'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

with app.app_context():
    db = SQLAlchemy(app)
    bcrypt = Bcrypt(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)

class LoginForm(FlaskForm):
    username = StringField(validators=[
        InputRequired(), Length(min=6, max=20)
    ], render_kw={
        'placeholder': 'username'
    })
    password = PasswordField(validators=[
        InputRequired(), Length(min=6, max=20)
    ], render_kw={
        'placeholder': 'password'
    })
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField(validators=[
        InputRequired(), Length(min=6, max=20)
    ], render_kw={
        'placeholder': 'username'
    })
    password = PasswordField(validators=[
        InputRequired(), Length(min=6, max=20)
    ], render_kw={
        'placeholder': 'password'
    })
    submit = SubmitField('Register')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm() 
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)



@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)