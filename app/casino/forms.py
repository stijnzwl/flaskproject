from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import sqlalchemy as sa
from app import db
from app.models import User, Game, GameStatus


class StartGame(FlaskForm):
    yes = SubmitField("Yes")
    no = SubmitField("No")


class FirstMoveForm(FlaskForm):
    hit = SubmitField("Hit")
    stand = SubmitField("Stand")
    double_down = SubmitField("Double down")
