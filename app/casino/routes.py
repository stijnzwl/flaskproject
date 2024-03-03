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
        player_hand, dealer_hand, player_score, dealer_score, modified_deck = (
            blackjack_game.deal_initial_cards()
        )

        new_game = Game(
            user_id=current_user.id, game_type="Blackjack", winner="Pending"
        )
        db.session.add(new_game)
        db.session.flush()

        new_game_status = GameStatus(
            game_id=new_game.id,
            player_hand=json.dumps(player_hand),
            dealer_hand=json.dumps(dealer_hand),
            deck=json.dumps(modified_deck),
            player_score=player_score,
            dealer_score=dealer_score,
            game_status="First Move",
        )
        db.session.add(new_game_status)
        db.session.commit()
        flash("New game started!")

        game = (
            Game.query.filter_by(
                user_id=current_user.id, game_type="Blackjack", winner="Pending"
            )
            .order_by(Game.timestamp.desc())
            .first()
        )
        if game:
            game_status = GameStatus.query.filter_by(game_id=game.id).first()
            player_hand = json.loads(game_status.player_hand)
            dealer_hand = json.loads(game_status.dealer_hand)
            modified_deck = json.loads(game_status.deck)
            if player_score == 21 and dealer_score != 21:
                blackjack_game.blackjack_win(
                    game, game_status, player_score, dealer_score, modified_deck
                )
            if player_score == 21 and dealer_score == 21:
                blackjack_game.blackjack_tie(
                    game, game_status, player_score, dealer_score, modified_deck
                )
        return render_template(
            "casino/blackjack.html",
            player_hand=player_hand,
            game_status=game_status,
            dealer_hand=dealer_hand,
            player_score=player_score,
            dealer_score=dealer_score,
        )

    game_status = None
    return render_template(
        "casino/blackjack.html",
        form=form,
        game_status=game_status,
    )


@bp.route("/blackjack/hit", methods=["GET", "POST"])
@login_required
def blackjack_hit():
    game = (
        Game.query.filter_by(
            user_id=current_user.id, game_type="Blackjack", winner="Pending"
        )
        .order_by(Game.timestamp.desc())
        .first()
    )
    if not game:
        return redirect(url_for('casino.blackjack'))
    game_status = GameStatus.query.filter_by(game_id=game.id).first()
    game_status.game_status = "hit"
    modified_deck = json.loads(game_status.deck)
    dealer_hand = json.loads(game_status.dealer_hand)
    player_hand = json.loads(game_status.player_hand)
    blackjack_game = Blackjack(modified_deck, player_hand, dealer_hand)
    player_hand, player_score, modified_deck = blackjack_game.player_hit(game_status)
    dealer_score = game_status.dealer_score
    if len(dealer_hand) == 2 and dealer_score == 21:
        blackjack_game.blackjack_loss(
            game, game_status, player_score, dealer_score, modified_deck
        )
    elif player_score > 21:
        blackjack_game.player_bust(
            game, game_status, player_score, dealer_score, modified_deck
        )
    elif player_score == 21 and dealer_score != 21:
        blackjack_game.player_21(
            game, game_status, player_score, dealer_score, modified_deck
        )
    elif player_score < 21:
        blackjack_game.player_not_21(
            game, game_status, player_score, dealer_score, modified_deck
        )
    game_status.player_hand = json.dumps(player_hand)
    game_status.dealer_hand = json.dumps(dealer_hand)
    db.session.commit()
    return render_template(
        "casino/blackjack.html",
        player_hand=player_hand,
        game_status=game_status,
        dealer_hand=dealer_hand,
    )


# @bp.route('/blackjack/stand', method=['GET', 'POST'])
# @login_required
# def blackjack_stand():
#     pass