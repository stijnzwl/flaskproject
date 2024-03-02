from flask import render_template, redirect, url_for, flash
from app.casino import bp
from app.casino.blackjack import Blackjack
from app.casino.forms import FirstMoveForm, StartGameForm
from flask_login import current_user, login_required
from app.models import GameStatus, Game
from app import db
import json


@bp.route("/blackjack", methods=["GET", "POST"])
@login_required
def blackjack():
    form = StartGameForm()
    if form.validate_on_submit() and form.start_game.data:
        blackjack_game = Blackjack()
        player_hand, dealer_hand, player_score, dealer_score = (
            blackjack_game.deal_initial_cards()
        )

        new_game = Game(user_id=current_user.id, game_type="Blackjack", winner="pending")
        db.session.add(new_game)
        db.session.flush()

        new_game_status = GameStatus(
            game_id=new_game.id,
            player_hand=json.dumps(player_hand),
            dealer_hand=json.dumps(dealer_hand),
            player_score=player_score,
            dealer_score=dealer_score,
            game_status="In Progress",
        )
        db.session.add(new_game_status)
        db.session.commit()
        flash("New game started!")

        game = (
            Game.query.filter_by(user_id=current_user.id, game_type="Blackjack", winner="pending")
            .order_by(Game.timestamp.desc())
            .first()
        )
        if game:
            game_status = GameStatus.query.filter_by(game_id=game.id).first()
            player_hand = json.loads(game_status.player_hand)
            dealer_hand = json.loads(game_status.dealer_hand)
            if player_score == 21 and dealer_score != 21:
                blackjack_game.blackjack_win(new_game)
        return render_template(
            "casino/blackjack.html",
            player_hand=player_hand,
            game_status=game_status,
            dealer_hand=dealer_hand,
        )

    game_status = None
    return render_template(
        "casino/blackjack.html",
        form=form,
        game_status=game_status,
    )
