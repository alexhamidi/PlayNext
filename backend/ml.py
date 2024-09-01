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
from config import NUM_FEATURES, NUM_CLASSES, POSITIVE_THRESHOLD # need to fix these

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

    print('Loading dataasets')

    print('Loading train dataset')
    train_dataset = TensorDataset(train_data_features, train_data_classes)

    print('initializing loader')
    train_loader = DataLoader(train_dataset, batch_size=num_examples, shuffle=True)
    nn_model = SongClassifier(n_features=NUM_FEATURES, n_classes=NUM_CLASSES)

    print('Entering training mode')
    nn_model.train()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(nn_model.parameters(), lr=lr)

    print('Starting training process')

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

        print(probabilities)

        prob_class_1 = probabilities[:, 1]

        predictions = (prob_class_1 > POSITIVE_THRESHOLD).long()

    return predictions
#=======================================================================#
# def get_positive_examples(nn_model, songs_features_tensor, song_ids_tensor):
# returns a list of only positive (1) classified examples
#=======================================================================#
def get_positive_examples(nn_model, songs_features_tensor, song_ids_list):
    predictions = classify_examples(nn_model, songs_features_tensor)
    print("PREDICTIONS", predictions)
    predictions_list = predictions.tolist()


    positive_song_ids = [song_id for pred, song_id in zip(predictions_list, song_ids_list) if pred == 1]

    return positive_song_ids


# 65
