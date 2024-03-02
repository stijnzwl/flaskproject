from flask import render_template, redirect, url_for, flash
from app.casino import bp
from app.casino.blackjack import Blackjack
from app.casino.forms import FirstMoveForm, StartGameForm
from flask_login import current_user, login_required
from app.models import GameStatus, Game
from app import db


@bp.route("/blackjack", methods=["GET", "POST"])
@login_required
def blackjack():
    form = StartGameForm()
    if form.validate_on_submit() and form.start_game.data:
        blackjack_game = Blackjack()
        player_hand, dealer_hand, player_score, dealer_score = (
            blackjack_game.deal_initial_cards()
        )

        new_game = Game(user_id=current_user.id, game_type='Blackjack')
        db.session.add(new_game)
        db.session.flush()

        new_game_status = GameStatus(
            game_id=new_game.id,
            player_hand=str(player_hand),
            dealer_hand=str(dealer_hand),
            game_status='In Progress'
        )
        db.session.add(new_game_status)
        db.session.commit()
        flash('New game started!')
        return redirect(url_for("casino.blackjack", game_id=new_game.id))

    return render_template(
        "casino/blackjack.html",
        player_hand=player_hand,
        dealer_hand=dealer_hand,
        player_score=player_score,
        dealer_score=dealer_score,
        form=form,
    )
