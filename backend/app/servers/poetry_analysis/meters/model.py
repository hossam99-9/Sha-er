import numpy as np

from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow import keras
from tensorflow.keras import layers
import tensorflow as tf

import keras

from backend.app.config.config import Config


vocab = list('إةابتثجحخدذرزسشصضطظعغفقكلمنهويىأءئؤ#آ ') + list('ًٌٍَُِّ') +['ْ']+['ٓ']

BOHOUR_NAMES_AR = [
    "السريع", "الكامل", "المتقارب", "المتدارك", "المنسرح", "المديد", 
    "المجتث", "الرمل", "البسيط", "الخفيف", "الطويل", "الوافر", 
    "الهزج", "الرجز", "المضارع", "المقتضب", "نثر"
]

label2name = BOHOUR_NAMES_AR

char2idx = {u: i+1 for i, u in enumerate(vocab)}

class TransformerBlock(layers.Layer):
    def __init__(self, embed_dim, num_heads, ff_dim, rate=0.1, training=True):
        super(TransformerBlock, self).__init__()
        self.training = training
        self.att = layers.MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)
        self.ffn = keras.Sequential(
            [layers.Bidirectional(layers.GRU(units=ff_dim, return_sequences=True)),
             layers.Bidirectional(layers.GRU(units=ff_dim, return_sequences=True)),
             layers.Bidirectional(layers.GRU(units=ff_dim, return_sequences=True)),
             layers.Dense(embed_dim)]
        )
        self.layernorm1 = layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = layers.LayerNormalization(epsilon=1e-6)
        self.dropout1 = layers.Dropout(rate)
        self.dropout2 = layers.Dropout(rate)

    def call(self, inputs):
        attn_output = self.att(inputs, inputs)
        attn_output = self.dropout1(attn_output, training=self.training)
        out1 = self.layernorm1(inputs + attn_output)
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=self.training)
        return self.layernorm2(out1 + ffn_output)

class TokenAndPositionEmbedding(layers.Layer):
    def __init__(self, maxlen, vocab_size, embed_dim):
        super(TokenAndPositionEmbedding, self).__init__()
        self.token_emb = layers.Embedding(input_dim=vocab_size, output_dim=embed_dim)
        self.pos_emb = layers.Embedding(input_dim=maxlen, output_dim=embed_dim)

    def call(self, x):
        maxlen = tf.shape(x)[-1]
        positions = tf.range(start=0, limit=maxlen, delta=1)
        positions = self.pos_emb(positions)
        x = self.token_emb(x)
        return x

def create_transformer_model(training=False):
    embed_dim = 64  # Embedding size for each token
    num_heads = 3  # Number of attention heads
    ff_dim = 64  # Hidden layer size in feed forward network inside transformer
    maxlen = 128
    vocab_size = len(char2idx) + 1

    inputs = layers.Input(shape=(maxlen,))
    embedding_layer = TokenAndPositionEmbedding(maxlen, vocab_size, embed_dim)
    x = embedding_layer(inputs)
    transformer_block = TransformerBlock(embed_dim, num_heads, ff_dim, training=training)
    x = transformer_block(x)
    x = layers.Flatten()(x)
    x = layers.Dense(128, activation="relu")(x)
    outputs = layers.Dense(len(label2name), activation="softmax")(x)

    model = keras.Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

def preprocess(input: str):
    x = [[char2idx.get(char, 0) for char in input]]
    x = pad_sequences(x, padding='post', value=0, maxlen=128)
    return np.array(x)

# Load model weights
checkpoint_path = Config.METERS_MODEL_WEIGHTS
model = create_transformer_model(training=False)
model.load_weights(checkpoint_path)

def predict_meter(bait: str):
    processed_bait = preprocess(bait)
    logit = model.predict(processed_bait)
    meter_index = logit.argmax(-1)[0]
    meter = label2name[meter_index]
    return meter