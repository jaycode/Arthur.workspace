"""
Controllers for mod_cmd
"""
import os
import glob
import importlib
from libs.arthur import ArthurProject
from helpers import get_package
import pdb
import sockjs.tornado
import json
from libs.redis_session.for_tornado import Session

class WorkspaceConnection(sockjs.tornado.SockJSConnection):
    """Workspace connection implementation"""
    # Class level variable
    participants = set()

    def write(self, message=''):
        """This method is needed so WorkspaceConnection object can be passed to functions
        that print progress as they run, e.g. :class:`ArthurReader`.
        """

    def on_open(self, info):
        # Todo: Multiple connect not working well. Need to learn SocketJS' behaviors.
        # for participant in self.participants:
        #     if participant.session.conn_info.ip == self.session.conn_info.ip:
        #         self.send("%s has already joined this session." % self.session.conn_info.ip)
        from app import app
        from app.mod_cmd.commands.projects.load_project import load_project
        from app.mod_cmd.commands.docs.list_docs import list_docs
        from client_instruction import ClientInstruction

        session_id = info.cookies.get('session').value
        app.session = Session(app.session_store, session_id)

        app.session['active_user'] = 'default'

        # Send that someone joined
        self.broadcast(self.participants, "%s joined." % self.session.conn_info.ip)

        # Add client to the clients list
        self.participants.add(self)
        if 'active_project' in app.session:
            project, instruction = load_project(app.session['active_user'], app.session['active_project'])
            if project.active_doc == None:
                project, instruction = list_docs(project)
            instruction.set_value('message', "Connected to workspace server.\n\n%s" % instruction.get_value('message'))

            project, instruction = self.pass_other_stuff(project, instruction)

            self.send(instruction.to_json())
        else:
            self.send("Connected to workspace server.")

    def on_message(self, message):
        from app import app
        data = json.loads(message)
        [project, response_msg] = self.run_cmd(data)
        self.broadcast(self.participants, response_msg)

    def on_close(self):
        # Remove client from the clients list and broadcast leave message
        self.participants.remove(self)

        self.broadcast(self.participants, "%s left." % self.session.conn_info.ip)
        self.send("Disconnected from workspace server. Run 'connect' to reconnect.")

    def run_cmd(self, data):
        """Runs the given command.
        """
        from app.mod_cmd.commands.projects.load_project import load_project
        from app import app
        from app.mod_cmd.client_instruction import ClientInstruction
        
        command = data['method']
        params = data['params']

        package = get_package(command)

        project = None
        if 'active_project' in app.session:
            project, _ = load_project(app.session['active_user'], app.session['active_project'])

        if os.path.exists(os.path.join('app', 'mod_cmd', 'commands', package, command+'.py')):
            if package != '':
                package += '.'
            cmd = importlib.import_module("app.mod_cmd.commands.%s%s" % (package, command))
            [project, instruction] = cmd.run(project, params, connection=self)
        else:
            instruction = ClientInstruction({'message': "Command %s not found. Run 'help' to view all available commands." % command})

        project, instruction = self.pass_other_stuff(project, instruction)

        return (project, instruction.to_json())

    def pass_other_stuff(self, project, instruction):
        # If instructed to pass project, fill in "project" key with serialized ArthurProject object.
        if instruction.get_value('pass_project'):
            instruction.set_value('project', project.to_dict())

        return (project, instruction)
