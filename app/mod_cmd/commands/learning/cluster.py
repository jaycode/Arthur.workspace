"""Cluster document elements.
"""
from app.mod_cmd.client_instruction import ClientInstruction
from libs.arthur.learner import get_clustering_algorithms, get_clusterer_class
from libs.arthur.reader import read
import os
import config
from app.helpers import user_path
from app import app, mongo
from bson import ObjectId

def run(project = None, args = [], connection = None, **kwargs):
    """Cluster elements in active document.

    cluster [algorithm]

    Pass no argument to list all available clustering algorithms.

    Args:
        algorithm: Algorithm name to cluster document with.
    """

    if len(args) > 0:
        try:
            clusterer_class = get_clusterer_class(args[0])
        except IOError as e:
            instruction = ClientInstruction({'message': "Clusterer '%s' not found. Run 'cluster' to view all available clusterers." % args[0]})

        # Try to find list of mwes (multi-word expressions) from database, and setup clusterer when not found.
        user_id = mongo.db.users.find_one({'username': app.session['active_user']}, ['_id'])
        query = {'user_id': user_id, 'project_id': ObjectId(project._id)}

        # Todo: Use either user's or project's path, still undecided for now...
        corpus_dir = os.path.join(config.BASE_DIR, 'exploration', 'corpus')
        clusterer = clusterer_class(corpus_dir=corpus_dir, setup_mwes=False)
        if mongo.db.mwes.count(query) == 0:         
            mwes = clusterer.setup_mwes(trigram_nbest=1000, bigram_nbest=30000)
            inserted_ids = mongo.db.mwes.insert_many([{'user_id': user_id, 'project_id': ObjectId(project._id), 'value': mwe} for mwe in mwes]).inserted_ids
            connection.send("Inserted %i multi-word expressions (MWEs)." % len(inserted_ids))
        else:
            mwes =  mongo.db.mwes.find(query, ['value'])
            count = 0
            for mwe in mwes:
                clusterer.mwes.append(mwe['value'])
                count += 1
            connection.send("Loaded %i multi-word expressions (MWEs)." % count)
        connection.send("Applying MWEs to document...")

        data_fields = read(project.active_doc, clusterer, project_id=project._id)
        instruction = ClientInstruction({
            'message': 'Clustering done',
            'pass_project': True,
            'data_fields': data_fields,
            'page': '#doc-view'
        })
    else:
        algos = get_clustering_algorithms()
        algos_str = "\n".join(algos)
        instruction = ClientInstruction({'message': "Choose any of the clustering algorithms below (by command `cluster [algorithm]`):\n%s" % algos_str})
    return (project, instruction)
