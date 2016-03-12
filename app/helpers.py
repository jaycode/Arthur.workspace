from app import app, mongo
import os

def user_logged_in():
    """Checks if user logged in.
    """
    if 'active_user' not in app.session:
        return False
    username = app.session['active_user']
    return mongo.db.users.count({'username': username}) > 0

def user_path():
    """Returns user's path (/user_data/active_user)
    """
    return os.path.join(app.config['BASE_DIR'], 'user_data', app.session['active_user'])

def docs_path():
    """Returns path to a project's docs.zip file (where all documents for that project are stored).
    """
    return os.path.join(user_path(), app.session['active_project'], 'docs.zip')

def uploaded_path():
    """Returns path to a user's (temporary) uploaded directory.
    """
    return os.path.join(user_path(), '_uploaded')

def corpus_path():
    return os.path.join(user_path(), app.session['active_project'], 'corpus')

def save_project(project):
    """Shallow saves project to mongodb database.

    WARNING: Saving method is shallow, meaning it does not update deep nested data like
             projects.docs and projects blocks - These should be inserted one by one, otherwise
             it takes too much memory.
    """
    active_doc_name = None
    if project.active_doc is not None:
        active_doc_name = project.active_doc.name

    doclist = []
    for doc in project.docs:
        docdict = doc.to_dict(raw=False, with_details=False)
        docdict.pop('project_id', None)
        doclist.append(docdict)

    mongo.db.users.update(
        {'username': app.session['active_user'], 'projects._id': project._id},
        {
            '$set': {
                'projects.$.name': project.name,
                'projects.$.active_doc': active_doc_name,
                'projects.$.docs': doclist
            }
        }
    )
