import pandas as pd

def find_seg(df, th, rd, ra, visualize=False):
    df['avg'] = df.iloc[:, 1].rolling(ra, center=True).mean()
    df['seg'] = df.apply(lambda row: 1 if row['avg'] > th else 0, axis=1)
    df['det'] = 0

    last_seg = 0
    bk_start = 0
    bk_pair = []
    time_start = 0
    if visualize:
        from matplotlib import pyplot as plt
        import tqdm
        pbar = tqdm.tqdm(total=len(df['Time (s)']))
    for idx, row in df.iterrows():
        if last_seg != row['seg']:
            if last_seg == 0:  # going up
                if not bk_pair:  # first time
                    bk_pair.append((bk_start, idx))
                elif row['Time (s)'] - time_start > rd: # a valid break
                    bk_pair.append((bk_start, idx))
                elif row['Time (s)'] - time_start > 8 and len(bk_pair) > 1: # end of test
                    # print('Time start: %f, Time end: %f' % (time_start, row['Time (s)']))
                    break

            else:  # going down
                bk_start = idx
                time_start = row['Time (s)']
        last_seg = row['seg']
        if visualize:
            pbar.update(1)

    test_pair = [(bk_pair[i][1], bk_pair[i + 1][0]) for i in range(len(bk_pair) - 1)]

    if visualize:
        pbar.close()
        print('seg detected: %d' % len(test_pair))
        dur_list = [(end - start, idx)for idx, (start, end) in enumerate(test_pair)]
        dur_list.sort(key=lambda x: x[0], reverse=True)
        print(dur_list[:10])

        plt.scatter(df['Time (s)'], df['Main Avg Power (W)'], marker='.', s=1)
        plt.plot(df['Time (s)'], df['avg'], color='red')
        plt.plot(df['Time (s)'], df['seg'] * 15, color='yellow')
        plt.plot(df['Time (s)'], [th for _ in range(len(df['Time (s)']))], color='green')
        for start, end in bk_pair:
            plt.axvspan(df.iloc[start]['Time (s)'], df.iloc[end]['Time (s)'], facecolor='red', alpha=0.3)

        for start, end in test_pair:
            plt.axvspan(df.iloc[start]['Time (s)'], df.iloc[end]['Time (s)'], facecolor='green', alpha=0.3)

        plt.grid(True)
        plt.show()
    return test_pair


if __name__ == '__main__':
    # f = Fitter()
    # f.load_data()
    df = pd.read_csv('data/8g3 gb5 6758.csv')
    th = 2
    rd = 0.6
    ra = 250
    find_seg(df, th, rd, ra, True)
