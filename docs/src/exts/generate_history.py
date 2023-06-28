import subprocess
from packaging.version import Version, InvalidVersion


def git_tags():
    proc = subprocess.run(['git', 'tag'], stdout=subprocess.PIPE)
    for tag in proc.stdout.decode().split('\n'):
        if tag.lower().startswith('v'):
            try:
                yield tag, Version(tag)
            except InvalidVersion:
                pass


def git_branch():
    proc = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE)
    return proc.stdout.decode().strip()


def git_commits(since_tag):
    since = '' if since_tag is None else since_tag + '..'
    cmd = ['git', 'log', '--pretty=oneline', since]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE)
    lines = [x for x in proc.stdout.strip().decode().split('\n') if x]
    return len(lines)


def make_directive(current_tag, last_tag, title=None):
    if current_tag is None and last_tag is None:
        revision = r'    :revisions: 100'
    elif last_tag is None:
        revision = r'    :rev-list: %s' % current_tag
    else:
        revision = r'    :rev-list: %s..%s' % (last_tag, current_tag or '')
    if title is None:
        title = current_tag
    directive = [
        title,
        '-' * len(title),
        r'.. git_changelog::',
        r'    :detailed-message-pre: True',
        r'    :filename_filter: LICENSE|.*\.(py|md|rst)',
        revision,
    ]
    return '\n'.join(directive) + '\n'


def make_changelog():
    git_changelog = []
    previous_tag = None

    for tag, version in sorted(git_tags(), key=lambda x: x[1]):
        git_changelog += [make_directive(tag, previous_tag)]
        previous_tag = tag

    git_changelog = '\n'.join(reversed(git_changelog)) + '\n'
    return git_changelog


def make_unreleased():
    tags = sorted(git_tags(), key=lambda x: x[1])
    previous_tag = None if len(tags) == 0 else tags[-1][0]

    if git_commits(since_tag=previous_tag) == 0:
        return ''

    return make_directive(None, previous_tag, title=git_branch())


def replace_directive(text, directive, replace_fn):
    replace_idx = []
    lines = text.split('\n')
    for idx, line in enumerate(lines):
        if directive in line:
            replace_idx.append(idx)

    if not replace_idx:
        return text

    for idx in replace_idx:
        lines[idx] = replace_fn()

    return '\n'.join(lines)


def generate_changelog(app, docname, source):
    if docname == 'history':
        source[0] = replace_directive(source[0], '.. history_changelog::', make_changelog)
        source[0] = replace_directive(source[0], '.. history_unreleased::', make_unreleased)
        lines = []
        for line in map(str.strip, source[0].split('\n')):
            if not line or line[0] in ['.', '-', ':']:
                continue
            lines.append(line)
        print('\n'.join(lines))


def setup(app):
    app.connect("source-read", generate_changelog)
