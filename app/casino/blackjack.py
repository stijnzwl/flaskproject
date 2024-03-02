from random import randint, shuffle
from flask import url_for, flash
from app.models import Game
from app import db


class Blackjack:
    def __init__(self):
        self.deck = self.create_deck()
        self.player_hand = []
        self.dealer_hand = []
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

    def deal_initial_cards(self):
        for _ in range(2):
            self.player_hand.append(self.deck.pop())
            self.dealer_hand.append(self.deck.pop())
        self.player_score = self.calculate_hand_value(self.player_hand)
        self.dealer_score = self.calculate_hand_value(self.dealer_hand)
        return self.player_hand, self.dealer_hand, self.player_score, self.dealer_score

    def hit(self, hand):
        card = self.deck.pop()
        hand.append(card)
        return card

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

    def blackjack_win(self, game):
        game.winner = "player"
        db.session.commit()
        flash("Blackjack! You win!")

    def blackjack_loss(self):
        flash("Dealer has blackjack, you lose!")

    def blackjack_tie(self):
        flash("Blackjack, but the dealer also has blackjack. Tie!")
