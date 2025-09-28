import random
from time import sleep
from collections import deque

# Knight > Archer, Mage > Knight, Archer > Mage
move_choices = ["Knight", "Archer", "Mage"]

beats = {
    "Knight": "Archer",  # Knight beats Archer
    "Archer": "Mage",    # Archer beats Mage
    "Mage": "Knight"     # Mage beats Knight
}

beaten_by = {
    "Knight": "Mage",    # Knight is beaten by Mage
    "Archer": "Knight",  # Archer is beaten by Knight
    "Mage": "Archer"     # Mage is beaten by Archer
}

weights = {
    "Knight": 1,
    "Archer": 1,
    "Mage": 1
}

player_last_moves = deque(maxlen=3)  # Uhsed for ai predictions

win_streak = 0
loss_streak = 0


class Player:
    def __init__(self, gems, health):
        self.move = None
        self.gems = gems
        self.health = health
        self.win_streak = win_streak
        self.loss_streak = loss_streak
        self.has_been_taunted = False

    def make_move(self):
        choice = input("""Enter your move:
K- Knight
A- Archer
M- Mage
""").upper().strip()

        if choice == "K":
            self.move = "Knight"
        elif choice == "A":
            self.move = "Archer"
        elif choice == "M":
            self.move = "Mage"
        else:
            print("Invalid move")
            return self.make_move()

        player_last_moves.append(self.move)
        return self.move

    def __str__(self):
        return f"Player- {self.gems} - {self.health}"


class Corruptor:
    def __init__(self):
        self.move = None
        self.has_taunted = False

    def make_move(self):
        if len(player_last_moves) == 3 and len(set(player_last_moves)) == 1:
            # All 3 moves are identical - force counter
            if not self.has_taunted:
                sleep(2)
                print("Corruptor: Foolish mortal!")
                sleep(2)
                self.has_taunted = True
            last_move = player_last_moves[0]
            counter_move = beaten_by[last_move]
            self.move = counter_move
            return self.move

        moves = list(weights.keys())
        move_weights = list(weights.values())
        self.move = random.choices(moves, weights=move_weights)[0]
        return self.move

    def __str__(self):
        return f"Corruptor- {self.move}"


corruptor = Corruptor()
player = Player(0, 100)


def play_game():
    corruptor_move = corruptor.make_move()
    player_move = player.make_move()

    damage = 10 + player.loss_streak * 10
    round_won = False
    round_tied = False
    sleep(1)

    if corruptor_move == player_move:
        print("It's a tie! Try Again")
        round_tied = True
    elif corruptor_move == "Knight" and player_move == "Archer":
        print("That's unlucky... ")
        round_won = False
    elif corruptor_move == "Archer" and player_move == "Mage":
        print("That's unlucky... ")
        round_won = False
    elif corruptor_move == "Mage" and player_move == "Knight":
        print("That's unlucky... ")
        round_won = False
    else:
        print("You've passed this one for now")
        round_won = True

    if round_won:
        player.gems += 1 + player.win_streak
        player.win_streak += 1
        player.loss_streak = 0
    elif round_tied:
        player.win_streak = 0
        player.loss_streak = 0
    else:
        player.health -= damage
        player.health = max(player.health, 0)
        player.loss_streak += 1
        player.win_streak = 0
        if player.loss_streak >= 3 and not player.has_been_taunted:
            print("Corruptor: You are falling behind! 💀")
            player.has_been_taunted = True
    sleep(1)

    print(corruptor)
    print(player)

    temp_weights = {"Knight": 1, "Archer": 1, "Mage": 1}

    for move in set(player_last_moves):
        counter_move = beats[move]
        temp_weights[counter_move] -= player_last_moves.count(move) * 0.25
        temp_weights[counter_move] = max(temp_weights[counter_move], 0.1)

        beaten_move = beaten_by[move]
        temp_weights[beaten_move] -= player_last_moves.count(move) * 0.1
        temp_weights[beaten_move] = max(temp_weights[beaten_move], 0.1)

    weights.update(temp_weights)


while player.health > 0 and player.gems < 10:
    play_game()
