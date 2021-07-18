
# TODO: Supplemental figure with these two axes
numTransitions_gs = gridspec.GridSpec(1, 2)
numTransitions_nonChain_ax = fig.add_subplot(numTransitions_gs[0])
numTransitions_chain_ax = fig.add_subplot(numTransitions_gs[1])

distributionTransition_gs = gridspec.GridSpec(1, 1)
distributionTransition_ax = fig.add_subplot(distributionTransition_gs[0])
numTransitions_nonChain_ax: [Column('num_typical_transitions', 'typical', hatch=None, alpha=1)],
numTransitions_chain_ax: [Column('num_atypical_transitions', 'atypical', hatch=None, alpha=0.5)],
distributionTransition_ax: [Column("skips_percentAtypicalTransitions", 'skips', hatch=None, alpha=1),
                            Column("reverse_percentAtypicalTransitions", 'reverses', hatch=None, alpha=0.6),
                            Column('atypicalEnd_percentAtypicalTransitions', 'premature\ntermination', hatch=None,
                                   alpha=0.3)
# Number of transitions

numTransitions_nonChain_ax = paired_bar_chart(numTransitions_nonChain_ax,
                                              columns_dict,
                                              trials_with_chains_mean_sem,
                                              '# of transitions\nper trial',
                                              [0, 10],
                                              [3, 6, 9],
                                              title='phase transitions')
numTransitions_chain_ax = paired_bar_chart(numTransitions_chain_ax,
                                           columns_dict,
                                           trials_with_chains_mean_sem,
                                           None,
                                           [0, 10],
                                           [3, 6, 9])
numTransitions_chain_ax.yaxis.set_label_position("right")
numTransitions_chain_ax.spines['left'].set_visible(False)
numTransitions_chain_ax.spines['right'].set_visible(False)
numTransitions_chain_ax.yaxis.set_tick_params(width=0, length=0, labelleft=False)

# numberTransitions_orderedColumns = columns_dict[numTransitions_nonChain_ax]
# numberTransitions_mean, numberTransitions_sem = get_mean_sem(trials_with_chains_mean_sem,
#                                                              numberTransitions_orderedColumns)
# numTransitions_nonChain_ax = create_stacked_bar_chart(numTransitions_nonChain_ax,
#                                              numberTransitions_mean,
#                                              numberTransitions_sem,
#                                              numberTransitions_orderedColumns)
# numTransitions_nonChain_ax = format_ax(numTransitions_nonChain_ax,
#                               ylim=[0, 17],
#                               yticks=[5, 10, 15],
#                               ylabel="number of transitions\n(per trial)",
#                               title='phase transitions')
#
# legend_elements = create_legend_patches(numberChains_orderedColumns)
# numTransitions_nonChain_ax.legend(handles=legend_elements,
#                         loc='right',
#                         frameon=False,
#                         fancybox=False,
#                         fontsize='small')

# Distribution of atypical transitions (Fig 3G)
distributionTransition_ax = paired_bar_chart(distributionTransition_ax,
                                             columns_dict,
                                             trials_with_chains_mean_sem,
                                             'proportion of transitions\n(% of atypical transitions)',
                                             [0, 75],
                                             [20, 40, 60],
                                             title='distribution of atypical transitions')
# distributionTransition_ax.tick_params('x', labelrotation=90)
# distributionTransitions_orderedColumns = columns_dict[distributionTransition_ax]
# distributionTransitions_mean, distributionTransitions_sem = get_mean_sem(trials_with_chains_mean_sem,
#                                                                          distributionTransitions_orderedColumns)
# distributionTransition_ax = create_stacked_bar_chart(distributionTransition_ax,
#                                                      distributionTransitions_mean,
#                                                      distributionTransitions_sem,
#                                                      distributionTransitions_orderedColumns)
# distributionTransition_ax = format_ax(distributionTransition_ax,
#                                       ylim=[0, 110],
#                                       yticks=[25, 50, 75, 100],
#                                       ylabel='proportion of transitions\n(% of atypical transitions)',
#                                       title='distribution of\natypical transitions',
#                                       titleloc='right')
#
# legend_elements = create_legend_patches(distributionTransitions_orderedColumns)
# distributionTransition_ax.legend(handles=legend_elements,
#                                  loc='upper center',
#                                  frameon=False,
#                                  fancybox=False,
#                                  fontsize='small')
numTransitions_gs.tight_layout(fig, rect=[0, 0.25, 0.5, 0.5], pad=0.2, w_pad=1)
distributionTransition_gs.tight_layout(fig, rect=[0.5, 0.25, 1, 0.5], pad=0.2)