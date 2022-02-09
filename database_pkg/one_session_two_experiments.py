from database_pkg import Reviewer, Experiment, Session, ChatSapSession, Folder, Trial, BlindFolder, BlindTrial
from database_pkg.utilities import random_string_generator
from pathlib import Path
import shutil

sr_exp = Experiment.get_by_name('dlxCKO-skilled-reaching')
chatsap_exp = Experiment.get_by_name('dlxCKO-chatSap-skilled-reaching')


exp_session_ids = [('0dc83134-97f5-40d4-98bb-e7797686f8ee', '7d761c04-0d62-4108-b91e-e8f68b11f77e'),
                      ('22af6b8a-1562-48fb-9031-2b3f671f2d66', '595ab5df-c46d-44f1-a12a-465a24dd608e'),
                      ('5f06e1df-8425-4dc0-8bc3-186c6fb1e145', 'fe46d8c8-3cb6-41a5-a6d6-d54194a766eb'),
                      ('02bf8d78-13a2-44b8-92e2-dfc5ed2ec30a', '489858df-1831-4b3e-a15e-c5b3df01c7a7'),
                      ('9ead7a04-dedb-4e03-801b-1d17a40dd80e', 'e193ff6e-2474-4179-8160-dd20c1fddac1')]

session_folders = {
    '0dc83134-97f5-40d4-98bb-e7797686f8ee': {'Reaches01': '03dc2ce8-14ab-4f24-9813-92a09bc6f704',
                                          'Reaches02': '8af653f6-b323-4e0d-b24b-b4910c7ed121',
                                          'Reaches03': 'fef3a8ae-33f1-40ee-be7e-efd1b414b739'},
    '7d761c04-0d62-4108-b91e-e8f68b11f77e': {'Reaches01': '46f38df4-e53e-4319-b69f-18b63cd9bcc6',
                                          'Reaches02': '9da0b414-d845-4f27-aff9-7623eeb778d2',
                                          'Reaches03': 'ce277a67-5ce0-495d-b4c0-d8960377ee42'},
    '22af6b8a-1562-48fb-9031-2b3f671f2d66': {'Reaches01': 'd1a25469-21c3-45a2-b7e7-d6801b75fa0e',
                                          'Reaches02': '9d472589-6b2d-4a5a-8f80-f8fb1074a768',
                                          'Reaches03': '0b958826-6cfc-4612-80c3-be595412943a'},
    '595ab5df-c46d-44f1-a12a-465a24dd608e': {'Reaches01': '49bf16f7-8d3b-4b4d-8fe1-8c5b28e21ec6',
                                          'Reaches02': 'd49ab692-f5db-4067-be91-7d28e3ee2b18',
                                          'Reaches03': '0ee8400e-8a53-4cdf-8f3a-7dd2e85eb6b3'},
    '5f06e1df-8425-4dc0-8bc3-186c6fb1e145': {'Reaches01': 'ff778d22-e1f4-4e53-ac3e-d0234a6f4808',
                                          'Reaches02': '770a9390-509f-478f-8c31-a50064950fe5',
                                          'Reaches03': 'dc73e662-e733-4a86-ad94-85827e102268'},
    'fe46d8c8-3cb6-41a5-a6d6-d54194a766eb': {'Reaches01': 'f67e3fc2-47fd-4ecb-8da5-0e366260f3cc',
                                          'Reaches02': 'af7812a5-15fd-43d4-86b2-a620ff5a0a45',
                                          'Reaches03': '64bf46a1-09ec-487e-ad53-4ba6880ee448'},
    '02bf8d78-13a2-44b8-92e2-dfc5ed2ec30a': {'Reaches01': '015617c3-d248-43f7-bede-0b04b8092b5d',
                                          'Reaches02': 'ee918d0b-3afa-4b48-b816-8492f66b6007',
                                          'Reaches03': '7d257d44-8479-46be-996d-7cce44320b85'},
    '489858df-1831-4b3e-a15e-c5b3df01c7a7': {'Reaches01': 'b106647c-7e76-456a-8002-662a5b1e08ad',
                                          'Reaches02': 'ff830c48-38a6-4eaf-9817-4fafbd1bf871',
                                          'Reaches03': '3a04fcd7-a7b3-4914-a7d5-50ba68e72e83'},
    '9ead7a04-dedb-4e03-801b-1d17a40dd80e': {'Reaches01': '53602211-6c41-4925-81a1-447cce62b3ed',
                                          'Reaches02': '19e015c7-6abc-4c98-94b4-6220623a9937',
                                          'Reaches03': '5339b3f0-375f-4d70-becf-29f13cafdf9d'},
    'e193ff6e-2474-4179-8160-dd20c1fddac1': {'Reaches01': 'edab7426-6623-4be4-b386-caf618e34101',
                                          'Reaches02': 'd329dd85-e97e-43bd-989f-ac05e0f8591a',
                                          'Reaches03': '9d75508d-fdb7-4c13-86f6-0e1355577cfe'},
    }


