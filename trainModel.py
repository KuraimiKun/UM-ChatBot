import json
import nltk
import random
import pickle
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from nltk.stem.lancaster import LancasterStemmer

# Initializing Lancaster Stemmer
stemmer = LancasterStemmer()

# Loading dataset
with open('dataset/dataset.json') as f:
    data = json.load(f)

# Initialize lists
words = []
labels = []
documents = []
ignore_words = ['?', '!', '.', ',']

# Loop through each intent in the dataset
for intent in data['intents']:
    for pattern in intent['patterns']:
        # Tokenize each word in the pattern
        w = nltk.word_tokenize(pattern)
        # Add to documents
        documents.append((w, intent['tag']))
        # Extend the word list
        words.extend(w)
    # Add to labels list
    if intent['tag'] not in labels:
        labels.append(intent['tag'])

# Stem and lower each word, remove duplicates
words = [stemmer.stem(w.lower()) for w in words if w not in ignore_words]
words = sorted(list(set(words)))

# Sort labels
labels = sorted(labels)

# Create training data
training = []
output_empty = [0] * len(labels)

for doc in documents:
    bag = []
    # List of tokenized and stemmed words for the pattern
    pattern_words = [stemmer.stem(word.lower()) for word in doc[0] if word not in ignore_words]
    # Create bag of words array
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)
    # Output is '1' for the current tag and '0' for the rest
    output_row = list(output_empty)
    output_row[labels.index(doc[1])] = 1
    training.append([bag, output_row])

# Shuffle the training data and convert to numpy arrays
random.shuffle(training)
training = np.array(training, dtype=object)

# Split the features and labels
train_x = np.array(list(training[:, 0]))
train_y = np.array(list(training[:, 1]))

# Building the model using Keras
model = keras.Sequential()
model.add(layers.Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(layers.Dropout(0.5))
model.add(layers.Dense(64, activation='relu'))
model.add(layers.Dropout(0.5))
model.add(layers.Dense(len(labels), activation='softmax'))

# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

print('[INFO] Training Model...')

# Training the model
model.fit(train_x, train_y, epochs=200, batch_size=5, verbose=1)

# Saving the model
model.save('models/chatbot-model.h5')

print('[INFO] Model successfully trained')

# Saving data structures
with open('data.pickle', 'wb') as f:
    pickle.dump((words, labels), f)
