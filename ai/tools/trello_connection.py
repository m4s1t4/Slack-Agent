import os
from dotenv import load_dotenv
from termcolor import colored
from trello import TrelloClient
from trello.exceptions import Unauthorized, ResourceUnavailable
import time

load_dotenv()

API_KEY = os.getenv("TRELLO_API_KEY")
TOKEN = os.getenv("TRELLO_TOKEN")
API_SECRET = os.getenv("TRELLO_API_SECRET")
BOARD_ID = os.getenv("BOARD_ID")

client = TrelloClient(api_key=API_KEY, api_secret=API_SECRET, token=TOKEN)
board = client.get_board(BOARD_ID)


def verify_credentials():
    try:
        required_vars = {
            "TRELLO_API_KEY": API_KEY,
            "TRELLO_TOKEN": TOKEN,
            "TRELLO_API_SECRET": API_SECRET,
            "BOARD_ID": BOARD_ID,
        }

        print(colored("\nVerificando credenciales:", "cyan"))
        for var_name, value in required_vars.items():
            if value:
                masked_value = value[:4] + "..." if value else "Not set"
                print(colored(f"✓ {var_name}: {masked_value}", "green"))
            else:
                print(colored(f"✗ {var_name}: Not set", "red"))

        missing_vars = [var for var, value in required_vars.items() if not value]
        if missing_vars:
            raise ValueError(f"Faltan las siguientes variables de entorno: {', '.join(missing_vars)}")

    except Exception as e:
        print(colored(f"Error en verify_credentials: {str(e)}", "red"))
        raise


def get_list_id_by_name(list_name):

    try:
        print(colored(f"Buscando lista '{list_name}'...", "cyan"))
        lists = board.list_lists()

        for lst in lists:
            if lst.name.lower() == list_name.lower():
                print(colored(f"✅ Lista encontrada: {lst.name} (ID: {lst.id})", "green"))
                return lst.id, lst.name, lst

        for lst in lists:
            if list_name.lower() in lst.name.lower():
                print(colored(f"✅ Lista encontrada (coincidencia parcial): {lst.name} (ID: {lst.id})", "green"))
                return lst.id, lst.name, lst

        print(colored(f"❌ No se encontró la lista '{list_name}'", "red"))
        print(colored("\nListas disponibles:", "yellow"))
        for lst in lists:
            print(colored(f"• {lst.name} (ID: {lst.id})", "yellow"))
        return None, None, None

    except Exception as e:
        print(colored(f"❌ Error al buscar la lista: {str(e)}", "red"))
        return None, None, None


def get_card_by_name_or_id(card_identifier, list_obj=None):

    try:
        print(colored(f"Buscando tarjeta '{card_identifier}'...", "cyan"))

        if card_identifier.isalnum() and len(card_identifier) > 20:
            try:
                card = client.get_card(card_identifier)
                if card:
                    print(colored(f"✅ Tarjeta encontrada por ID: {card.name}", "green"))
                    return card, card.get_list()
            except:
                pass

        lists_to_search = [list_obj] if list_obj else board.list_lists()

        for lst in lists_to_search:
            for card in lst.list_cards():
                if card.name.lower() == card_identifier.lower():
                    print(colored(f"✅ Tarjeta encontrada: {card.name} (ID: {card.id})", "green"))
                    return card, lst
                elif card_identifier.lower() in card.name.lower():
                    print(colored(f"✅ Tarjeta encontrada (coincidencia parcial): {card.name} (ID: {card.id})", "green"))
                    return card, lst

        print(colored(f"❌ No se encontró la tarjeta '{card_identifier}'", "red"))
        return None, None

    except Exception as e:
        print(colored(f"❌ Error al buscar la tarjeta: {str(e)}", "red"))
        return None, None


