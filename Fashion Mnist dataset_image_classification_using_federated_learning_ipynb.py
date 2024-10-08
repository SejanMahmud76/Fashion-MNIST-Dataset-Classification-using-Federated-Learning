# -*- coding: utf-8 -*-
"""fashion_mnist  dataset image classification using federated learning.ipynb.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1BiTXKvSo3Y2c1F_vOh9VwWAMLb8CkvqK

### Install dependencies & Import libraries

Next, we install the necessary packages
* Flower (`flwr`),
* TensorFlow (`tensorflow`),
"""

!pip install -q flwr[simulation] tensorflow matplotlib;

"""Now that we have all dependencies installed, we can import everything we need for this tutorial:"""

from collections import OrderedDict
from typing import List, Tuple, Dict, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.datasets import fashion_mnist
from tensorflow.keras.layers import Conv2D, Dense, Dropout, Flatten, Input, MaxPooling2D
from tensorflow.keras.models import Model
import flwr as fl
from flwr.common import Metrics
from flwr.common.typing import NDArrays, Scalar

# Let's train on CPU
tf.config.set_visible_devices([], 'GPU')

print(
    f"Training on {'GPU' if tf.config.get_visible_devices('GPU') else 'CPU'} using TensorFlow {tf.__version__} and Flower {fl.__version__}"
)

"""Let's define some useful constants that we will need along the tutorial."""

SEED = 42
NUM_CLIENTS = 10
BATCH_SIZE = 32
VALID_FRACTION = 0.2 # fraction of the dataset used for each local client
NUM_ROUNDS = 5

"""## Data

The aim of this section is to create a divided MNIST dataset to simulate the federated learning evironment.

We provide you with the `download_data` function and want you to implement the following:

* `partition_data`,
* `train_val_divide_local_datasets`.

You are given the function prototype - function name, the necessary information about a function, arguments, their types, and the return type.

If implemented correctly they should be able to run `load_datasets` function that creates the divided datasets.

Firstly let's just have a quick look at the data (already prepared, just run the cells below).
"""

from tensorflow.keras.datasets import fashion_mnist
import numpy as np
from typing import Tuple

def download_data() -> Tuple[np.ndarray, np.ndarray]:
    # Load the Fashion-MNIST dataset
    (X_train, y_train), (X_test, y_test) = fashion_mnist.load_data()

    # Scale the input data to [0, 1]
    X_train = X_train / 255.0
    X_test = X_test / 255.0

    # Add a channel dimension to the input data (required by Conv2D layers)
    X_train = X_train[..., np.newaxis]
    X_test = X_test[..., np.newaxis]

    return (X_train, y_train), (X_test, y_test)

# Keep the x_test for (optional) centralized evaluation.
(X_train, y_train), (X_test, y_test) = download_data()

"""### Quick EDA"""

import matplotlib.pyplot as plt

# Define class names for Fashion-MNIST dataset
class_names = [
    "T-shirt/top", "Trouser", "Pullover", "Dress", "Coat",
    "Sandal", "Shirt", "Sneaker", "Bag", "Ankle boot"
]

# Create a figure and a grid of subplots
fig, axs = plt.subplots(4, 8, figsize=(10, 4))

# Loop over the images and plot them
for i, ax in enumerate(axs.flat):
    ax.imshow(X_train[i].reshape(28, 28), cmap='gray')  # Reshape the image for plotting
    ax.set_title(class_names[y_train[i]])  # Set the title to the class name
    ax.axis("off")

# Show the plot
fig.tight_layout()
plt.show()

import pandas as pd
import matplotlib.pyplot as plt

# Define class names for Fashion-MNIST dataset
class_names = [
    "T-shirt/top", "Trouser", "Pullover", "Dress", "Coat",
    "Sandal", "Shirt", "Sneaker", "Bag", "Ankle boot"
]

# Convert numerical labels to class names
labels = pd.Series([class_names[label] for label in y_train])

# Calculate label counts and sort them by label index
counts = labels.value_counts().sort_index()

# Plot the bar chart
counts.plot.bar(figsize=(7, 4), color=["#F2B705"])
plt.ylabel("Count", fontsize=16)
plt.xlabel("Label", fontsize=16)
plt.xticks(fontsize=14, rotation=45)  # Rotate labels for better readability
plt.yticks(fontsize=12)
ax = plt.gca()
plt.tight_layout()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.show()

