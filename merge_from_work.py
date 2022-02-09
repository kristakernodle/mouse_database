from database_pkg import Experiment
exp = Experiment.get_by_name('dlxCKO-chatSap-skilled-reaching')
back_up_dir = '/Volumes/SharedX/Neuro-Leventhal/data/mouseSkilledReaching/back_up_csv/20210323-work'
exp.merge_from_work(back_up_dir)
