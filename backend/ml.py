#=======================================================================#
# IMPORTS
#=======================================================================#
import torch
import numpy as np
from torch import nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from nn_model import SongClassifier
import torch.nn.functional as F
from global_constants import NUM_FEATURES, NUM_CLASSES

#=======================================================================#
# def init_nn_model(): returns a pytorch.nn model based on feature sizes
#=======================================================================#
def init_nn_model():
    nn_model = SongClassifier(n_features=NUM_FEATURES, n_classes=NUM_CLASSES)
    return nn_model

#=======================================================================#
# def train_nn_model(nn_model, train_data_features, train_data_classes...)
# uses the labels (classes) along with the provided features to train
# the model
#=======================================================================#
def train_nn_model(nn_model, train_data_features, train_data_classes, epochs=100, lr=0.01):
    num_examples = train_data_features.shape[0]

    train_dataset = TensorDataset(train_data_features, train_data_classes)
    train_loader = DataLoader(train_dataset, batch_size=num_examples, shuffle=True)
    nn_model = SongClassifier(n_features=NUM_FEATURES, n_classes=NUM_FEATURES)

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

#=======================================================================#
# def classify_examples(nn_model, features_tensor): classifies the
# features using softmax (0 or 1)
#=======================================================================#
def classify_examples(nn_model, features_tensor):
    nn_model.eval()
    with torch.no_grad():
        output = nn_model(features_tensor)
        probabilities = F.softmax(output, dim=1)
        _, max_prob_index = torch.max(probabilities, dim=1)
    return max_prob_index

#=======================================================================#
# def get_positive_examples(nn_model, songs_features_tensor, song_ids_tensor):
# returns a list of only positive (1) classified examples
#=======================================================================#
def get_positive_examples(nn_model, songs_features_tensor, song_ids_tensor):

    predictions = classify_examples(nn_model, songs_features_tensor)
    positive_mask = predictions == 1
    positive_song_ids = song_ids_tensor[positive_mask].tolist()

    return positive_song_ids


# 65
