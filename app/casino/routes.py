from flask import render_template, redirect, url_for, flash
from app.casino import bp
from app.casino.blackjack import Blackjack
from app.casino.forms import StartGameForm
from flask_login import current_user, login_required
from app.models import GameStatus, Game
from app import db
import json
from decimal import Decimal


@bp.route("/blackjack", methods=["GET", "POST"])
@login_required
def blackjack():
    form = StartGameForm()
    if form.validate_on_submit():
        return handle_start_game(form)
    return render_template("casino/blackjack.html", form=form, game_status=None)


def handle_start_game(form):
    bet_amount = form.bet_amount.data
    if not has_sufficient_balance(bet_amount):
        flash("Insufficient balance to cover the bet.", "warning")
        return redirect(url_for("casino.blackjack"))

    current_user.balance -= bet_amount
    db.session.commit()

    blackjack_game, game, game_status = start_blackjack_game(bet_amount)

    if game_status.game_status == "First Move":
        handle_initial_blackjack_logic(blackjack_game, game, game_status)

    return render_template(
        "casino/blackjack.html",
        player_hand=json.loads(game_status.player_hand),
        dealer_hand=json.loads(game_status.dealer_hand),
        player_score=game_status.player_score,
        dealer_score=game_status.dealer_score,
        game_status=game_status,
        bet_amount=bet_amount,
    )


def has_sufficient_balance(bet_amount):
    return current_user.balance >= bet_amount


def start_blackjack_game(bet_amount):
    blackjack_game = Blackjack()
    player_hand, dealer_hand, player_score, dealer_score, modified_deck = (
        blackjack_game.deal_initial_cards()
    )

    new_game = Game(
        user_id=current_user.id, game_type="Blackjack", winner="Pending", bet=bet_amount
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
        player_decision="Pending",
    )
    db.session.add(new_game_status)
    db.session.commit()
    flash(f"You have placed a bet for ${bet_amount}, Good Luck!")

    return blackjack_game, new_game, new_game_status


def handle_initial_blackjack_logic(blackjack_game, game, game_status):
    player_score = game_status.player_score
    dealer_score = game_status.dealer_score
    player_hand = json.loads(game_status.player_hand)
    dealer_hand = json.loads(game_status.dealer_hand)
    modified_deck = json.loads(game_status.deck)

    if player_score == 21:
        if dealer_score == 21:
            blackjack_game.blackjack_tie(
                game, game_status, player_score, dealer_score, modified_deck, game.bet
            )
        else:
            blackjack_game.blackjack_win(
                game, game_status, player_score, dealer_score, modified_deck, game.bet
            )

    else:
        flash("No initial Blackjack, game continues.", "secondary")

    db.session.commit()


@bp.route("/blackjack/hit", methods=["GET", "POST"])
@login_required
def blackjack_hit():
    game, game_status = get_latest_game_and_status()
    if not game:
        return redirect(url_for("casino.blackjack"))
    if game_status.game_status == "First Move":
        game_status.game_status = "In Progress"
    blackjack_game, player_hand, dealer_hand, modified_deck = setup_game_environment(
        game_status
    )

    player_score, dealer_score = handle_player_hit(blackjack_game, game, game_status)

    update_game_status(game_status, player_hand, dealer_hand, modified_deck)

    return render_template(
        "casino/blackjack.html",
        player_hand=player_hand,
        game_status=game_status,
        dealer_hand=dealer_hand,
        player_score=player_score,
        dealer_score=dealer_score,
    )


def get_latest_game_and_status():
    game = (
        Game.query.filter_by(
            user_id=current_user.id, game_type="Blackjack", winner="Pending"
        )
        .order_by(Game.timestamp.desc())
        .first()
    )
    game_status = GameStatus.query.filter_by(game_id=game.id).first() if game else None
    return game, game_status


def setup_game_environment(game_status):
    modified_deck = json.loads(game_status.deck)
    dealer_hand = json.loads(game_status.dealer_hand)
    player_hand = json.loads(game_status.player_hand)
    blackjack_game = Blackjack(modified_deck, player_hand, dealer_hand)
    return blackjack_game, player_hand, dealer_hand, modified_deck


def handle_player_hit(blackjack_game, game, game_status):
    player_hand, player_score, modified_deck = blackjack_game.player_hit(game_status)
    dealer_score = game_status.dealer_score
    dealer_hand = json.loads(game_status.dealer_hand)

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
            game, game_status, player_score, dealer_score, modified_deck, game.bet
        )
    elif player_score < 21:
        blackjack_game.player_not_21(
            game, game_status, player_score, dealer_score, modified_deck, game.bet
        )

    return player_score, dealer_score


def update_game_status(game_status, player_hand, dealer_hand, modified_deck):
    game_status.player_hand = json.dumps(player_hand)
    game_status.dealer_hand = json.dumps(dealer_hand)
    game_status.deck = json.dumps(modified_deck)
    db.session.commit()


@bp.route("/blackjack/stand", methods=["GET", "POST"])
@login_required
def blackjack_stand():
    game, game_status = get_latest_game_and_status()
    if not game:
        return redirect(url_for("casino.blackjack"))
    if game_status.game_status == "First Move":
        game_status.game_status = "In Progress"
    blackjack_game, player_hand, dealer_hand, modified_deck = setup_game_environment(
        game_status
    )
    game_status.player_decision = "Stand"
    player_score, dealer_score = handle_player_stand(blackjack_game, game, game_status)

    update_game_status(game_status, player_hand, dealer_hand, modified_deck)

    return render_template(
        "casino/blackjack.html",
        player_hand=player_hand,
        game_status=game_status,
        dealer_hand=dealer_hand,
        player_score=player_score,
        dealer_score=dealer_score,
    )


def handle_player_stand(blackjack_game, game, game_status):
    modified_deck = json.loads(game_status.deck)
    dealer_score = game_status.dealer_score
    player_score = game_status.player_score
    dealer_hand = json.loads(game_status.dealer_hand)
    
    if len(dealer_hand) == 2 and dealer_score == 21:
        blackjack_game.blackjack_loss(
            game, game_status, player_score, dealer_score, modified_deck
        )
    elif player_score == 21 and dealer_score != 21:
        blackjack_game.player_21(
            game, game_status, player_score, dealer_score, modified_deck, game.bet
        )
    elif player_score < 21 and dealer_score < 17:
        blackjack_game.player_not_21_stand(
            game, game_status, player_score, dealer_score, modified_deck, game.bet
            )
        dealer_score = game_status.dealer_score
    elif dealer_score >= 17:
        blackjack_game.player_not_21_stand(
            game, game_status, player_score, dealer_score, modified_deck, game.bet
        )
        dealer_score = game_status.dealer_score
    return player_score, dealer_score
