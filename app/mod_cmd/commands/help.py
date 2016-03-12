"""Help command
"""
import imp
import pdb
import os
import importlib
from itertools import chain
from app.mod_cmd.client_instruction import ClientInstruction
from app.mod_cmd.helpers import get_package_module_pairs, get_base_package_module_pairs, get_package

def run(project=None, args=[], **kwargs):
    """Show all available console commands. `help [command]` to show detailed help for a command.
    """
    cmd = None
    message = "Below are the commands available, grouped by their functions.\n\n%s\n\nOther useful commands:\n" \
    "\tCTRL + L: Clear console.\n" \
    "\tALT + +: Maximize console size.\n" \
    "\tALT + -: Hide console.\n" \
    "\tALT + 0: Standard console size."
    if project is None:
        message += "\n\nLet's start by loading a prepared project. Try 'load_project risky'.\n" \
        "Tips: Run 'status' whenever you need to figure out where you're at, and run 'help' "\
        "whenever you need suggestion on what to do next"
    else:
        if project.context == None or 'concepts' not in project.context or len(project.context['concepts']) == 0:
            if project.active_doc == None:
                message += "\n\nProject %s is currently active. " \
                    "In the main screen, you should see all documents in this project with their status.\n" \
                    "Basically, the idea of this app is to keep all important information from documents to database.\n" \
                    "This is done by creating concepts, which is done as you label a couple of few documents then let Arthur\n" \
                    "learns the rest of documents in this project.\n" \
                    "Try loading a project by choosing from listed document." % project.name
            else:
                message += "To create a concept, run command 'create_concept'"
        else:
            message += "Now that concept(s) has been created, you can extract features and targets from documents.\n" \
                       "Run a dry-run extraction (i.e. not actually affecting the database) for an active document with command " \
                       " 'extract' (remember to load_doc to activate a document).\n" \
                       "When all seems good, 'extract --all' or 'extract -n [number]' can be run to extract features and targets for real."
    if len(args) > 0:
        cmd = args[0]
        message = "%s"
    docs = get_docs(cmd)
    instruction = ClientInstruction({
        'message': message % "\n".join(docs)
    })
    return [project, instruction]

def get_docs(cmd = None):
    """Get all the available modules and return their documentations. This method will find scripts
       inside another directory under `app/commands` directory.
    """
    docs = []
    if cmd is None:
        last_package = ''
        for package, module in chain(get_package_module_pairs(), get_base_package_module_pairs()):
            if package != last_package:
                if package == 'commands':
                    docs.append('others:')
                else:
                    docs.append(package+':')
            last_package = package

            if package == 'commands':
                package = ''
            if package != '':
                package += '.'
            mod = importlib.import_module("app.mod_cmd.commands.%s%s" % (package, module))
            docs.append(("\t%s: %s" % (module, mod.run.__doc__.split('\n', 1)[0].strip())))
    else:
        package = get_package(cmd)
        if package != '':
            package += '.'
        mod = importlib.import_module("app.mod_cmd.commands.%s%s" % (package, cmd))
        docs.append(("%s\n%s" % (cmd, mod.run.__doc__)).strip())

    return docs