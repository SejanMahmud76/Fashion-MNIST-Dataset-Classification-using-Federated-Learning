
# Fashion MNIST Classification using Federated Learning

This project implements an image classification model using the Fashion MNIST dataset, employing **Federated Learning** to distribute the training across multiple clients. The goal is to evaluate the effectiveness of federated learning versus centralized learning for image classification tasks.
![image](https://github.com/user-attachments/assets/c0a2ac63-a367-4f11-b3be-d1ba0c2c2677)
![image](https://github.com/user-attachments/assets/6336f82c-5b9f-40f6-8404-94a6b4c32bb1)



## Project Overview

- **Dataset**: Fashion-MNIST
- **Model**: Convolutional Neural Network (CNN)
- **Learning Approach**: Federated Learning (with a comparison to centralized learning)
- **Frameworks**:
  - TensorFlow/Keras
  - Flower (`flwr`) for federated learning

## Federated Learning

Federated learning is a distributed machine learning technique where the model is trained across multiple devices or servers (clients) without the need to share the data. The model updates are sent to a central server, which aggregates them to form a global model.

### Workflow:

1. **Clients**: Each client trains the model locally on its dataset.
2. **Server**: Aggregates the model updates from clients.
3. **Global Model**: The server updates the global model and sends it back to clients for the next round of training.

## Model Architecture

The model used is a Convolutional Neural Network (CNN), which is effective for image classification tasks. The architecture consists of multiple convolutional and pooling layers followed by fully connected layers.

## Results

The project tracks and compares the following metrics:

- **Loss**: Training loss for both distributed (federated) and centralized models.
- **Accuracy**: The accuracy of the model on the validation set.

### Centralized Model Performance:

| Round | Accuracy | Loss |
|-------|----------|------|
| 0     | 13.9%    | 2.29 |
| 5     | 84.3%    | 0.43 |
![image](https://github.com/user-attachments/assets/568e9887-c24e-44fc-abc5-899c9ae3ba06)
![image](https://github.com/user-attachments/assets/4c786108-257b-4397-aeb6-851d709734dc)



### Federated Model Performance:

| Round | Accuracy | Loss |
|-------|----------|------|
| 1     | 75.5%    | 0.75 |
| 5     | 84.7%    | 0.42 |
![image](https://github.com/user-attachments/assets/ffa07e6b-2df3-45a9-80eb-a3e9759518ab)
![image](https://github.com/user-attachments/assets/2f892004-756e-4b08-a6e4-4cc40c97b0a2)


## Installation and Setup

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/fashion-mnist-federated-learning.git
   cd fashion-mnist-federated-learning
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the notebook:

   Open the notebook in Jupyter or Google Colab to execute the cells.

## Usage

- **Training**: The notebook allows you to run both centralized and federated learning.
- **Evaluation**: After training, you can compare the accuracy and loss of the models.

## Dependencies

- TensorFlow
- Keras
- Flower (`flwr`)

To install dependencies, run:

```bash
pip install tensorflow flwr
```

## Acknowledgements

- The project uses the Fashion-MNIST dataset, provided by Zalando.
- Federated Learning framework: [Flower](https://flower.dev/)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