"""We see that the data is quite evenly distributed. Let's sample the data random - iid sampling."""

def partition_data(X: np.ndarray, y: np.ndarray, n_partitions: int) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    """
    Split the dataset into iid partitions to simulate federated learning.

    Returns
    -------
    Tuple[List[np.ndarray], List[np.ndarray]]
        A list of X and y (one for each client)
    """
    X_split = np.split(X, NUM_CLIENTS)
    y_split = np.split(y, NUM_CLIENTS)
    return X_split, y_split

def train_val_divide_local_datasets(local_X: List[np.ndarray], local_y: List[np.ndarray], valid_fraction: float) -> Tuple[Tuple[List[np.ndarray], List[np.ndarray]], Tuple[List[np.ndarray], List[np.ndarray]]]:
    """Split each local dataset into train and validation."""
    X_trains = []
    y_trains = []
    X_valids = []
    y_valids = []
    partition_size = local_X[0].shape[0]
    for client_x, client_y in zip(local_X, local_y):
        train_end_idx = int((1 - VALID_FRACTION) * partition_size)
        X_trains.append(client_x[:train_end_idx])
        y_trains.append(client_y[:train_end_idx])
        X_valids.append(client_x[train_end_idx:])
        y_valids.append(client_y[train_end_idx:])

    return (X_trains, y_trains), (X_valids, y_valids)

def load_datasets(n_partitions: int, valid_fraction: float):
    """Handles the MNIST data creation for federated learning.

    It starts from downloading, thought partitioning, train test division and centralized dataset creation.

    Parameters
    ----------
    n_partitions: int
        The number of partitions the MNIST train set is divided into.
    valid_split: float
        The fraction of the validaiton data in each local dataset.

    Returns
    -------
    Tuple[List[DataLoader], List[DataLoader], DataLoader]
        Local train datasets, local validation datasets, and a centralized dataset
    """
    # DO NOT MODIFY THIS CODE
    (X_train, y_train), (centralized_X, centralized_y) = download_data()
    X_split, y_split = partition_data(X_train, y_train, n_partitions)
    (X_trains, y_trains), (X_valids, y_valids) = train_val_divide_local_datasets(X_split, y_split, valid_fraction)
    return (X_trains, y_trains), (X_valids, y_valids), (centralized_X, centralized_y)

# DO NOT MODIFY THIS CODE
(X_trains, y_trains), (X_valids, y_valids), (centralized_X, centralized_y) = load_datasets(
    n_partitions=NUM_CLIENTS,
    valid_fraction=VALID_FRACTION)

"""## Test Solution using Centralized Training

In this section you are not required to implement anything. You can test your solution by doing centralized training on one of the partitions of the data by simply running the code below.


"""

class CNN(Model):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = Conv2D(32, (3, 3), activation='relu')
        self.pool1 = MaxPooling2D((2, 2))
        self.conv2 = Conv2D(64, (3, 3), activation='relu')
        self.pool2 = MaxPooling2D((2, 2))
        self.flatten = Flatten()
        self.dense1 = Dense(128, activation='relu')
        self.dropout = Dropout(0.5)
        self.dense2 = Dense(10, activation='softmax')

    def call(self, inputs):
        x = self.conv1(inputs)
        x = self.pool1(x)
        x = self.conv2(x)
        x = self.pool2(x)
        x = self.flatten(x)
        x = self.dense1(x)
        x = self.dropout(x)
        return self.dense2(x)

"""Run the centralized training."""

first_X_train, first_y_train = X_trains[0], y_trains[0]
first_X_valid, first_y_valid = X_trains[0], y_trains[0]
model = CNN()

model.compile("adam", "sparse_categorical_crossentropy", metrics=["accuracy"])
model.fit(first_X_train, first_y_train, epochs=5, batch_size=BATCH_SIZE, validation_data=(first_X_valid, first_y_valid))

