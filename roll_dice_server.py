import socket


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", 3003))
    server_socket.listen()

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")

        request = client_socket.recv(1024).decode()
        if (not request) or ('favicon.ico' in request):
            client_socket.close()
            continue

        request_line = request.splitlines()[0]
        method, query_params, http_version = request_line.split(" ")

        if query_params:
            param_lst = (query_params[2:]).split("&")
            params = {p: v for p, v in (param.split("=") for param in param_lst)}

        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(request_line)}\r\n"
            "\r\n"
            f"{request_line}\n"
        )
        client_socket.sendall(response.encode())
        client_socket.close()


if __name__ == "__main__":
    main()