def get_trello_board_info():
    try:
        print(colored("Iniciando conexión con Trello...", "cyan"))
        verify_credentials()

        response = []

        response.append("📋 INFORMACIÓN DEL TABLERO")
        response.append(f"Nombre: {board.name}")
        response.append(f"Descripción: {board.description or 'Sin descripción'}")
        response.append(f"URL: {board.url}")

        response.append("\n👥 MIEMBROS DEL TABLERO")
        for member in board.get_members():
            response.append(f"• {member.full_name} ({member.username})")

        response.append("\n📑 LISTAS Y TARJETAS")
        for lst in board.list_lists():
            response.append(f"\n📌 {lst.name}")
            cards = lst.list_cards()
            if not cards:
                response.append("   (No hay tarjetas)")
            for card in cards:
                response.append(f"   • {card.name}")
                if card.description:
                    response.append(f"     Descripción: {card.description}")
                if card.member_ids:
                    members = [board.get_member(member_id).full_name for member_id in card.member_ids]
                    response.append(f"     Asignado a: {', '.join(members)}")
                if card.labels:
                    labels = [f"{label.name or label.color}" for label in card.labels]
                    response.append(f"     Etiquetas: {', '.join(labels)}")
                if card.due_date:
                    response.append(f"     Fecha límite: {card.due_date}")

        return "\n".join(response)

    except Unauthorized as e:
        error_msg = "Error de autorización con Trello. Verifica tus credenciales."
        print(colored(error_msg, "red"))
        return error_msg
    except ResourceUnavailable as e:
        error_msg = "El tablero no está disponible o no existe."
        print(colored(error_msg, "red"))
        return error_msg
    except Exception as e:
        error_msg = f"Error al obtener información del tablero: {str(e)}"
        print(colored(error_msg, "red"))
        return error_msg


def add_card_to_list(list_id, name, description=""):

    try:
        if not name or name.strip() == "":
            raise ValueError("El nombre de la tarjeta no puede estar vacío")

        trello_list = None
        if list_id.isalnum() and len(list_id) > 20:
            trello_list = client.get_list(list_id)

        if not trello_list:
            list_id, trello_list = get_list_id_by_name(list_id)
            if not trello_list:
                return {"success": False, "message": "No se encontró la lista especificada"}

        print(colored(f"Intentando crear tarjeta '{name}' en la lista {trello_list.name}...", "cyan"))

        new_card = trello_list.add_card(name=name, desc=description or "")

        time.sleep(1)

        response = {
            "success": True,
            "message": "✅ Tarjeta creada exitosamente",
            "card": {
                "id": new_card.id,
                "name": new_card.name,
                "list_name": trello_list.name,
                "description": description if description else "",
                "url": new_card.url,
            },
        }

        print(
            colored(
                "\n".join(
                    [
                        "✅ Tarjeta creada exitosamente",
                        f"📌 Lista: {trello_list.name}",
                        f"📝 Tarjeta: {new_card.name}",
                        f"🆔 ID: {new_card.id}",
                        f"🔗 URL: {new_card.url}",
                    ]
                ),
                "green",
            )
        )

        return response

    except Exception as e:
        error_msg = f"❌ Error al crear la tarjeta: {str(e)}"
        print(colored(error_msg, "red"))
        return {"success": False, "message": error_msg}


def delete_card(card_id):

    try:
        card, card_list = get_card_by_name_or_id(card_id)
        if not card:
            return {"success": False, "message": "No se encontró la tarjeta especificada"}

        print(colored(f"Intentando eliminar tarjeta {card.name}...", "cyan"))

        card_info = {"id": card.id, "name": card.name, "list_name": card_list.name}

        card.delete()

        time.sleep(1)

        response = {"success": True, "message": "✅ Tarjeta eliminada exitosamente", "card": card_info}

        print(
            colored(
                "\n".join(
                    [
                        "✅ Tarjeta eliminada exitosamente",
                        f"📝 Tarjeta: {card_info['name']}",
                        f"📌 Lista: {card_info['list_name']}",
                        f"🆔 ID: {card_info['id']}",
                    ]
                ),
                "green",
            )
        )

        return response

    except Exception as e:
        error_msg = f"❌ Error al eliminar la tarjeta: {str(e)}"
        print(colored(error_msg, "red"))
        return {"success": False, "message": error_msg}


