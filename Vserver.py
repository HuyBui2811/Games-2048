import socket
import threading
import json
import os

# Paths for user and high scores data files
USER_DATA_FILE = 'users.json'
HIGH_SCORES_FILE = 'high_scores.json'
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000


# Load user and high score data from files
def load_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            users = json.load(file)
    else:
        users = {}

    if os.path.exists(HIGH_SCORES_FILE):
        with open(HIGH_SCORES_FILE, 'r') as file:
            high_scores = json.load(file)
    else:
        high_scores = {}

    return users, high_scores


# Save user and high score data to files
def save_data(users, high_scores):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(users, file)

    with open(HIGH_SCORES_FILE, 'w') as file:
        json.dump(high_scores, file)


# Initialize user and high score data
users, high_scores = load_data()


# Function to handle client requests
def handle_client(client_socket):
    global users, high_scores

    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break

            request = json.loads(message)
            action = request['action']

            if action == 'register':
                username = request['username']
                password = request['password']
                if username in users:
                    response = {'status': 'error', 'message': 'User already exists'}
                else:
                    users[username] = password
                    high_scores[username] = {'score': 0, 'high_score': 0}
                    save_data(users, high_scores)
                    response = {'status': 'success', 'message': 'Registration successful'}

            elif action == 'login':
                username = request['username']
                password = request['password']
                if users.get(username) == password:
                    response = {'status': 'success', 'message': 'Login successful'}
                else:
                    response = {'status': 'error', 'message': 'Invalid credentials'}

            elif action == 'submit_score':
                username = request['username']
                score = request['score']
                if username not in high_scores:
                    response = {'status': 'error', 'message': 'User not found'}
                else:
                    user_scores = high_scores[username]
                    new_high_score = False
                    if score > user_scores['high_score']:
                        user_scores['high_score'] = score
                        new_high_score = True
                    user_scores['score'] = score
                    save_data(users, high_scores)
                    response = {'status': 'success', 'message': 'Score submitted successfully',
                                'new_high_score': new_high_score}

            elif action == 'get_leaderboard':
                sorted_users = sorted(high_scores.items(), key=lambda x: x[1]['high_score'], reverse=True)
                leaderboard = [{'username': user[0], 'high_score': user[1]['high_score']} for user in sorted_users]
                response = {'status': 'success', 'leaderboard': leaderboard}

            elif action == 'get_player_stats':
                username = request['username']
                if username not in high_scores:
                    response = {'status': 'error', 'message': 'User not found'}
                else:
                    response = {'status': 'success', 'stats': high_scores[username]}

            client_socket.send(json.dumps(response).encode('utf-8'))

        except Exception as e:
            print(f"Error: {e}")
            break

    client_socket.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen(5)
    print("Server started and listening on port 5000")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()


if __name__ == '__main__':
    start_server()
