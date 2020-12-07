import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.collections import PathCollection
from pathlib import Path

palette = {"Control": 'b', "Knock-Out": 'r'}


def plot_success_rate(success_type, data, group: bool, subtitle=None, eartag=None,
                      save_dir='/Users/Krista/Desktop/figures/', upper_ylim=70):
    sns.set_theme(context='talk', style="darkgrid")

    figure, axis = plt.subplots()
    sns.lineplot(x="session_num", y=success_type, hue='genotype', palette=palette,
                 data=data)

    if group:
        sns.scatterplot(x="session_num", y=success_type, hue='genotype', palette=palette,
                        data=data)

    axis.set_ylim(0, upper_ylim)
    axis.set_xticks(list(range(1, 22)))
    plt.setp(axis.get_xticklabels(), rotation=90)
    axis.set(xlabel='Training Session', ylabel='Percent Success')

    title_string = f"Skilled-Reaching {success_type} Rate \n" \
                   f"{subtitle}"
    axis.set_title(title_string)

    plt.legend(title='Genotype')

    handles, labels = axis.get_legend_handles_labels()

    if len(handles) > 2:
        handles_labels = list(zip(handles, labels))
        handles_labels = [tup for tup in handles_labels if isinstance(tup[0], PathCollection)]
        handles_labels = sorted(handles_labels, key=lambda group: group[1])
        unzipped_handles_labels = list(zip(*handles_labels))
        axis.legend(unzipped_handles_labels[0], unzipped_handles_labels[1])

    if group:
        file_name = f'{"_".join(success_type.lower().split(" "))}_rate.png'
    else:
        file_name = f'{eartag}_{"_".join(success_type.lower().split(" "))}_rate.png'
    plt.subplots_adjust(bottom=0.15)
    plt.savefig(str(Path(save_dir).joinpath(file_name)))
    plt.close(figure)