"""## Federated Learning

Now, we'll move to implementing federated learning system.

You will need to implement `FlowerClinet`, create Flower Strategy e.g. `FedAvg` and start simulation.

### Updating model parameters

In federated learning, the server sends the global model parameters to the client, and the client updates the local model with the parameters received from the server. It then trains the model on the local data (which changes the model parameters locally) and sends the updated/changed model parameters back to the server (or, alternatively, it sends just the gradients back to the server, not the full model parameters).

Luckily, TensorFlow has `set_weigths` and `get_weights` methods. (Note that when working with PyTorch helper functions creation is needed to achieve that).

### Implement a Flower client

In Flower, we create clients by implementing subclasses of `flwr.client.Client` or `flwr.client.NumPyClient`. We use `NumPyClient` in this tutorial because it is easier to implement and requires us to write less boilerplate.

To implement the Flower client, we create a subclass of `flwr.client.NumPyClient` and implement the three methods `get_parameters`, `fit`, and `evaluate`.
"""

from flwr.common.typing import NDArrays
class FlowerClient(fl.client.NumPyClient):
    """
    Class representing a single client in FL system, required to use Flower.
    """
    def __init__(self, model: Model, X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray, y_test: np.ndarray):
        self.model = model
        self.model.build((32, 28, 28, 1))
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test

    def get_parameters(self, config):
        """Return the current local model parameters"""
        return self.model.get_weights()


    def fit(self, parameters: NDArrays, config: Dict[str, Scalar]) -> NDArrays:
        """Train the model on the local (train) data.

        Parameters
        ----------
        parameters: NDarrays
            Model parameters (weights) received from the server

        config: Dict[str, Scalar]
            Server based configuration (needed only if you require dynamically changing values).

        Returns
        -------
        NDArrays
            Updated model parameters

        """
        self.model.compile("adam", "sparse_categorical_crossentropy", metrics=["accuracy"])
        self.model.set_weights(parameters)
        self.model.fit(self.X_train, self.y_train, epochs=1, batch_size=BATCH_SIZE, verbose=0)
        return self.model.get_weights(), len(self.X_train), {}

    def evaluate(self, parameters: NDArrays, config: Dict[str, Scalar])-> Tuple[float, int, Dict[str, Scalar]]:
        """Evaluate model using the validation data.

        Parameters
        ----------
         parameters: NDarrays
            Model parameters (weights) received from the server

        config: Dict[str, Scalar]
            Server based configuration (needed only if you require dynamically changing values).

        Returns
        -------
        loss : float
            The evaluation loss of the model on the local dataset.
        num_examples : int
            The number of examples used for evaluation.
        metrics : Dict[str, Scalar]
            A dictionary mapping arbitrary string keys to values of
            type bool, bytes, float, int, or str. It can be used to
            communicate arbitrary values back to the server.
        """
        self.model.compile("adam", "sparse_categorical_crossentropy", metrics=["accuracy"])
        # self.model.build(input_shape=(32, 28, 28, 1))
        self.model.set_weights(parameters)
        loss, accuracy = self.model.evaluate(self.X_test, self.y_test, batch_size=32, verbose=0)
        return loss, len(self.X_test), {"accuracy": accuracy}

"""Our class `FlowerClient` defines how local training/evaluation will be performed and allows Flower to call the local training/evaluation through `fit` and `evaluate`. Each instance of `FlowerClient` represents a *single client* in our federated learning system. Federated learning systems have multiple clients (otherwise, there's not much to federate), so each client will be represented by its own instance of `FlowerClient`. If we have, for example, three clients in our workload, then we'd have three instances of `FlowerClient`. Flower calls `FlowerClient.fit` on the respective instance when the server selects a particular client for training (and `FlowerClient.evaluate` for evaluation).

### Use the Virtual Client Engine

We will simulate a federated learning system with 10 clients on a single machine = 10 instances of `FlowerClient` in memory. Doing this on a single machine.

Flower creates `FlowerClient` instances only when they are actually necessary for training or evaluation by callling `client_fn` that returns a `FlowerClient` instance on demand. After using them for `fit` or `evaluate` they are discarded, so they should not keep any local state.

`client_fn` takes a single argument `cid` - a client ID. The `cid` can be used, for example, to load different local data partitions for different clients.
"""

# We can use the fact that we are using Jupyter Notebook environment and use the data without providing it as an argument.
def create_client_fn(cid: str) -> FlowerClient:
    """Create a Flower client representing a single organization."""
    model = CNN()
    cid_int = int(cid)
    return FlowerClient(model, X_trains[cid_int], y_trains[cid_int], X_valids[cid_int], y_valids[cid_int])

