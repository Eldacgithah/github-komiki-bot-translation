from github import Auth, Github
from github import GithubException


def create_webhook(host: str, endpoint: str, gh_token: str, integration: str):
    """
    🔗 Создаёт webhook для указанного репозитория.
    Это программный способ создания webhook через PyGithub API.
    Можно сделать вручную в разделе "Settings" репозитория на GitHub.
    """

    config = {
        "url": f"{host}webhook/{endpoint}",
        "content_type": "json",
    }
    try:
        auth = Auth.Token(gh_token)
        g = Github(auth=auth)
    except GithubException as e:
        return {"message": "❌ Ошибка аутентификации в Github, возможно токен устарел.", "error": e.data}

    events = ["push", "pull_request", "issues", "fork", "star"]

    try:
        repo = g.get_repo(integration)
        repo.create_hook("web", config, events, active=True)
    except GithubException as e:
        return {"message": "❌ Ошибка при создании webhook, проверьте права токена.", "error": e.data}


def validate(token: str):
    """
    ✅ Валидирует указанный Github токен.
    Можно сделать вручную в разделе "Settings" на GitHub.
    """

    if not token.startswith("ghp_"):
        return False

    try:
        auth = Auth.Token(token)
        g = Github(auth=auth)
    except GithubException:
        return False

    try:
        g.get_repo("vsecoder/github-notifi-bot")
    except GithubException:
        return False

    return True


def get_repos(token: str):
    """
    📜 Возвращает список репозиториев пользователя.
    Использует PyGithub API.
    """

    try:
        auth = Auth.Token(token)
        g = Github(auth=auth)
    except GithubException as e:
        return {"message": "❌ Ошибка аутентификации в Github.", "error": e.data}

    try:
        repos = g.get_user().get_repos()
    except GithubException as e:
        return {"message": "❌ Ошибка получения репозиториев.", "error": e.data}

    return repos


def check_repo(token: str, repo: str):
    """
    🔍 Проверяет существование репозитория пользователя.
    """

    try:
        auth = Auth.Token(token)
        g = Github(auth=auth)
    except GithubException as e:
        return {"message": "❌ Ошибка аутентификации в Github.", "error": e.data}

    try:
        repos = g.get_repo(repo)
    except GithubException as e:
        return {"message": "❌ Ошибка получения репозитория.", "error": e.data}

    return repos
