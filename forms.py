from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired

class JoinForm(FlaskForm):
    user_id = StringField('ID de Usuario', validators=[DataRequired()])
    team = SelectField('Selecciona tu equipo', choices=[('Equipo A', 'Equipo A'), ('Equipo B', 'Equipo B')], validators=[DataRequired()])
    submit = SubmitField('Unirse al Equipo')