def get_list_cards(list_id):

    try:
        trello_list = None
        if list_id.isalnum() and len(list_id) > 20:
            trello_list = client.get_list(list_id)

        if not trello_list:
            list_id, trello_list = get_list_id_by_name(list_id)
            if not trello_list:
                return {
                    "success": False,
                    "message": "No se encontró la lista especificada",
                    "formatted_response": "No se encontró la lista especificada",
                }

        print(colored(f"Obteniendo tarjetas de la lista {trello_list.name}...", "cyan"))
        cards = trello_list.list_cards()

        response = []
        response.append(f"**Lista: {trello_list.name}**")
        response.append(f"ID: {trello_list.id}\n")

        if not cards:
            response.append("(No hay tarjetas en esta lista)")
        else:
            for card in cards:
                response.append(f"* {card.name}")
                response.append(f"  - ID: {card.id}")
                if card.description:
                    response.append(f"  - Descripción: {card.description}")
                if card.member_ids:
                    members = [board.get_member(member_id).full_name for member_id in card.member_ids]
                    response.append(f"  - Asignado a: {', '.join(members)}")
                if card.labels:
                    labels = [f"{label.name or label.color}" for label in card.labels]
                    response.append(f"  - Etiquetas: {', '.join(labels)}")
                if card.due_date:
                    response.append(f"  - Fecha límite: {card.due_date}")
                response.append("")

        result = {
            "success": True,
            "message": f"✅ Se encontraron {len(cards)} tarjetas en la lista {trello_list.name}",
            "list_name": trello_list.name,
            "list_id": trello_list.id,
            "cards_count": len(cards),
            "formatted_response": "\n".join(response),
        }

        print(colored(result["message"], "green"))
        return result

    except Exception as e:
        error_msg = f"❌ Error al obtener las tarjetas: {str(e)}"
        print(colored(error_msg, "red"))
        return {"success": False, "message": error_msg, "formatted_response": error_msg}


def search_card_descriptions(search_term):
    """
    Busca un término específico en las descripciones de todas las tarjetas del tablero.

    Args:
        search_term (str): Término a buscar en las descripciones de las tarjetas

    Returns:
        list: Lista de diccionarios con la información de las tarjetas que coinciden con la búsqueda
    """
    try:
        print(colored(f"Buscando '{search_term}' en las descripciones de las tarjetas...", "cyan"))
        results = []

        for lst in board.list_lists():
            for card in lst.list_cards():
                if card.description and search_term.lower() in card.description.lower():
                    card_info = {
                        "card_id": card.id,
                        "card_name": card.name,
                        "description": card.description,
                        "list_name": lst.name,
                        "url": card.url,
                    }
                    results.append(card_info)
                    print(colored(f"✅ Coincidencia encontrada en lista '{lst.name}', tarjeta '{card.name}'", "green"))

        if not results:
            print(colored(f"❌ No se encontraron tarjetas con '{search_term}' en su descripción", "yellow"))

        return results

    except Exception as e:
        error_msg = f"Error al buscar en las descripciones: {str(e)}"
        print(colored(error_msg, "red"))
        return []


def get_latest_card():
    """
    Obtiene la información de la última tarjeta agregada al tablero de Trello.

    Returns:
        dict: Diccionario con la información de la tarjeta más reciente
              - card_name: Nombre de la tarjeta
              - description: Descripción de la tarjeta
              - created_date: Fecha de creación
              - list_name: Nombre de la lista donde se encuentra
    """
    try:
        print(colored("Buscando la última tarjeta agregada...", "cyan"))
        latest_card = None
        latest_card_date = None
        card_list = None

        for lst in board.list_lists():
            for card in lst.list_cards():
                card_date = card.created_date
                if latest_card_date is None or card_date > latest_card_date:
                    latest_card = card
                    latest_card_date = card_date
                    card_list = lst

        if latest_card:
            result = {
                "success": True,
                "message": "✅ Última tarjeta encontrada",
                "card_info": {
                    "card_name": latest_card.name,
                    "description": latest_card.description or "Sin descripción",
                    "list_name": card_list.name,
                    "url": latest_card.url,
                    "created_date": (
                        latest_card_date.strftime("%Y-%m-%d %H:%M:%S") if latest_card_date else "Fecha no disponible"
                    ),
                },
            }
            print(
                colored(
                    "\n".join(
                        [
                            "✅ Última tarjeta encontrada:",
                            f"📝 Nombre: {latest_card.name}",
                            f"📌 Lista: {card_list.name}",
                            f"📅 Fecha: {result['card_info']['created_date']}",
                            f"🔗 URL: {latest_card.url}",
                        ]
                    ),
                    "green",
                )
            )
            return result
        else:
            result = {"success": False, "message": "❌ No se encontraron tarjetas en el tablero", "card_info": None}
            print(colored(result["message"], "yellow"))
            return result

    except Exception as e:
        error_msg = f"Error al buscar la última tarjeta: {str(e)}"
        print(colored(error_msg, "red"))
        return {"success": False, "message": error_msg, "card_info": None}
