import matplotlib.pyplot as plt

# some nicer plot settings 
plt.rcParams['figure.figsize'] = (4,4)
plt.rcParams['font.family'] = 'serif'
plt.rcParams['figure.autolayout'] = True

plt.plot(range(0,8), [0.5,0.5723139575294736,0.5928076127504238,0.6090044649319126,
                      0.6093622729043453,0.6167507763975155,0.6253242921245726,
                      0.5861536604634832], '.', color='k')

# axes labels
plt.xlabel('dmax')
plt.ylabel('AUC')

# axes limits
plt.xlim(0, 7.9)
plt.ylim(0.5, 1)

# make legend and show plot
plt.show()