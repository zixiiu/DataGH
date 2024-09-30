import pandas as pd

import consts


def find_seg(df, th, rd, ra, visualize=False):
    df['avg'] = df.iloc[:, 1].rolling(ra, center=True).mean()
    df['seg'] = df.apply(lambda row: 1 if row['avg'] > th else 0, axis=1)
    df['det'] = 0

    # Find the indices where 'seg' changes.
    changes = df['seg'] != df['seg'].shift()
    change_indices = changes[changes].index

    last_seg = 0
    bk_start = 0
    bk_pair = []
    time_start = 0
    if visualize:
        from matplotlib import pyplot as plt
        import tqdm
        pbar = tqdm.tqdm(total=len(change_indices))

    for idx, cidx in enumerate(change_indices):
        if last_seg != df.loc[cidx, 'seg']:
            if last_seg == 0:  # going up
                if not bk_pair:  # first time
                    bk_pair.append((bk_start, cidx))
                elif df.iloc[cidx][consts.time_col_name] - time_start > rd:  # a valid break
                    bk_pair.append((bk_start, cidx))
                elif df.iloc[cidx][consts.time_col_name] - time_start > 8 and len(bk_pair) > 1:  # end of test
                    # print('Time start: %f, Time end: %f' % (time_start, row['Time (s)']))
                    break
            else:
                bk_start = cidx
                time_start = df.iloc[cidx][consts.time_col_name]
            last_seg = df.iloc[cidx]['seg']
            if visualize:
                pbar.update(1)
    #
    # for idx, row in df.iterrows():
    #     if last_seg != row['seg']:
    #         if last_seg == 0:  # going up
    #             if not bk_pair:  # first time
    #                 bk_pair.append((bk_start, idx))
    #             elif row['Time (s)'] - time_start > rd: # a valid break
    #                 bk_pair.append((bk_start, idx))
    #             elif row['Time (s)'] - time_start > 8 and len(bk_pair) > 1: # end of test
    #                 # print('Time start: %f, Time end: %f' % (time_start, row['Time (s)']))
    #                 break
    #
    #         else:  # going down
    #             bk_start = idx
    #             time_start = row['Time (s)']
    #     last_seg = row['seg']
    #     if visualize:
    #         pbar.update(1)

    test_pair = [(bk_pair[i][1], bk_pair[i + 1][0]) for i in range(len(bk_pair) - 1)]

    if visualize:
        pbar.close()
        print('seg detected: %d' % len(test_pair))
        dur_list = [(end - start, idx)for idx, (start, end) in enumerate(test_pair)]
        dur_list.sort(key=lambda x: x[0], reverse=True)
        print(dur_list[:10])

        plt.scatter(df[consts.time_col_name], df[consts.power_col_name], marker='.', s=1)
        plt.plot(df[consts.time_col_name], df['avg'], color='red')
        plt.plot(df[consts.time_col_name], df['seg'] * 15, color='yellow')
        plt.plot(df[consts.time_col_name], [th for _ in range(len(df[consts.time_col_name]))], color='green')
        for start, end in bk_pair:
            plt.axvspan(df.iloc[start][consts.time_col_name], df.iloc[end][consts.time_col_name], facecolor='red', alpha=0.3)

        for start, end in test_pair:
            plt.axvspan(df.iloc[start][consts.time_col_name], df.iloc[end][consts.time_col_name], facecolor='green', alpha=0.3)

        plt.grid(True)
        plt.show()
    return test_pair


if __name__ == '__main__':
    # f = Fitter()
    # f.load_data()
    # df = pd.read_csv('data/8g3 gb5 6758.csv')
    df = pd.read_csv('data/Xiaomi13/S8 gen2 2.84 1861 5184.csv')
    th = 2
    rd = 1.9
    ra = 250
    find_seg(df, th, rd, ra, True)
