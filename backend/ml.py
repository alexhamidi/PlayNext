import torch
import numpy as np
from torch import nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from utils.spotify_api_utils import KEYS_TO_USE
from utils.db_utils import get_random_song_id
from utils.processing_utils import test_song_id_to_tensor
from utils.nn_model import SongClassifier


NUM_RETRIES = 10
POSITIVE_THRESHOLD = .7

class SongClassifier(nn.Module):
    def __init__(self, n_features, n_classes):
        super().__init__()
        self.linear_layer_1 = nn.Linear(n_features, 8)
        self.linear_layer_2 = nn.Linear(8, n_classes)

    def forward(self, features):
        x = torch.relu(self.linear_layer_1(features))
        return self.linear_layer_2(x)

def init_nn_model():
    num_features = len(KEYS_TO_USE)
    num_classes = 2
    nn_model = SongClassifier(n_features=num_features, n_classes=num_classes)
    return nn_model

def train_nn_model(nn_model, train_data_features, train_data_classes, epochs=100, lr=0.01):
    num_examples = train_data_features.shape[0]
    num_features = len(KEYS_TO_USE)
    num_classes = 2

    train_dataset = TensorDataset(train_data_features, train_data_classes)
    train_loader = DataLoader(train_dataset, batch_size=num_examples, shuffle=True)
    nn_model = SongClassifier(n_features=num_features, n_classes=num_classes)

    nn_model.train()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(nn_model.parameters(), lr=lr)

    for epoch in range(epochs):
        for train_data_features, train_data_classes in train_loader:
            outputs = nn_model(train_data_features)
            loss = criterion(outputs, train_data_classes)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step() # update params

            if (epoch + 1) % 10 == 0:
                print(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')

    return nn_model, num_examples


# problem - mismatch between labels and classes
def classify_single_example(nn_model, test_data_features):
    print('made it to classification')
    nn_model.eval()
    with torch.no_grad():
        output = nn_model(test_data_features)
        probabilities = torch.softmax(output, dim=-1)
        positive_prob = probabilities[..., 1]  # Assuming 1 is the positive class
        predicted = (positive_prob > POSITIVE_THRESHOLD).to(torch.int64)
    return predicted.item()


def get_single_song_prediction(nn_model):
    predicted_id = None
    retries = 0
    for _ in range(NUM_RETRIES): # this isnt qorking out
        retries += 1
        current_song_id = get_random_song_id()
        print(current_song_id) #
        current_song_features_tensor = test_song_id_to_tensor(current_song_id) # error here
        print(current_song_features_tensor)
        class_prediction = classify_single_example(nn_model, current_song_features_tensor) # problem - not choosy enough
        print(class_prediction)
        if class_prediction == 1:
            predicted_id = current_song_id
            break
    if predicted_id is None:
        raise Exception(f"no matches found for the model after {NUM_RETRIES} attempts")
    else:
        return predicted_id



def get_multiple_song_predictions(nn_model, num_recommendations):
    predicted_ids = []
    while len(predicted_ids) < num_recommendations:
        predicted_id = get_single_song_prediction(nn_model)
        predicted_ids.append(predicted_id)

    return predicted_ids
