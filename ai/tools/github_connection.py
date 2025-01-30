from github import Github
from github import Auth
import os
import sys
from dotenv import load_dotenv
from termcolor import colored

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")


def get_github_instance():
    if not TOKEN:
        print(colored("🚨 Error: El token debe estar en el archivo .env como GITHUB_TOKEN", "red"))
        sys.exit(1)
    return Github(TOKEN)


g = get_github_instance()
user = g.get_user()


def list_user_repos(**kwargs):

    try:
        response = []
        response.append(f"\n📦 Repositorios de {user.login}:")

        for repo in user.get_repos():
            response.append(f"\n🔍 Nombre: {repo.name}")
            response.append(f"   📌 Privacidad: {'🔒 Privado' if repo.private else '🌍 Público'}")
            response.append(f"   📝 Descripción: {repo.description or 'Sin descripción'}")
            response.append(f"   ⭐ Stars: {repo.stargazers_count}")
            response.append(f"   🕒 Última actualización: {repo.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
            response.append(f"   🔗 URL: {repo.html_url}")

        response.append("\n" + "=" * 50)
        result = "\n".join(response)
        print(colored(result, "green"))
        return result

    except Exception as e:
        error_msg = f"Error al obtener repositorios: {str(e)}"
        print(colored(error_msg, "red"))
        return error_msg


def print_repo_contents(repo_name, path="", level=0, **kwargs):

    try:
        try:
            level = int(level)
        except (ValueError, TypeError):
            level = 0
        if not repo_name:
            error_msg = "Error: Debe especificar el nombre del repositorio"
            print(colored(error_msg, "red"))
            return error_msg

        if not isinstance(path, str):
            path = ""

        print(colored(f"Buscando repositorio '{repo_name}'...", "cyan"))
        try:
            repo = user.get_repo(repo_name)
        except Exception as e:
            error_msg = f"Error: No se encontró el repositorio '{repo_name}'. Verifica que el nombre sea correcto."
            print(colored(error_msg, "red"))
            return error_msg

        response = []
        response.append(f"\n📂 Contenido de {repo_name} en {path or 'raíz'}:")

        try:
            contents = repo.get_contents(path)
            if not contents:
                response.append("   (El directorio está vacío)")
            else:
                for content in contents:
                    prefix = "  " * level
                    if content.type == "dir":
                        response.append(f"{prefix}📁 {content.name}/")
                    else:
                        response.append(f"{prefix}📄 {content.name}")

            result = "\n".join(response)
            print(colored(result, "green"))
            return result

        except Exception as e:
            error_msg = f"Error al acceder a la ruta '{path}': {str(e)}"
            print(colored(error_msg, "red"))
            return error_msg

    except Exception as e:
        error_msg = f"Error al obtener contenido del repositorio: {str(e)}"
        print(colored(error_msg, "red"))
        return error_msg


def list_branches(repo_name, **kwargs):

    try:
        if not repo_name:
            error_msg = "Error: Debe especificar el nombre del repositorio"
            print(colored(error_msg, "red"))
            return error_msg

        print(colored(f"Buscando repositorio '{repo_name}'...", "cyan"))
        try:
            repo = user.get_repo(repo_name)
        except Exception as e:
            error_msg = f"Error: No se encontró el repositorio '{repo_name}'. Verifica que el nombre sea correcto."
            print(colored(error_msg, "red"))
            return error_msg

        response = []
        response.append(f"\n🌿 Ramas en {repo_name}:")

        branches = list(repo.get_branches())
        if not branches:
            response.append("  • No hay ramas en este repositorio")
        else:
            for branch in branches:
                response.append(f"  • {branch.name}")

        result = "\n".join(response)
        print(colored(result, "green"))
        return result

    except Exception as e:
        error_msg = f"Error al obtener ramas: {str(e)}"
        print(colored(error_msg, "red"))
        return error_msg


def show_commit_history(repo_name, limit=30):

    try:
        repo = user.get_repo(repo_name)
        commits = repo.get_commits()
        response = []
        response.append(f"\n📜 Últimos {limit} commits en {repo_name}:")

        for commit in commits[:limit]:
            commit_date = commit.commit.author.date.strftime("%Y-%m-%d %H:%M:%S")
            response.append(f"\n🔹 {commit.sha[:7]} - {commit.commit.author.name}")
            response.append(f"   📅 {commit_date}")
            response.append(f"   📝 {commit.commit.message.splitlines()[0]}")
            response.append(f"   🔗 {commit.html_url}")

        result = "\n".join(response)
        print(colored(result, "green"))
        return result

    except Exception as e:
        error_msg = f"Error al obtener commits: {str(e)}"
        print(colored(error_msg, "red"))
        return error_msg
