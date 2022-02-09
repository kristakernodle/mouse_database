import database_pkg as dbpkg
import pandas as pd

chain_ids = pd.read_sql(dbpkg.db.session.query(dbpkg.GroomingChain.grooming_chain_id).statement,
                        dbpkg.db.session.bind)
chain_ids = chain_ids['grooming_chain_id'].to_list()
chain_ids = list(map(str, chain_ids))
chains = [dbpkg.GroomingChain.query.filter_by(grooming_chain_id=chain_id).first() for chain_id in chain_ids]

not_chains = []
for chain in chains:
    if chain.grooming_phase_2 == 0 and chain.grooming_phase_3 == 0:
        not_chains.append(chain)

for chain in not_chains:
    chain.remove_from_db()

pd.DataFrame.from_records([chain.as_dict() for chain in not_chains]).to_csv('/Users/Krista/OneDrive - Umich/behavior_paper/removedChains_20210722.csv')

bouts = dbpkg.GroomingBout.query.all()

for bout in bouts:
    bout.num_chains = len(bout.chains)
    if len(bout.chains) == 0:
        bout.num_complete_chains = 0
        bout.update()
        continue
    complete_chains = pd.DataFrame.from_records([c.as_dict() for c in bout.chains]).query('complete == True')
    bout.num_complete_chains = len(complete_chains)
    bout.update()

trials = dbpkg.GroomingTrial.query.all()
for trial in trials:
    bouts = pd.DataFrame.from_records([b.as_dict() for b in trial.bouts])
    chains = pd.DataFrame.from_records([c.as_dict() for c in trial.chains])

    trial.total_time_grooming = bouts['bout_length'].sum()
    trial.num_bouts = len(bouts)
    trial.num_chains = len(chains)
    if len(chains) != 0:
        trial.num_complete_chains = len(chains.query('complete == True'))
    trial.update()

bouts_might_be_chains = dbpkg.GroomingBout.query.filter_by(num_chains=1).all()

bouts_are_chains = []
for bout in bouts_might_be_chains:
    chain = bout.chains[0]
    if chain.duration <= bout.bout_length:
        continue
    bouts_are_chains.append(bout)