for (sr_session_id, chatsap_session_id) in exp_session_ids:
    sr_session = Session.query.get(sr_session_id)
    chatsap_session = Session.query.get(chatsap_session_id)

    sr_folders = session_folders[sr_session_id]
    chatsap_folders = session_folders[chatsap_session_id]
    for folder_name in sr_folders.keys():
        sr_folder_id = sr_folders[folder_name]
        chatsap_folder_id = chatsap_folders[folder_name]

        sr_folder = Folder.query.get(sr_folder_id)
        chatsap_folder = Folder.query.get(chatsap_folder_id)

        reviewer = Reviewer.query.filter_by(first_name='Alli', last_name='C').first()
        sr_blind_folder = BlindFolder.query.filter_by(folder_id=sr_folder.folder_id, reviewer_id=reviewer.reviewer_id).all()

        if len(sr_blind_folder) == 0:
            sr_blind_folder = [BlindFolder.query.filter_by(folder_id=sr_folder.folder_id).first()]

        if len(sr_blind_folder) == 1:
            sr_blind_folder = sr_blind_folder[0]
            reviewer = Reviewer.query.get(sr_blind_folder.reviewer_id)
            chatsap_blind_folder = BlindFolder.query.filter_by(folder_id=chatsap_folder.folder_id, reviewer_id=reviewer.reviewer_id).first()
            if chatsap_blind_folder is None:
                blind_name = random_string_generator()
                while BlindFolder.query.filter_by(blind_name=blind_name).first() is not None:
                    blind_name = random_string_generator()
                BlindFolder(folder_id=chatsap_folder.folder_id,
                            reviewer_id=reviewer.reviewer_id,
                            blind_name=blind_name).add_to_db()
                chatsap_blind_folder = BlindFolder.query.filter_by(blind_name=blind_name).first()

            sr_scored_path = Path(reviewer.scored_dir).joinpath(f"{sr_blind_folder.blind_name}_{reviewer.first_name[0]}{reviewer.last_name[0]}.csv")
            chatsap_scored_path = Path(reviewer.scored_dir).joinpath(f"{chatsap_blind_folder.blind_name}_{reviewer.first_name[0]}{reviewer.last_name[0]}.csv")
            if sr_scored_path.exists() and not chatsap_scored_path.exists():
                shutil.copyfile(sr_scored_path, chatsap_scored_path)
            else:
                print(f"score {sr_blind_folder.blind_name}")

            for sr_trial in sr_folder.trials:
                trial_dir = Path(chatsap_folder.folder_dir).joinpath(Path(sr_trial.trial_dir).name)
                chatsap_trial = Trial.query.filter_by(trial_dir=str(trial_dir)).first()

                if chatsap_trial is None:
                    Trial(experiment_id=chatsap_exp.experiment_id,
                          session_id=chatsap_session.session_id,
                          folder_id=chatsap_folder.folder_id,
                          trial_dir=str(trial_dir),
                          trial_date=sr_trial.trial_date,
                          trial_num=sr_trial.trial_num).add_to_db()
                    chatsap_trial = Trial.query.filter_by(trial_dir=str(trial_dir)).first()

                sr_blind_trial = BlindTrial.query.filter_by(blind_folder_id=sr_blind_folder.blind_folder_id,
                                                            trial_id=sr_trial.trial_id).first()
                chatsap_blind_trial = BlindTrial.query.filter_by(blind_folder_id=chatsap_blind_folder.blind_folder_id,
                                                                 trial_id=chatsap_trial.trial_id).first()
                if chatsap_blind_trial is None:
                    BlindTrial(blind_folder_id=chatsap_blind_folder.blind_folder_id,
                               reviewer_id=reviewer.reviewer_id,
                               trial_id=chatsap_trial.trial_id,
                               folder_id=chatsap_folder.folder_id,
                               blind_trial_num=sr_blind_trial.blind_trial_num).add_to_db()
