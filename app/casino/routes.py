from flask import render_template, redirect, url_for
from app.casino import bp
from app.casino.blackjack import Blackjack
from app.casino.forms import FirstMoveForm, StartGame
from flask_login import current_user, login_required
from app.models import GameStatus
from app import db


@bp.route("/blackjack", methods=["GET", "POST"])
@login_required
def blackjack():
    form = StartGame()
    game_status = None
    if form.validate_on_submit() and form.yes.data:
        blackjack = Blackjack()
        player_hand, dealer_hand, player_score, dealer_score = (
            blackjack.deal_initial_cards()
        )
        game_status = GameStatus(
            user_id=current_user.id,
            player_hand=str(player_hand),
            dealer_hand=str(dealer_hand),
            game_status="initial turn",
            player_score=player_score,
            dealer_score=dealer_score,
        )
        db.session.add(game_status)
        db.session.commit()
        return redirect(url_for("casino.blackjack"))

    return render_template(
        "casino/blackjack.html",
        player_hand=player_hand,
        dealer_hand=dealer_hand,
        player_score=player_score,
        dealer_score=dealer_score,
        form=form,
    )
