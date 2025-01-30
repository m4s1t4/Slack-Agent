import os
from dotenv import load_dotenv
from termcolor import colored
from trello import TrelloClient

load_dotenv()


def test_trello_connection():
    try:
        print(colored("Probando conexión con Trello...", "cyan"))

        api_key = os.getenv("TRELLO_API_KEY")
        token = os.getenv("TRELLO_TOKEN")
        api_secret = os.getenv("TRELLO_API_SECRET")
        board_id = os.getenv("BOARD_ID")

        client = TrelloClient(api_key=api_key, api_secret=api_secret, token=token)

        board = client.get_board(board_id)
        print(colored(f"✓ Conexión exitosa! Nombre del tablero: {board.name} {board.id}", "green"))

    except Exception as e:
        print(colored(f"✗ Error de conexión: {str(e)}", "red"))


if __name__ == "__main__":
    test_trello_connection()
