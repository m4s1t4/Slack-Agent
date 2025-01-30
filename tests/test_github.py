import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from ai.tools.github_connection import (
    get_github_instance,
    list_branches,
    list_user_repos,
    print_repo_contents,
    show_commit_history,
)


load_dotenv()

USERNAME = os.getenv("GITHUB_USER")
TOKEN = os.getenv("GITHUB_TOKEN")


def main():
    g = get_github_instance()

    try:
        username = os.getenv("GITHUB_USER")
        if not username:
            print("🚨 Error: El usuario debe estar en el archivo .env como GITHUB_USER")
            sys.exit(1)

        user = g.get_user(username)
        repo = None

        while True:
            print("\n" + "=" * 50)
            print("🐙 GitHub Repository Explorer")
            print("=" * 50)
            print("1. Listar todos mis repositorios")
            print("2. Inspeccionar un repositorio")
            print("3. Salir")

            choice = input("\nSelecciona una opción (1-3): ").strip()

            if choice == "1":
                list_user_repos(user)

            elif choice == "2":
                repo_name = input("\nIngresa el nombre del repositorio: ").strip()
                repo = user.get_repo(repo_name)

                while True:
                    print("\n" + "=" * 50)
                    print(f"📦 Repositorio seleccionado: {repo.name}")
                    print("=" * 50)
                    print("1. Ver contenido del repositorio")
                    print("2. Listar ramas")
                    print("3. Ver historial de commits")
                    print("4. Volver al menú principal")

                    sub_choice = input("\nSelecciona una opción (1-4): ").strip()

                    if sub_choice == "1":
                        print("\n📂 Contenido del repositorio:")
                        print_repo_contents(repo)

                    elif sub_choice == "2":
                        list_branches(repo)

                    elif sub_choice == "3":
                        limit = input("¿Cuántos commits quieres ver? (default 30): ").strip()
                        show_commit_history(repo, int(limit) if limit.isdigit() else 30)

                    elif sub_choice == "4":
                        break

                    else:
                        print("\n❌ Opción inválida, intenta nuevamente")

            elif choice == "3":
                print("\n👋 ¡Hasta luego!")
                break

            else:
                print("\n❌ Opción inválida, intenta nuevamente")

    except Exception as e:
        print(f"\n🚨 Error: {e}")
    finally:
        g.close()


if __name__ == "__main__":
    main()
