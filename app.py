from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5

from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField, EmailField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, Email
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = 'your_long_term_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Use SQLite for simplicity
db = SQLAlchemy(app)

# Bootstrap-Flask requires this line
bootstrap = Bootstrap5(app)
# Flask-WTF requires this line
csrf = CSRFProtect(app)

class Contactdb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    number = db.Column(db.String(15), nullable=False)
    text_field = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Contact(id={self.id}, name={self.name}, email={self.email}, number={self.number}, text_field={self.text_field})"


class ContactForm(FlaskForm):
    name = StringField('Full name: ', validators=[DataRequired(), Length(10, 60)])
    email = EmailField('Email: ', validators=[DataRequired(), Email()])
    number = IntegerField('phone', validators=[DataRequired()])
    content = TextAreaField('Explain any concern', validators=[DataRequired(), Length(10, 250)])
    submit = SubmitField('Submit')

    def __str__(self):
        return f'{self.name.data} has upload a concern {self.content.data}'

@app.route('/', methods=['GET', 'POST'])
def index():
    # you must tell the variable 'form' what you named the class, above
    # 'form' is the variable name used in this template: index.html
    form = ContactForm()
    message = ""
    if form.validate_on_submit():
        # Create a new Contact instance and add it to the database
        new_contact = Contactdb(
            name=form.name.data,
            email=form.email.data,
            number=form.number.data,
            text_field=form.content.data
        )



        db.session.add(new_contact)
        try:
            db.session.commit()
        except IntegrityError as err:
            if 'email' in str(err):
                print('Email already registered')
            else:
                print(err)
        
        message = "Consulta enviada. Gracias."

        print(form)
    return render_template('index.html', form=form, message=message)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=False)
