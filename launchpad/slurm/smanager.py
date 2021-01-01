import time
import glob
import os
import subprocess

import numpy as np
import pandas as pd


class Smanager():
    def __init__(self, user=None, format='%.18i %.9P %.100j %.8u %.2t %.10M %.6D %R'):
        self._user = user 
        if self._user is None: 
            self._user = os.environ['USER']
        self._format = format
        self.update()

    def update(self):
        if self._user == "":
            cmd = ['squeue', '-o', self._format]

        else:
            cmd = ['squeue', '-u', self._user, '-o', self._format]

        smines = subprocess.check_output(cmd)
        smines = smines.decode('utf8').split('\n')

        ids = [None for _ in range(len(smines) - 2)]
        partitions = [None for _ in range(len(smines) - 2)]
        names = [None for _ in range(len(smines) - 2)]
        users = [None for _ in range(len(smines) - 2)]
        states = [None for _ in range(len(smines) - 2)]
        times = [None for _ in range(len(smines) - 2)]
        nodes = [None for _ in range(len(smines) - 2)]
        nodelists = [None for _ in range(len(smines) - 2)]

        for i, smine in enumerate(smines[1:-1]):
            smine = smine.split(' ')
            s = [s for s in smine if s is not '']
            ids[i] = s[0]
            partitions[i] = s[1]
            names[i] = s[2]
            users[i] = s[3]
            states[i] = s[4]
            times[i] = s[5]
            nodes[i] = s[6]
            nodelists[i] = s[7]
        
        self.df = pd.DataFrame({
            'id': ids,
            'partition': partitions,
            'name': names,
            'user': users,
            'state': states,
            'time': times,
            'node': nodes,
            'nodelist': nodelists,
            })

    def get_state(self, name):
        if name not in self.df.name.unique().tolist():
            return "N"
        state = self.df.query(f"name=='{name}'").state.iloc[0]
        return state
       

    def count_job(self, pattern=None, state=None):
        self.update()
        df_ = self.df.copy()
        if pattern is not None:
            df_ = df_[df_['name'].str.contains(pattern)]
        if state is not None:
            df_ = df_[df_['state'] == state]
        return len(df_)

    def get_id(self, pattern=None):
        self.update()
        if pattern is None:
            return self.df['id'].tolist()
        else:
            return [id for id, name in zip(self.df['id'], self.df['name']) if pattern in name]

    def cancel_all(self):
        self.update()
        ids = self.get_id()
        for id in ids:
            subprocess.run(['scancel', id])

    def cancel(self, pattern):
        self.update()
        ids = self.get_id(pattern=pattern)
        for id in ids:
            subprocess.run(['scancel', id])

 