"""### Metrics Aggregation
Flower can automatically aggregate losses returned by individual clients, but it cannot do the same for metrics in the generic metrics dictionary (the one with the `accuracy` key). Metrics dictionaries can contain very different kinds of metrics and even key/value pairs that are not metrics at all, so the framework does not (and can not) know how to handle these automatically.

The `weighted_average` function has to be passed to `evaluate_metrics_aggregation_fn` in your strategy.
"""

def weighted_average(metrics: List[Tuple[int, Metrics]]) -> Metrics:
    # Multiply accuracy of each client by number of examples used
    accuracies = [num_examples * m["accuracy"] for num_examples, m in metrics]
    examples = [num_examples for num_examples, _ in metrics]

    # Aggregate and return custom metric (weighted average)
    return {"accuracy": sum(accuracies) / sum(examples)}

"""### Create a Strategy

Pick a strategy used for training. A good starting point is `FedAvg` but feel free to go throught the available strategies https://github.com/adap/flower/tree/main/src/py/flwr/server/strategy
"""

# Instantiate/Create a Flower strategy e.g. FedAvg
#TODO: Choose the strategy and specify the arguments
strategy = fl.server.strategy.FedAvg(
    fraction_fit=1.0,  # Sample 100% of available clients for training
    fraction_evaluate=0.5,  # Sample 50% of available clients for evaluation
    min_fit_clients=10,  # Never sample less than 10 clients for training
    min_evaluate_clients=5,  # Never sample less than 5 clients for evaluation
    min_available_clients=10,  # Wait until all 10 clients are available
    evaluate_metrics_aggregation_fn=weighted_average,
)

"""### Run Flower Simulation

The function `flwr.simulation.start_simulation` accepts a number of arguments, amongst them the `client_fn` used to create `FlowerClient` instances, the number of clients to simulate (`num_clients`), the number of federated learning rounds (`num_rounds`), and the strategy. The strategy encapsulates the federated learning approach/algorithm, for example, *Federated Averaging* (FedAvg).

Flower has a number of built-in strategies, but we can also use our own strategy implementations to customize nearly all aspects of the federated learning approach. For this example, we use the built-in `FedAvg` implementation and customize it using a few basic parameters. The last step is the actual call to `start_simulation` which - you guessed it - starts the simulation:
"""

client_resources = {"num_cpus": 2}
if tf.config.get_visible_devices("GPU"):
    client_resources["num_gpus"] = 1


# Start simulation
history = fl.simulation.start_simulation(
    client_fn=create_client_fn,
    num_clients=NUM_CLIENTS,
    config=fl.server.ServerConfig(num_rounds=NUM_ROUNDS),
    strategy=strategy,
    client_resources=client_resources,
)

history

"""## Centralized Evaluation

Modification of the strategy is needed for centralized evaluation.
"""

def evaluate(
    server_round: int,
    parameters: fl.common.NDArrays,
    config: Dict[str, fl.common.Scalar],
    ) -> Optional[Tuple[float, Dict[str, fl.common.Scalar]]]:
    """Centralized evaluation function"""
    model = CNN()
    model.compile("adam", "sparse_categorical_crossentropy", metrics=["accuracy"])
    model.build(input_shape=(BATCH_SIZE, 28, 28, 1))
    model.set_weights(parameters)
    loss, accuracy = model.evaluate(X_test, y_test, batch_size=32, verbose=0)
    return loss, {"accuracy": accuracy}

# TODO: Specify the Strategy
strategy = fl.server.strategy.FedAvg(
    fraction_fit=1.0,  # Sample 100% of available clients for training
    fraction_evaluate=0.5,  # Sample 50% of available clients for evaluation
    min_fit_clients=10,  # Never sample less than 10 clients for training
    min_evaluate_clients=5,  # Never sample less than 5 clients for evaluation
    min_available_clients=10,  # Wait until all 10 clients are available
    evaluate_metrics_aggregation_fn=weighted_average,
    evaluate_fn=evaluate
)

# Start simulation
history = fl.simulation.start_simulation(
    client_fn=create_client_fn,
    num_clients=NUM_CLIENTS,
    config=fl.server.ServerConfig(num_rounds=NUM_ROUNDS),
    strategy=strategy,
    client_resources=client_resources,
)

history

