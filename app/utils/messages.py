from github import Auth, Github
from html import escape as _


def commit_message(res, user_token):
    auth = Auth.Token(user_token)
    g = Github(auth=auth)

    repo = g.get_repo(res["repository"]["full_name"])

    if not res["commits"]:
        return f"""<b>📏 На <a href="{res["repository"]["html_url"]}">{res["repository"]["full_name"]}:{res["ref"].split("/")[-1]}</a> новый пустой push</b>"""

    commits_info = []
    for commit_data in res["commits"]:
        commit = repo.get_commit(commit_data["id"])

        diff = commit.files
        modified_files = [file.filename for file in diff if file.status == "modified"]
        created_files = [file.filename for file in diff if file.status == "added"]
        removed_files = [file.filename for file in diff if file.status == "removed"]

        modified = "\n".join(modified_files)
        created = "\n".join(created_files)
        removed = "\n".join(removed_files)

        added_lines, removed_lines = 0, 0
        for file in diff:
            added_lines += file.additions
            removed_lines += file.deletions

        commit_message = f"""
<blockquote>
<b>🔨 Commit <a href="{commit_data["url"]}">#{commit_data["id"][:7]}</a></b>
<b>Автор:</b> <i>{commit_data["author"]["name"]} (<a href="https://github.com/{commit_data["author"]["username"]}">@{commit_data["author"]["username"]}</a>)</i>
<blockquote><i>{_(commit_data["message"])}</i></blockquote>
"""

        if created:
            commit_message += f"""
<b>➕ Созданные файлы:</b>
<code>{created}</code>
"""

        if removed:
            commit_message += f"""
<b>🗑 Удалённые файлы:</b>
<code>{removed}</code>
"""

        if modified:
            commit_message += f"""
<b>🖊 Изменённые файлы:</b>
<code>{modified}</code>
"""

        if added_lines or removed_lines:
            commit_message += f"""
<b>⌨️ Изменения:</b>
➕ {added_lines} строк
➖ {removed_lines} строк
"""

        commit_message += "</blockquote>"
        commits_info.append(commit_message)

    message = f"""
<b>📏 На <a href="{res["repository"]["html_url"]}">{res["repository"]["full_name"]}:{res["ref"].split("/")[-1]}</a> новые коммиты!</b>
<b>Всего коммитов:</b> {len(res["commits"])}
<a href="{res["compare"]}">Сравнить изменения</a>

<blockquote>
{''.join(commits_info)}
</blockquote>
"""

    return message


def issue_message(res):
    return f"""
<b>📌 На <a href="{res['issue']['html_url']}">{res["repository"]["full_name"]}</a> {res["action"]} issue!</b>
<blockquote><b>Заголовок:</b> <i>{_(res["issue"]["title"])}</i></blockquote>
<b>Ссылка:</b> <a href="{res["issue"]["html_url"]}">#{res["issue"]["number"]}</a>
<b>Автор:</b> <a href="{res["sender"]["html_url"]}"><i>@{res["issue"]["user"]["login"]}</i></a>
"""


def star_message(res):
    return f"""
<b>⭐️ На <a href="{res['repository']['html_url']}">{res["repository"]["full_name"]}</a> {"добавлена" if res["action"] == "created" else "удалена"} звезда!</b>
<blockquote><b>Всего звёзд:</b> <i>{res["repository"]["stargazers_count"]}</i></blockquote>
<b>Пользователь:</b> <a href="{res["sender"]["html_url"]}"><i>@{res["sender"]["login"]}</i></a>
"""


def ping_message(res):
    return f"""
<b>🏓 Репозиторий <i>{res["repository"]["full_name"]}</i> подключён и отправил ping!</b>
"""


def pull_request_message(res):
    body = res["pull_request"]["body"] if res["pull_request"]["body"] else "Нет описания"

    if len(body) > 200:
        body = body[:200] + "..."

    return f"""
<b>📝 На <a href="{res['repository']['html_url']}">{res["repository"]["full_name"]}</a> {res["action"]} pull request!</b>
<blockquote><b>Название:</b> <i>{res["pull_request"]["title"]}</i></blockquote>
<blockquote expandable="expandable"><i>{_(body)}</i></blockquote>
<b>Автор:</b> <a href="{res["sender"]["html_url"]}"><i>@{res["pull_request"]["user"]["login"]}</i></a>
<b>Ссылка:</b> <a href="{res["pull_request"]["html_url"]}">#{res["pull_request"]["number"]}</a>
"""


def create_message(res):
    return f"""
<b>🖇 На <a href="{res['repository']['html_url']}">{res["repository"]["full_name"]}</a> создан <b>{res["ref_type"]}</b> <b>{res["ref"]}</b></b>
"""


def fork_message(res):
    return f"""
<b>🍴 <a href="{res['repository']['html_url']}">{res["repository"]["full_name"]}</a> сделан форк</b>
<blockquote><b>Всего форков:</b> <code>{res["repository"]["forks"]}</code></blockquote>
<b>Ссылка на форк:</b> <a href="{res["forkee"]["html_url"]}">{res["forkee"]["full_name"]}</a>
"""
