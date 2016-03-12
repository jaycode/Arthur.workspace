"""Create a concept
"""
from argparse import ArgumentParser
from app.mod_cmd.client_instruction import ClientInstruction
from app import app, mongo

def run(project = None, args = [], **kwargs):
    """Create a concept.

    Run without any parameter to begin interactive concept creation.

    Create a concept from given hints, values, and other information.
    On duplicated concepts (i.e. same names) hints, values, regexes, and docs will be updated.

    usage: create_concept [--hints HINTS [HINTS ...]]
                          [--values VALUES [VALUES ...]]
                          [--type {single,list}] [--regex REGEX [REGEX ...]]
                          [--docs DOCS [DOCS ...]]
                          name

    Args:
        name                                                   Name of concept to create. Consider this as a 
                                                               field name in database.
    Optional arguments:
        --hints HINTS [HINTS ...], -h HINTS [HINTS ...]        List of hints for this concept.
        --values VALUES [VALUES ...], -v VALUES [VALUES ...]   List of values for this concept.
        --type {single,multiple}, -t {single,multiple}         How many values to keep for this concept?
        --regex REGEX [REGEX ...], -r REGEX [REGEX ...]        If value is going to be some floating numbers followed by some words,
                                                               for example, add an option -r "([0-9.]*)( *?)(kg)"
        --docs DOCS [DOCS ...], -d DOCS [DOCS ...]             Name of documents this concept was created from.

    """
    if len(args) == 0:
        instruction = ClientInstruction({
            'action': 'startsContextCreation'
        })
    else:
        parser = ArgumentParser(add_help=False)
        parser.add_argument('name')
        parser.add_argument('--hints', '-h', nargs='+')
        parser.add_argument('--values', '-v', nargs='+')
        parser.add_argument('--type', '-t', default='single', choices=['single', 'multiple'])
        parser.add_argument('--regex', '-r', nargs='+')
        parser.add_argument('--docs', '-d', nargs='+')
        parsed_args = parser.parse_args(args)

        user_id = mongo.db.users.find_one({'username': app.session['active_user']},
                                          projection=['_id'])['_id']


        project, instruction = create_concept(project, parsed_args.name, hints=parsed_args.hints,
                                                       values=parsed_args.values, type=parsed_args.type,
                                                       regex=parsed_args.regex, docs=parsed_args.docs)
        context = mongo.db.contexts.update({'user_id': user_id, 'name': parsed_args.name})
    return [project, instruction]

def create_concept(project, name, hints=[], values=[], vtype='single', regex=None, docs=[]):
    """Create a concept and insert it into project.
    """
    project.context.add_concept({
        'name': name,
        'hints': hints,
        'values': values,
        'type': vtype,
        'regex': regex,
        'docs': docs
    })
    instruction = ClientInstruction({
        'pass_context': True,
        'action': 'redrawConcepts()',
        'context': context.to_dict()
    })
    return project, instruction