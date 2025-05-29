"""
Quick and dirty socket script to demonstrate a basic socket server that uses
query params and responds accordingly.
"""
import socket
from random import randint


def setup_socket(url: str, port: int) -> socket:
    """Sets up a socket listen on the given port at the given url"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((url, port))
    server_socket.listen()
    return server_socket


def populate_qry_params_dct(qry_param_strs: list) -> dict:
    """Populates a dictionary with {param : value} keys and values"""
    if qry_param_strs:
        return dict(
            param_str.split("=") for param_str in qry_param_strs.split("&")
        )
    else:
        return {}


def get_path_and_query_params_dct(path_and_params: str) -> tuple:
    """returns the path and a params dictionary (if any params exist)"""
    try:
        path, qry_param_strs = path_and_params.split("?")
    except ValueError:
        path = path_and_params
        qry_param_strs = ''
    return path, populate_qry_params_dct(qry_param_strs)


def append_rolls_to_body(rolls: int, sides: int) -> str:
    """Returns a str representation (`Roll: X`) of rolling a n-sides die by
    the number of given rolls"""
    roll_str = "<ul>"

    for _ in range(rolls):
        roll = randint(1, sides)
        roll_str += f"<li>Roll: {roll}</li>"
    return roll_str + "</ul>"


def get_response_body(request_line: str, http_method: str,
                      path: str, params_dct: dict) -> str:
    """Creates the response body"""
    return (
        "<html><head><title>Dice Rolls</title></head><body>"
        "<h1>HTTP Request Information</h1>"
        f"<p><strong>Request Line:</strong> {request_line}</p>"
        f"<p><strong>HTTP Method:</strong> {http_method}</p>"
        f"<p><strong>Path:</strong> {path}</p>"
        f"<p><strong>Parameters:</strong> {params_dct}</p>"
        "<h2>Rolls:</h2>"
    )


def get_response(http_version, response_body: str) -> str:
    """Returns the formatted response headers and body"""
    return (
        f"{http_version} 200 OK\r\n"
        "Content-Type: text/html\r\n"
        f"Content-Length: {len(response_body)}\r\n"
        "\r\n"
        f"{response_body}</body></html>"
    )


def handle_requests(server_socket: socket):
    """Handle requests to the given socket"""
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        request = client_socket.recv(1024).decode()
        if not request or 'favicon.ico' in request:
            client_socket.close()
            continue
        request_line = request.splitlines()[0]
        http_method, path_and_params, http_version = request_line.split(" ")
        path, params_dct = get_path_and_query_params_dct(path_and_params)
        response_body = get_response_body(request_line, http_method,
                                          path, params_dct)
        rolls = int(params_dct.get("rolls", '1'))
        sides = int(params_dct.get("sides", "6"))
        response_body += append_rolls_to_body(rolls, sides)
        response = get_response(http_version, response_body)
        client_socket.sendall(response.encode())
        client_socket.close()


def main():
    """Driver code"""
    with setup_socket(url="localhost", port=3003) as server_socket:
        handle_requests(server_socket)


if __name__ == "__main__":
    main()
