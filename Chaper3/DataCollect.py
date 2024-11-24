from sklearn.datasets import fetch_openml
mnist = fetch_openml('mnist_784',version=1)
print(mnist.keys())

X, y = mnist['data'],mnist['target']
print(X.shape)
print(y.shape)

import matplotlib.pyplot as plt

some_digit = X[0]
some_digit_image = some_digit.reshape(28,28)

plt.plot(some_digit_image,cmap='binary')
plt.show()