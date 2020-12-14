import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

if __name__ == '__main__':
    grooming_trial_full_path = '/Users/Krista/Desktop/grooming/745_20181130_CC1_03_V01.csv'
    grooming_trial = pd.read_csv(grooming_trial_full_path, delimiter=',')

    grooming_trial["left_paw"] = grooming_trial["left_paw"]*(-1)

    full_color_palette_colors = sns.color_palette("colorblind", 7)
    full_color_palette = {0: full_color_palette_colors[0],
                          1: full_color_palette_colors[1],
                          2: full_color_palette_colors[2],
                          3: full_color_palette_colors[3],
                          4: full_color_palette_colors[4],
                          5: full_color_palette_colors[5],
                          6: full_color_palette_colors[6]}

    color_palette = {bout_pattern: full_color_palette_colors[bout_pattern]
                     for bout_pattern in grooming_trial.bout_pattern.unique()}

    figure, axis = plt.subplots()
    sns.scatterplot(x="frame_num", y="left_paw", data=grooming_trial,
                    hue="bout_pattern", palette=color_palette, ax=axis)
    sns.scatterplot(x="frame_num", y="right_paw", data=grooming_trial,
                    hue="bout_pattern", palette=color_palette, ax=axis)
    sns.lineplot(x="frame_num", y="left_paw", data=grooming_trial, hue="bout_pattern", palette=color_palette, ax=axis, legend=False)
    sns.lineplot(x="frame_num", y="right_paw", data=grooming_trial,  hue="bout_pattern", palette=color_palette, ax=axis)
    plt.show()

