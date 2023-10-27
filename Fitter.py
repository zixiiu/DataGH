import logging

import numpy as np
import pandas as pd
import tqdm

from multiprocessing import Pool, Value, Manager, freeze_support, cpu_count

from find_seg import find_seg


class Fitter:
    def __init__(self, is_gb5=False):
        self.df = None
        self.res_loss = None
        self.path = ''
        self.seg_pair = []
        self.seg_name = []
        self.rm_idx = set()
        self.is_gb5 = is_gb5
        self.seg_average = [0.0 for _ in range(42 if self.is_gb5 else 32)]

    def get_seg_pair(self, idx):
        if idx < len(self.seg_pair):
            return self.seg_pair[idx]
        else:
            return (-2, -1)
    def save_df_to_file(self):
        self.sync_seg_to_df()
        self.sync_rm_mark()
        self.df.to_csv(self.path, index=False)
    def load_data(self, path='data/D9200 1920 5150.csv'):
        self.df = pd.read_csv(path)
        self.path = path
        if 'seg' not in self.df.columns:
            self.df['seg'] = -1
            self.df.to_csv(path, index=False)
        if 'rm_mark' not in self.df.columns:
            self.df['rm_mark'] = False
            self.df.to_csv(path, index=False)



    def load_seg_from_df(self):
        seg_pair = []
        last_seg = -1
        start_idx = 0
        pbar = tqdm.tqdm(total=len(self.df['Time (s)']), desc='Loading...')
        for idx, row in self.df.iterrows():
            if last_seg != row['seg']:
                if last_seg == -1:
                    start_idx = idx
                else:
                    seg_pair.append((start_idx, idx))
            if row['rm_mark']:
                self.rm_idx.add(idx)
            last_seg = row['seg']
            pbar.update(1)

        self.seg_pair = seg_pair

        self.recalculate_avg()

        pbar.set_description('found %d seg' % len(seg_pair))
        pbar.close()

    def sync_rm_mark(self):
        self.df['rm_mark'] = False
        self.df.loc[list(self.rm_idx), 'rm_mark'] = True

    def recalculate_avg(self):
        self.sync_rm_mark()
        for idx, (start, end) in enumerate(self.seg_pair):
            filtered_df = self.df.iloc[start:end].copy()
            filtered_df = filtered_df[filtered_df['rm_mark'] == False]
            average = filtered_df['Main Avg Power (W)'].mean()
            self.seg_average[idx] = average

    def add_seg(self, start, end):
        # if start and end inside any existing seg, return
        for idx, (s, e) in enumerate(self.seg_pair):
            if start >= s and end <= e:
                logging.info('start and end inside seg %i' % idx)
                return
        # rearrange seg_pair
        self.seg_pair.append((start, end))
        self.seg_pair.sort(key=lambda x: x[0])

    def rm_seg(self, idx):
        if idx < len(self.seg_pair):
            self.seg_pair.pop(idx)
        else:
            logging.info('idx out of range')

    def get_seg_idxes_by_range(self, start, end):
        seg_idxes = []
        for idx, (s, e) in enumerate(self.seg_pair):
            if s <= start <= e or s <= end <= e:
                seg_idxes.append(idx)
        return seg_idxes

    def sync_seg_to_df(self):
        self.df.loc[:, 'seg'] = -1
        for idx, (start, end) in enumerate(self.seg_pair):
            self.df.loc[start:end, 'seg'] = idx
        self.df.to_csv(self.path, index=False)

    def sync_df(self):
        self.sync_seg_to_df()
        self.sync_rm_mark()
        self.df.to_csv(self.path, index=False)

    def det_seg(self, th_lo=1.5, th_hi=2.5, avg_lo=200, avg_hi=300, rest_lo=2.0, rest_hi=3.0):
        self.try_range(th_lo, th_hi, avg_lo, avg_hi, rest_lo, rest_hi)
        sorted_loss = sorted(self.res_loss, key=lambda x: x[0])
        selected_seg_pair = sorted_loss[0][4][:42 if self.is_gb5 else 32]
        logging.info('minimum loss: %s' % str(sorted_loss[0][0]))
        self.df.loc[:, 'seg'] = -1
        for idx, (start, end) in enumerate(selected_seg_pair):
            self.df.loc[start:end, 'seg'] = idx
        self.df.to_csv(self.path, index=False)


    def calculate(self, args, linear_idx, res_table):
        threshold, avg_num, rest_dur = args
        # dt, da, dr = location
        d = self.df.copy()
        seg_pair = find_seg(d, threshold, rest_dur, avg_num)

        ### get loss
        loss = 23333
        if seg_pair:
            loss = 0
            ### longest test : 11
            c_order = {0: 22, 1: 39, 2: 40} if self.is_gb5 else {0: 11}
            dur_list = [(end - start, idx) for idx, (start, end) in enumerate(seg_pair)]
            dur_list.sort(key=lambda x: x[0], reverse=True)

            for key, val in c_order.items():
                length, idx = dur_list[key]
                loss += abs(idx - val)

            loss += abs((42 if self.is_gb5 else 32) - len(seg_pair))
        res_table[linear_idx] = (loss, threshold, avg_num, rest_dur, seg_pair.copy())

    def try_range(self, th_lo, th_hi, avg_lo, avg_hi, rest_lo, rest_hi):
        d_threshold, d_avg, d_rest_duration = np.arange(th_lo, th_hi, 0.1), \
            np.arange(avg_lo, avg_hi, 20), \
            np.arange(rest_lo, rest_hi, 0.2)
        # d_threshold, d_avg, d_rest_duration = np.arange(1.5, 2.5, 0.1), \
        #     np.arange(200, 300, 20), \
        #     np.arange(2.0, 3.0, 0.2)

        n_thresholds = len(d_threshold)
        n_avgs = len(d_avg)
        n_rest_durations = len(d_rest_duration)

        total = n_thresholds * n_avgs * n_rest_durations

        pbar = tqdm.tqdm(total=total)

        mp_man = Manager()
        n_process = cpu_count()
        res_loss = mp_man.list([None] * total)

        # construct arg list for processes
        args_list = []
        for it, threshold in enumerate(d_threshold):
            for ia, avg_num in enumerate(d_avg):
                for ir, rest_dur in enumerate(d_rest_duration):
                    args = (threshold, avg_num, rest_dur)
                    linear_idx = it * n_avgs * n_rest_durations + ia * n_rest_durations + ir
                    args_list.append((args, linear_idx, res_loss))

        with Pool(n_process) as p:
            for i in range(0, total, n_process):
                end = i + n_process
                p.starmap(self.calculate, args_list[i:end])
                pbar.update(n_process)
        pbar.close()
        self.res_loss = res_loss[0:len(res_loss)]


if __name__ == '__main__':
    fitter = Fitter()
    fitter.load_data()
    fitter.det_seg()
    # fitter.calculate((1.5, 10, 0.7), 0, [None])
    # print(fitter.res_loss)
