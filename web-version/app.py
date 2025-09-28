from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

# In memory game state
game_state = {
    'player': {'gems': 0, 'health': 100, 'win_streak': 0, 'loss_streak': 0},
    'weights': {'Knight': 1, 'Archer': 1, 'Mage': 1},
    'player_last_moves': []
}

beats = {
    "Knight": "Archer",
    "Archer": "Mage",
    "Mage": "Knight"
}

beaten_by = {
    "Knight": "Mage",
    "Archer": "Knight",
    "Mage": "Archer"
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/play', methods=['POST'])
def play_game():
    global game_state
    data = request.get_json()
    player_move = data['move']

    corruptor_move = get_corruptor_move(game_state)

    result = determine_winner(player_move, corruptor_move)

    update_game_state(game_state, player_move, result)

    game_over = False
    win = False
    if game_state['player']['health'] <= 0:
        game_over = True
        win = False
    elif game_state['player']['gems'] >= 10:
        game_over = True
        win = True

    return jsonify({
        'corruptorMove': corruptor_move,
        'message': result['message'],
        'gameState': game_state,
        'gameOver': game_over,
        'win': win
    })


def get_corruptor_move(state):
    """AI logic for corruptor move"""
    player_moves = state['player_last_moves']
    weights = state['weights']

    # Check for pattern (3 identical moves)
    if len(player_moves) >= 3 and len(set(player_moves[-3:])) == 1:
        # Counter the repeated move
        last_move = player_moves[-1]
        return beaten_by[last_move]

    # Use weighted random choice
    moves = list(weights.keys())
    move_weights = list(weights.values())
    return random.choices(moves, weights=move_weights)[0]


def determine_winner(player_move, corruptor_move):
    """Determine game result"""
    if player_move == corruptor_move:
        return {'result': 'tie', 'message': "It's a tie! Try Again"}
    elif corruptor_move in beats and beats[corruptor_move] == player_move:
        return {'result': 'lose', 'message': "That's unlucky..."}
    else:
        return {'result': 'win', 'message': "You've passed this one for now"}


def update_game_state(state, player_move, result):
    """Update game state based on result"""
    player = state['player']

    # Add player move to history (keep last 3)
    state['player_last_moves'].append(player_move)
    if len(state['player_last_moves']) > 3:
        state['player_last_moves'] = state['player_last_moves'][-3:]

    if result['result'] == 'win':
        player['gems'] += 1 + player['win_streak']
        player['win_streak'] += 1
        player['loss_streak'] = 0
    elif result['result'] == 'tie':
        player['win_streak'] = 0
        player['loss_streak'] = 0
    else:  # lose
        damage = 10 + player['loss_streak'] * 10
        player['health'] -= damage
        player['health'] = max(player['health'], 0)
        player['loss_streak'] += 1
        player['win_streak'] = 0

    # Update AI weights based on player patterns
    update_ai_weights(state)


def update_ai_weights(state):
    """Update AI weights based on player patterns - only considers last 3 moves"""
    # Reset weights to base values
    state['weights'] = {"Knight": 1, "Archer": 1, "Mage": 1}
    player_moves = state['player_last_moves']

    # Only consider the last 3 moves (which should already be limited to 3)
    for move in set(player_moves):
        counter_move = beats[move]
        state['weights'][counter_move] -= player_moves.count(move) * 0.25

        beaten_move = beaten_by[move]
        state['weights'][beaten_move] -= player_moves.count(move) * 0.1


@app.route('/state', methods=['GET'])
def get_state():
    return jsonify(game_state)


@app.route('/reset', methods=['POST'])
def reset_game():
    global game_state
    game_state = {
        'player': {'gems': 0, 'health': 100, 'win_streak': 0, 'loss_streak': 0},
        'weights': {'Knight': 1, 'Archer': 1, 'Mage': 1},
        'player_last_moves': []
    }
    return jsonify(game_state)


if __name__ == '__main__':
    app.run(debug=True)
