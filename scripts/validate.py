"""Check the skill layout: skills/<category>/<skill>/SKILL.md, frontmatter name == folder, README row per skill."""
from pathlib import Path
import argparse
import re
import sys
import tempfile

KEBAB = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*')
FRONTMATTER = re.compile(r'\A---\r?\n(.*?)\r?\n---\r?\n', re.S)


def field(frontmatter, key):
    match = re.search(rf'^{key}:[ \t]*(.*?)[ \t]*$', frontmatter, re.M)
    return match.group(1).strip('\'"') if match else ''


def check(root):
    skills_dir = root / 'skills'
    errors, seen = [], {}
    for skill_md in skills_dir.rglob('SKILL.md'):
        rel = skill_md.relative_to(skills_dir)
        if len(rel.parts) != 3:
            errors.append(f'SKILL.md at wrong depth, expected skills/<category>/<skill>/SKILL.md: {rel.as_posix()}')
    for category in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        for folder in sorted(p for p in category.iterdir() if p.is_dir()):
            rel = folder.relative_to(root).as_posix()
            for part in (category.name, folder.name):
                if not KEBAB.fullmatch(part):
                    errors.append(f'{rel}: "{part}" is not kebab-case')
            skill_md = folder / 'SKILL.md'
            if not skill_md.is_file():
                errors.append(f'{rel}: missing SKILL.md')
                continue
            match = FRONTMATTER.match(skill_md.read_text(encoding='utf-8'))
            if not match:
                errors.append(f'{rel}: SKILL.md has no frontmatter block')
                continue
            if field(match.group(1), 'name') != folder.name:
                errors.append(f'{rel}: frontmatter name must equal the folder name "{folder.name}"')
            if not field(match.group(1), 'description'):
                errors.append(f'{rel}: frontmatter description is empty')
            if folder.name in seen:
                errors.append(f'{rel}: duplicate skill name, also in {seen[folder.name]}')
            seen[folder.name] = rel
    readme = (root / 'README.md').read_text(encoding='utf-8') if (root / 'README.md').is_file() else ''
    for name in seen:
        if f'| `{name}` |' not in readme:
            errors.append(f'README.md has no table row for `{name}`')
    return errors


def _write(root, rel, text):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def _skill(name, description='Does a thing.'):
    return f'---\nname: {name}\ndescription: {description}\n---\n\nBody.\n'


def self_test():
    def fixture(directory):
        root = Path(directory)
        _write(root, 'README.md', '| `alpha` | media |\n| `beta` | engineering |\n')
        _write(root, 'skills/media/alpha/SKILL.md', _skill('alpha'))
        _write(root, 'skills/engineering/beta/SKILL.md', _skill('beta'))
        return root

    def expect(mutate, fragment):
        with tempfile.TemporaryDirectory() as directory:
            root = fixture(directory)
            mutate(root)
            errors = check(root)
            assert any(fragment in e for e in errors), (fragment, errors)

    with tempfile.TemporaryDirectory() as directory:
        assert check(fixture(directory)) == [], check(fixture(directory))

    expect(lambda r: _write(r, 'skills/media/alpha/SKILL.md', _skill('other')), 'name')
    expect(lambda r: _write(r, 'skills/media/alpha/SKILL.md', _skill('alpha', '')), 'description')
    expect(lambda r: _write(r, 'skills/media/alpha/SKILL.md', 'name: alpha\n'), 'frontmatter')
    expect(lambda r: _write(r, 'skills/media/gamma/notes.md', 'x'), 'missing SKILL.md')
    expect(lambda r: _write(r, 'skills/delta/SKILL.md', _skill('delta')), 'depth')
    expect(lambda r: _write(r, 'skills/media/Bad_Name/SKILL.md', _skill('Bad_Name')), 'kebab-case')
    expect(lambda r: _write(r, 'skills/engineering/alpha/SKILL.md', _skill('alpha')), 'duplicate')
    expect(lambda r: _write(r, 'README.md', '| `alpha` | media |\n'), 'README')
    print('PASS: valid layout; wrong name, empty description, missing frontmatter, missing SKILL.md, wrong depth, '
          'non-kebab name, duplicate name, missing README row all fail')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    if args.self_test:
        self_test()
    else:
        problems = check(args.root)
        for problem in problems:
            print(f'FAIL: {problem}')
        print('OK' if not problems else f'{len(problems)} problem(s)')
        sys.exit(1 if problems else 0)
