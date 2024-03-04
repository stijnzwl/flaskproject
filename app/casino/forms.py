from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Regexp


class StartGameForm(FlaskForm):
    start_game = SubmitField("Yes")
    no = SubmitField("No")


class FirstMoveForm(FlaskForm):
    hit = SubmitField("Hit")
    stand = SubmitField("Stand")
    double_down = SubmitField("Double down")


class BetForm(FlaskForm):
    amount = StringField(
        "Bet amount",
        validators=[
            Regexp(r"^\d+(\.\d{1,2})?$", message="Enter a valid amount."),
        ],
    )
    bet = SubmitField('Bet')