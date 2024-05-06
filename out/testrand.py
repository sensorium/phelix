import matplotlib.pyplot as plt
plt.figure(figsize = (8, 4))
plt.hist([random.expovariate(0.5) for i in range(100000)], bins = 100)
plt.show()