# MIT License
#
# Copyright (c) [2024] [Diego Carrasco G.]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from nikola.plugin_categories import ShortcodePlugin
from github import Github
# Authentication is defined via github.Auth
from github import Auth
from github.GithubException import UnknownObjectException


def render_github_widget(repo_data, show_avatar, max_width, latest_release_bool, latest_commit_bool):
    image_url = repo_data.owner.avatar_url if show_avatar else "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"

    latest_activity_html = ""

    if latest_commit_bool:
        # Get the latest commit
        latest_commit = repo_data.get_commits()[0]
        if latest_commit:
            latest_activity_html += f"<p><strong>Latest Commit:</strong> {latest_commit.commit.message} ({latest_commit.commit.author.date})</p>"

    if latest_release_bool:
        try:
            # Get the latest release if exists, if not there will be a 404 error
            latest_release = repo_data.get_latest_release()

            if latest_release:
                latest_activity_html += f"<p><strong>Latest Release:</strong> {latest_release.title} - {latest_release.body} ({latest_release.created_at})</p>"
        except UnknownObjectException:
            pass

    widget_html = f"""
    <div class="github-widget" style="max-width: {max_width};">
        <div class="github-widget-image">
            <a href="{repo_data.html_url}" target="_blank">
                <img src="{image_url}" alt="{repo_data.owner}" max-width="50" max-height="50">
            </a>
        </div>
        <div class="repo-info">
            <a href="{repo_data.html_url}" target="_blank">
                <h3>{repo_data.name}</h3>
            </a>
            <p>{repo_data.description}</p>
            <p><strong>Languages:</strong> {repo_data.language}</p>
            <ul>
                <li>⭐ Stars: {repo_data.stargazers_count}</li>
                <li><svg aria-hidden="true" height="16" viewBox="0 0 16 16" version="1.1" width="16" data-view-component="true" class="octicon octicon-git-branch UnderlineNav-octicon">
    <path d="M9.5 3.25a2.25 2.25 0 1 1 3 2.122V6A2.5 2.5 0 0 1 10 8.5H6a1 1 0 0 0-1 1v1.128a2.251 2.251 0 1 1-1.5 0V5.372a2.25 2.25 0 1 1 1.5 0v1.836A2.493 2.493 0 0 1 6 7h4a1 1 0 0 0 1-1v-.628A2.25 2.25 0 0 1 9.5 3.25Zm-6 0a.75.75 0 1 0 1.5 0 .75.75 0 0 0-1.5 0Zm8.25-.75a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5ZM4.25 12a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5Z"></path>
</svg> Forks: {repo_data.forks_count}</li>
                <li>👁 Watchers: {repo_data.subscribers_count}</li>
                <li>❗ Open Issues: {repo_data.open_issues_count}</li>
            </ul>
            {latest_activity_html}
        </div>
    </div>
    """
    return widget_html


class GitHubWidgetPlugin(ShortcodePlugin):
    name = "github_widget"

    def handler(self, **kwargs):
        data = kwargs.get('data', '').strip().split()
        repo = data[0]
        show_avatar = kwargs.get('avatar', False)
        max_width = kwargs.get('max_width', '100%')
        latest_release_bool = kwargs.get('latest_release', False)
        latest_commit_bool = kwargs.get('latest_commit', False)

        token = self.site.config.get('GITHUB_API_TOKEN')

        if token:
            # using an access token
            auth = Auth.Token(token)
            g = Github(auth=auth)
        else:
            g = Github()  # without token there will be api rate limits.

        repo_data = g.get_repo(repo)

        if repo_data:
            return render_github_widget(repo_data, show_avatar, max_width, latest_release_bool, latest_commit_bool), []
        else:
            return f"<p>Repository '{repo}' not found or an error occurred.</p>", []
