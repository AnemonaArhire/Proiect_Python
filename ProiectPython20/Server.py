import socket
import threading
import random

MAX_PLAYERS = 3
current_players = []
lock = threading.Lock()
VALID_MOVES = {"rock", "paper", "scissors", "lizard", "spock"}

def determine_outcome(player_move, server_move):
    if player_move == server_move:
        return "draw"

    if player_move == "rock":
        return "win" if server_move in ["scissors", "lizard"] else "lose"

    if player_move == "paper":
        return "win" if server_move in ["rock", "spock"] else "lose"

    if player_move == "scissors":
        return "win" if server_move in ["paper", "lizard"] else "lose"

    if player_move == "lizard":
        return "win" if server_move in ["spock", "paper"] else "lose"

    if player_move == "spock":
        return "win" if server_move in ["scissors", "rock"] else "lose"

    return "invalid"

def handle_client(client_socket, client_address):

    print(f"Player {client_address} connected.")
    client_socket.sendall("Welcome! The server already chose, now it's your turn!\n".encode())

    try:
        while True:
            client_socket.sendall("Enter your move (rock, paper, scissors, lizard, spock) or type 'exit' to leave: ".encode())
            player_move = client_socket.recv(1024).decode().strip().lower()

            if player_move == "exit":
                client_socket.sendall("You chose to exit the game. Goodbye!\n".encode())
                break

            if player_move not in VALID_MOVES:
                client_socket.sendall("Invalid move. Try again.\n".encode())
                continue

            server_move = random.choice(list(VALID_MOVES))
            print(f"Server choice for this round: {server_move}")
            print(f"Player {client_address} chose: {player_move}")

            result = determine_outcome(player_move, server_move)
            result_message = f"Server chose: {server_move}. You {result}!\n"

            if result == "lose":
                print(f"Player {client_address} lost.")
            elif result == "draw":
                print(f"You and player {client_address} drew!")
            else:
                print(f"Player {client_address} won!")

            client_socket.sendall(result_message.encode())

            if result == "lose":
                client_socket.sendall("You lost! Disconnecting...\n".encode())
                break

    except Exception as error:
        print(f"Error with player {client_address}: {error}")

    finally:
        client_socket.close()
        with lock:
            current_players.remove(client_socket)
        print(f"Player {client_address} disconnected.")

def reject_client(client_socket):

    try:
        client_socket.sendall("Server is full. You cannot join at the moment. Goodbye!\n".encode())
    except Exception as error:
        print(f"Error sending rejection message: {error}")
    finally:
        client_socket.close()

def main():
    host = "0.0.0.0"
    port = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(MAX_PLAYERS)

    print(f"Server started on {host}:{port}. Waiting for players...")

    while True:
        client_socket, client_address = server_socket.accept()

        with lock:
            if len(current_players) < MAX_PLAYERS:
                current_players.append(client_socket)
                threading.Thread(target=handle_client, args=(client_socket, client_address)).start()
            else:
                print(f"Rejecting connection from {client_address}: server is full.")
                threading.Thread(target=reject_client, args=(client_socket,)).start()

if __name__ == "__main__":
    main()
