import socket

def main():
    host = "127.0.0.1"
    port = 12345

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    try:
        while True:
            message = client_socket.recv(1024).decode()
            print(message)

            if "Enter your move" in message:
                choice = input("Your move: ")
                client_socket.sendall(choice.encode())

            if "Goodbye" in message or "Disconnecting" in message:
                break


    except KeyboardInterrupt:
        print("\nDisconnected.")
    finally:
        client_socket.close()


if __name__ == "__main__":
    main()
