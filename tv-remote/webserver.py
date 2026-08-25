from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


HOST = "0.0.0.0"
PORT = 8000


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


def main():
    server = ThreadingHTTPServer(
        (HOST, PORT),
        QuietHandler,
    )

    server.serve_forever()


if __name__ == "__main__":
    main()