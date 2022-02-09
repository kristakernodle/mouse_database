from database_pkg import Experiment, Session, Reviewer, BlindFolder
from pathlib import Path

experiment = Experiment.get_by_name('dlxCKO-skilled-reaching')
#
# sessions_wrong_path = list(
#     Session.query.filter(Session.experiment_id == experiment.experiment_id)
#         .filter(Session.session_dir.like('/Volumes/SharedX/Neuro-Leventhal/data/mouseSkilledreaching/%')))
#
# folders_to_inspect = list()
# for session in sessions_wrong_path:
#     if len(Session.query.filter(Session.session_dir.ilike(session.session_dir)).all()) > 1:
#         for folder in session.folders:
#             if len(folder.score_folders) == 0:
#                 for trial in folder.trials:
#                     trial.remove_from_db()
#                 folder.remove_from_db()
#             else:
#                 folders_to_inspect.append(folder)
#                 continue
#
#         if len(session.folders) == 0:
#             session.remove_from_db()
#
# print(folders_to_inspect)


reviewer_name='Krista K'
first_name, last_name = reviewer_name.split(' ')
reviewer = Reviewer.query.filter_by(first_name=first_name, last_name=last_name).first()

for blind_path in Path(reviewer.toScore_dir).glob('*'):
    if '.DS_Store' in blind_path.stem:
        continue

    blind_folder = BlindFolder.query.filter_by(blind_name=blind_path.stem).first()
    if blind_folder is None:
        for path in blind_path.glob('*'):
            path.unlink()
        blind_path.rmdir()

