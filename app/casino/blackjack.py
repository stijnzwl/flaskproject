from random import shuffle
from flask import flash
from app import db
import json
from flask_login import current_user
from decimal import Decimal


class Blackjack:
    def __init__(self, deck=None, player_hand=None, dealer_hand=None):
        self.deck = deck if deck is not None else self.create_deck()
        self.player_hand = player_hand if player_hand is not None else []
        self.dealer_hand = dealer_hand if dealer_hand is not None else []
        self.player_score = 0
        self.dealer_score = 0
        self.aces = [
            "Ace of Hearts",
            "Ace of Diamonds",
            "Ace of Clubs",
            "Ace of Spades",
        ]

    def create_deck(self):
        suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        names = [
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "Jack",
            "Queen",
            "King",
            "Ace",
        ]
        values = {
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
            "9": 9,
            "10": 10,
            "Jack": 10,
            "Queen": 10,
            "King": 10,
            "Ace": 11,
        }

        deck = []

        for suit in suits:
            for name in names:
                card_value = values[name]
                card_name = f"{name} of {suit}"
                image_path = f"/cards/card_{suit.lower()}_{name}.png"
                deck.append((card_name, card_value, image_path))
        shuffle(deck)
        return deck

    def update_scores(self):
        self.player_score = self.calculate_hand_value(self.player_hand)
        self.dealer_score = self.calculate_hand_value(self.dealer_hand)

    def update_game_status(
        self,
        game,
        game_status,
        winner,
        message,
        status,
        player_score,
        dealer_score,
        deck,
    ):
        game.winner = winner
        game_status.game_status = status
        game_status.dealer_score = dealer_score
        game_status.player_score = player_score
        game_status.deck = json.dumps(deck)
        db.session.commit()
        flash(message)

    def deal_initial_cards(self):
        for _ in range(2):
            self.player_hand.append(self.deck.pop())
            self.dealer_hand.append(self.deck.pop())
        self.update_scores()
        return (
            self.player_hand,
            self.dealer_hand,
            self.player_score,
            self.dealer_score,
            self.deck,
        )

    def player_hit(self, game_status):
        card = self.deck.pop()
        self.player_hand.append(card)
        self.player_score = self.calculate_hand_value(self.player_hand)
        game_status.deck = json.dumps(self.deck)
        return self.player_hand, self.player_score, self.deck

    def dealer_hit(self, game_status):
        card = self.deck.pop()
        self.dealer_hand.append(card)
        self.dealer_score = self.calculate_hand_value(self.dealer_hand)
        game_status.deck = json.dumps(self.deck)
        return self.dealer_hand, self.dealer_score, self.deck

    def calculate_hand_value(self, hand):
        total = 0
        ace_count = 0
        for card in hand:
            value, is_ace = card[1], card[0] in self.aces
            total += value
            if is_ace:
                ace_count += 1
        while total > 21 and ace_count > 0:
            total -= 10
            ace_count -= 1
        return total

    def blackjack_win(self, game, game_status, player_score, dealer_score, deck, bet):
        winnings = bet * Decimal("2.5")
        current_user.balance += Decimal(winnings)
        self.update_game_status(
            game,
            game_status,
            "Player",
            f"Blackjack! You win ${winnings}",
            "Finished",
            player_score,
            dealer_score,
            deck,
        )

    def blackjack_loss(self, game, game_status, player_score, dealer_score, deck):
        self.update_game_status(
            game,
            game_status,
            "Dealer",
            "Dealer has blackjack, you lose!",
            "Finished",
            player_score,
            dealer_score,
            deck,
        )

    def blackjack_tie(self, game, game_status, player_score, dealer_score, deck, bet):
        winnings = bet
        current_user.balance += Decimal(winnings)
        self.update_game_status(
            game,
            game_status,
            "tie",
            f"Blackjack, but the dealer also has blackjack. Tie! Balance: ${current_user.balance}",
            "Finished",
            player_score,
            dealer_score,
            deck,
        )

    def player_bust(self, game, game_status, player_score, dealer_score, deck):
        self.update_game_status(
            game,
            game_status,
            "Dealer",
            "You bust! Dealer wins.",
            "Finished",
            player_score,
            dealer_score,
            deck,
        )

    def player_21(self, game, game_status, player_score, dealer_score, deck, bet):
        while dealer_score < 17:
            dealer_hand, dealer_score, deck = self.dealer_hit(game_status)
            if dealer_score > 21:
                winnings = bet * Decimal("2")
                current_user.balance += Decimal(winnings)
                self.update_game_status(
                    game,
                    game_status,
                    "Player",
                    f"Dealer busts, you win ${winnings}",
                    "Finished",
                    player_score,
                    dealer_score,
                    deck,
                )
                break
        if dealer_score >= 17 and dealer_score < 21:
            winnings = bet * Decimal("2")
            current_user.balance += Decimal(winnings)
            self.update_game_status(
                game,
                game_status,
                "Player",
                f"Dealer stands, you win ${winnings}!",
                "Finished",
                player_score,
                dealer_score,
                deck,
            )

        elif dealer_score == 21:
            winnings = bet
            current_user.balance += Decimal(winnings)
            self.update_game_status(
                game,
                game_status,
                "tie",
                "Dealer also has 21, tie!",
                "Finished",
                player_score,
                dealer_score,
                deck,
            )

    def player_not_21(self, game, game_status, player_score, dealer_score, deck, bet):
        if dealer_score >= 17:
            self.update_game_status(
                game,
                game_status,
                "Pending",
                "Dealer stands",
                "In Progress",
                player_score,
                dealer_score,
                deck,
            )
            if player_score > dealer_score:
                winnings = bet * Decimal("2")
                current_user.balance += Decimal(winnings)
                self.update_game_status(
                    game,
                    game_status,
                    "Player",
                    f"You win ${winnings}!",
                    "Finished",
                    player_score,
                    dealer_score,
                    deck,
                )
        if dealer_score < 17:
            dealer_hand, dealer_score, deck = self.dealer_hit(game_status)
            if dealer_score > 21:
                winnings = bet * Decimal("2")
                current_user.balance += Decimal(winnings)
                self.update_game_status(
                    game,
                    game_status,
                    "Player",
                    f"Dealer busts, you win ${winnings}!",
                    "Finished",
                    player_score,
                    dealer_score,
                    deck,
                )
            elif dealer_score == 21:
                self.update_game_status(
                    game,
                    game_status,
                    "Dealer",
                    "Dealer hits and has 21, you lose!",
                    "Finished",
                    player_score,
                    dealer_score,
                    deck,
                )
