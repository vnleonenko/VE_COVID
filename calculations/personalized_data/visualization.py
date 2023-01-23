import locale

import numpy as np
import pandas as pd


import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


locale.setlocale(locale.LC_ALL, locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8')))

font = {'size': 22}
matplotlib.rc('font', **font)


def plot_lost_gdp(pop1, pop2):
    matplotlib.rcParams.update({'font.size': 11})
    fig, ax = plt.subplots(1, 1, figsize=(7, 5))
    bar_width = 0.25
    colors = ['tab:blue', 'tab:orange']
    for i, y in enumerate(pop1):
        if i == 0:
            label = 'Невакцинированное население'
        else:
            label = None
        bar1 = ax.bar(x=i + bar_width / 2, height=y, width=bar_width,
                      color=colors[0], label=label)
        ax.bar_label(bar1, [str(round(y, 2)).replace('.', ',')])

    for i, y in enumerate(pop2):
        if i == 0:
            label = 'Вакцинированное население (ПВН 100%)'
        else:
            label = None
        bar2 = ax.bar(x=i - bar_width / 2, height=y, width=bar_width,
                      color=colors[1], label=label)
        ax.bar_label(bar2, [str(round(y, 2)).replace('.', ',')])

    plt.xticks([0, 1], ['мужчины', 'женщины'])
    plt.xlabel('Категории населения')
    plt.ylabel('Недополученный ВВП на душу населения, руб')
    plt.legend(loc='upper right', bbox_to_anchor=(1, 0.95))
    plt.show()


def plot_yll(dfs, vac_percentage, female_pop=False, output_folder='output'):
    matplotlib.rcParams.update({'font.size': 25})

    fig, ax1 = plt.subplots(figsize=(15, 17))
    labels = {0: 'Все население', 1: 'Вакцинированное население (ПВН 100%)'}
    offset = 0
    width = 0.5
    x = 0
    xticks = {2: '20-29 лет', 3: '30-39 лет',
              4: '40-49 лет', 5: '50-59 лет',
              6: '60-69 лет', 7: '70-79 лет',
              8: '80-89 лет', 9: '90-99 лет'}
    for j, df in enumerate(dfs):
        bar_width = width / len(dfs)
        center = int(len(dfs) / 2)
        if len(dfs) % 2 != 0:
            if j < center:
                offset = -(center-j) * bar_width
            elif j == center:
                offset = 0
            else:
                offset = (j-center) * bar_width
        else:
            if j < center:
                offset = -(center-j) * bar_width + bar_width/2
            elif j >= center:
                offset = (j-center) * bar_width + bar_width/2
        x = df['age_cat']
        y = df['crude_yll']
        bars = ax1.bar(x + offset, y, bar_width, label=labels[j])
        ax1.bar_label(bars, labels=[str(round(x, 1)).replace('.', ',') for x in y])
    ax2 = ax1.twinx()
    ax2.plot(x, vac_percentage, color='green', marker='.', lw=2,
             label='Процент вакцинированного населения (ПВН)')
    ax2.set_ylim([0, 100])
    for i, t in enumerate(vac_percentage):
        ax2.text(i+2, t+2, f'{t:,.0f}%', color='green')

    ax1.set_xlabel('Возрастная категория', labelpad=9)
    ax1.set_ylabel('ПГПЖ на 1000 человек, годы')
    ax2.set_ylabel('Процент вакцинированных среди возрастной группы, %',
                   rotation=-90, labelpad=13)

    # ax1.set_title(title)
    ax1.set_xticks(x, labels=[xticks[k] for k in x])
    handles, labels = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    handles, labels = handles2 + handles, labels2 + labels
    order = [1, 0, 2]
    plt.tight_layout(pad=1)
    fig.legend([handles[idx] for idx in order], [labels[idx] for idx in order],
               loc="upper left", bbox_to_anchor=(0, 0.95), bbox_transform=ax1.transAxes)
    png_title = 'мужское_население'
    if female_pop:
        png_title = 'женское_население'
    fig.savefig(f'./{output_folder}/ПГПЖ_{png_title}.png')


def plot_ratio(dfs, subject, age_groups, df_labels, ppv=None, output_folder='output'):
    severe_degree = {1: 'удовлетво-\nрительное', 2: 'средней\nтяжести', 3: 'тяжелое',
                     4: 'крайне\nтяжелое', 5: 'клиническая\nсмерть', 6: 'терми-\nнальное'}

    age_cats = list(age_groups.keys())
    subject_id, subject_name = subject.popitem()
    # titles = ['а)', 'б)', 'в)', 'г)', 'д)', 'е)', 'ж)', 'з)']

    for i, age_cat in enumerate(age_cats):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
        fig.subplots_adjust(hspace=0.05)

        x_max = offset = 0
        xtick_vals = None
        min_cut_value = 0
        max_cut_value = 1
        for j, df in enumerate(dfs):
            region_df = df[df['region_id'] == subject_id]
            df = region_df[region_df['age_cat'] == age_cat]
            x, y = df['tyazh_code'], df['ratio']
            width = 0.5
            if len(x) > x_max:
                x_max = len(x)
                xtick_vals = x
            bar_width = width / len(dfs)
            center = int(len(dfs)/2)

            if len(dfs) % 2 != 0:
                if j < center:
                    offset = -(center-j) * bar_width - 0.04
                elif j == center:
                    offset = 0
                else:
                    offset = (j-center) * bar_width + 0.04
            else:
                if j < center:
                    offset = -(center-j) * bar_width + bar_width/2 - 0.02
                elif j >= center:
                    offset = (j-center) * bar_width + bar_width/2 + 0.02

            y = [el if el != 0 else 0 for el in y.round(2).tolist()]
            if j == 0 and ppv is not None:
                label = df_labels[j][0] + f' (ПВН {ppv[i]:,.0f}%)'
            else:
                label = df_labels[j][0]
            bar1 = ax1.bar(x + offset, y, bar_width, label=label, color=df_labels[j][1])
            ax1.bar_label(bar1, labels=[str(round(x, 2)).replace('.', ',') for x in y],
                          fontsize=15, padding=2)
            bar2 = ax2.bar(x + offset, y, bar_width, color=df_labels[j][1])
            ax2.bar_label(bar2, labels=[str(round(x, 2)).replace('.', ',') for x in y],
                          fontsize=15, padding=2)

            min_tyazh_1 = df[(df['age_cat'].isin(age_cats)) & (df['tyazh_code'] == 1) &
                         (df['region_id'] == subject_id)]['ratio'].min()
            max_tyazh_2 = df[(df['age_cat'].isin(age_cats)) & (df['tyazh_code'] == 2) &
                         (df['region_id'] == subject_id)]['ratio'].max()

            if max_tyazh_2 > min_cut_value:
                min_cut_value = max_tyazh_2
            if min_tyazh_1 < max_cut_value:
                max_cut_value = min_tyazh_1

        cut_interval = [min_cut_value + 0.4 * min_cut_value, max_cut_value - 0.2 * max_cut_value]

        ax1.set_ylim(cut_interval[1], 1)
        ax2.set_ylim(0, cut_interval[0])

        ax1.spines.bottom.set_visible(False)
        ax1.xaxis.tick_top()
        ax1.tick_params(labeltop=False)
        ax1.set_title(age_groups[age_cat], pad=20, loc='right')
        ax1.locator_params(tight=True, nbins=6)
        ax1.ticklabel_format(axis='y', useLocale=True)

        ax1.grid()
        ax1.legend()
        ax1.set_axisbelow(True)

        ax2.set_axisbelow(True)
        ax2.xaxis.tick_bottom()
        ax2.spines.top.set_visible(False)
        xtick_labels = [severe_degree[k] for k in xtick_vals]
        ax2.set_xticks(xtick_vals, xtick_labels)
        ax2.locator_params(axis='x', tight=True, nbins=x_max)
        ax2.locator_params(axis='y', tight=True, nbins=6)
        ax2.ticklabel_format(axis='y', useLocale=True)
        ax2.grid()

        plt.xlabel('Степень тяжести заболевания', labelpad=10)
        fig.supylabel('Доля заболевших в феврале')
        plt.tight_layout(pad=1.08)

        d = .5
        kwargs = dict(marker=[(-1, -d), (1, d)], markersize=12,
                      linestyle="none", color='k', mec='k', mew=1, clip_on=False)
        ax1.plot([0, 1], [0, 0], transform=ax1.transAxes, **kwargs)
        ax2.plot([0, 1], [1, 1], transform=ax2.transAxes, **kwargs)

        fig.savefig(f'./{output_folder}/ratio_{age_cat}', dpi=200)


def plot_lost_profit(dfs, female_pop=False, output_folder='output'):
    matplotlib.rcParams.update({'font.size': 18})

    fig, ax1 = plt.subplots(figsize=(10, 7))
    label = 'мужское'
    if female_pop:
        label = 'женское'
    labels = {0: f'Невакц. {label} трудоспособное население',
              1: f'Вакц. {label} трудоспособное население'}
    offset = 0
    width = 0.5
    x = 0
    xticks = {2: '20-29 лет', 3: '30-39 лет',
              4: '40-49 лет', 5: '50-59 лет'}
    for j, df in enumerate(dfs):
        bar_width = width / len(dfs)
        center = int(len(dfs) / 2)
        if len(dfs) % 2 != 0:
            if j < center:
                offset = -(center - j) * bar_width
            elif j == center:
                offset = 0
            else:
                offset = (j - center) * bar_width
        else:
            if j < center:
                offset = -(center - j) * bar_width + bar_width / 2
            elif j >= center:
                offset = (j - center) * bar_width + bar_width / 2
        x = df['age_cat']
        y = df['lost_gdp']
        bars = ax1.bar(x + offset, y, bar_width, label=labels[j])
        ax1.bar_label(bars, labels=[str(round(x)).replace('.', ',') for x in y],
                      fontsize=12)

    ax1.set_xlabel('Возрастная категория', labelpad=9)
    ax1.set_ylabel('Недополученный ВВП на душу населения, руб')

    ax1.set_xticks(x, labels=[xticks[k] for k in x])
    plt.tight_layout(pad=1)
    fig.legend(loc='lower left', bbox_to_anchor=(0, 0), bbox_transform=ax1.transAxes)
    png_title = 'мужское_население'
    if female_pop:
        png_title = 'женское_население'
    fig.savefig(f'./{output_folder}/недополученный_ввп_{png_title}.png')
