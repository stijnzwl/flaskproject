from flask import render_template
from app.casino import bp
from app.casino.blackjack import Blackjack
from flask_login import current_user, login_required


@bp.route("/blackjack", methods=["GET", "POST"])
@login_required
def blackjack():
    blackjack = Blackjack()
    player_hand, dealer_hand, player_score, dealer_score = blackjack.deal_initial_cards()
    return render_template(
        "casino/blackjack.html",
        player_hand=player_hand,
        dealer_hand=dealer_hand,
        player_score=player_score,
        dealer_score=dealer_score,
    )
