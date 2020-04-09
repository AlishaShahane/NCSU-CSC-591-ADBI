import matplotlib.pyplot as plt
from scipy.stats import norm
import math
import numpy as np

# Given parameters
n = 20
mu_prior = 4
var_prior = 0.64
std_dev_prior = math.sqrt(var_prior)

mu_like = 6
var_like = 2.25
std_dev_like = math.sqrt(var_like)

# Calculated parametres for posterior distribution
mu_post = 5.7
var_post = 0.095
std_dev_post = math.sqrt(var_post)

# Plotting
# -------------- Prior --------------
x_prior = sorted(np.random.normal(mu_prior, std_dev_prior, n))
y_prior = norm.pdf(x_prior, mu_prior, std_dev_prior)
 
prior, = plt.plot(x_prior, y_prior, color = 'tab:purple', linewidth = 4.0)

# -------------- Likelihood --------------
x_like = sorted(np.random.normal(mu_like, std_dev_like, n))
y_like = norm.pdf(x_like, mu_like, std_dev_like)

likelihood, = plt.plot(x_like, y_like, color = 'tab:blue', linewidth = 4.0)

# -------------- Posterior --------------
x_post = sorted(np.random.normal(mu_post, std_dev_post, n))
y_post = norm.pdf(x_post, mu_post, std_dev_post)

posterior, = plt.plot(x_post, y_post, color = 'magenta', linewidth = 4.0)

plt.title("Probability Distribution")
plt.xlabel('x')
plt.ylabel('Probability Density')
plt.legend(handles = [prior, likelihood, posterior], labels = ['prior', 'likelihood', 'posterior'])
plt.savefig("Plot.png")
#plt.show()


