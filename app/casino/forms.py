from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField
from wtforms.validators import DataRequired, Regexp, NumberRange


class StartGameForm(FlaskForm):
    start_game = SubmitField("Yes")
    bet_amount = DecimalField('Bet Amount', validators=[DataRequired(), NumberRange(min=1)])
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