import socket
import threading
import random

MAX_PLAYERS = 3
connected_players = []
lock = threading.Lock()
MOVES = {"rock", "paper", "scissors", "lizard", "spock"}

def determine_result(player_choice, server_choice):
    if player_choice == server_choice:
        return "draw"

    if player_choice == "rock":
        if server_choice in ["scissors", "lizard"]:
            return "win"
        else:
            return "lose"

    elif player_choice == "paper":
        if server_choice in ["rock", "spock"]:
            return "win"
        else:
            return "lose"

    elif player_choice == "scissors":
        if server_choice in ["paper", "lizard"]:
            return "win"
        else:
            return "lose"

    elif player_choice == "lizard":
        if server_choice in ["spock", "paper"]:
            return "win"
        else:
            return "lose"

    elif player_choice == "spock":
        if server_choice in ["scissors", "rock"]:
            return "win"
        else:
            return "lose"

    return "invalid"

def handle_player(player_socket, addr):
    print(f"Player {addr} connected.")
    player_socket.sendall(f"Welcome! The server already chose, now it's your turn!\n".encode())

    try:
        while True:
            player_socket.sendall("Enter your move (rock, paper, scissors, lizard, spock) or type 'exit' to leave: ".encode())
            player_choice = player_socket.recv(1024).decode().strip().lower()

            if player_choice == "exit":
                player_socket.sendall("You chose to exit the game. Goodbye!\n".encode())
                break

            if player_choice not in MOVES:
                player_socket.sendall("Invalid move. Try again.\n".encode())
                continue

            server_choice = random.choice(list(MOVES))
            print(f"Server choice for this round: {server_choice}")
            print(f"Player {addr} chose: {player_choice}")

            # Determină rezultatul pentru jucător
            result = determine_result(player_choice, server_choice)
            result_message = f"Server chose: {server_choice}. You {result}!\n"

            player_socket.sendall(result_message.encode())

            # Dacă jucătorul pierde, încheiem jocul pentru el
            if result == "lose":
                player_socket.sendall("You lost! Disconnecting...\n".encode())
                break

    except Exception as e:
        print(f"Error with player {addr}: {e}")

    finally:
        player_socket.close()
        with lock:
            connected_players.remove(player_socket)
        print(f"Player {addr} disconnected.")

def handle_rejected_player(client_socket):
    try:
        client_socket.sendall("Server is full. You cannot join at the moment. Goodbye!\n".encode())
    except Exception as e:
        print(f"Error sending rejection message: {e}")
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
        client_socket, addr = server_socket.accept()

        with lock:
            if len(connected_players) < MAX_PLAYERS:
                connected_players.append(client_socket)
                threading.Thread(target=handle_player, args=(client_socket, addr)).start()
            else:
                print(f"Rejecting connection from {addr}: server is full.")
                threading.Thread(target=handle_rejected_player, args=(client_socket,)).start()

if __name__ == "__main__":
    main()
