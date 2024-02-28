from random import randint, shuffle



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
        deck = [
            ("2 of Hearts", 2),
            ("3 of Hearts", 3),
            ("4 of Hearts", 4),
            ("5 of Hearts", 5),
            ("6 of Hearts", 6),
            ("7 of Hearts", 7),
            ("8 of Hearts", 8),
            ("9 of Hearts", 9),
            ("10 of Hearts", 10),
            ("Jack of Hearts", 10),
            ("Queen of Hearts", 10),
            ("King of Hearts", 10),
            ("Ace of Hearts", 11),
            ("2 of Diamonds", 2),
            ("3 of Diamonds", 3),
            ("4 of Diamonds", 4),
            ("5 of Diamonds", 5),
            ("6 of Diamonds", 6),
            ("7 of Diamonds", 7),
            ("8 of Diamonds", 8),
            ("9 of Diamonds", 9),
            ("10 of Diamonds", 10),
            ("Jack of Diamonds", 10),
            ("Queen of Diamonds", 10),
            ("King of Diamonds", 10),
            ("Ace of Diamonds", 11),
            ("2 of Clubs", 2),
            ("3 of Clubs", 3),
            ("4 of Clubs", 4),
            ("5 of Clubs", 5),
            ("6 of Clubs", 6),
            ("7 of Clubs", 7),
            ("8 of Clubs", 8),
            ("9 of Clubs", 9),
            ("10 of Clubs", 10),
            ("Jack of Clubs", 10),
            ("Queen of Clubs", 10),
            ("King of Clubs", 10),
            ("Ace of Clubs", 11),
            ("2 of Spades", 2),
            ("3 of Spades", 3),
            ("4 of Spades", 4),
            ("5 of Spades", 5),
            ("6 of Spades", 6),
            ("7 of Spades", 7),
            ("8 of Spades", 8),
            ("9 of Spades", 9),
            ("10 of Spades", 10),
            ("Jack of Spades", 10),
            ("Queen of Spades", 10),
            ("King of Spades", 10),
            ("Ace of Spades", 11),
        ]
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
