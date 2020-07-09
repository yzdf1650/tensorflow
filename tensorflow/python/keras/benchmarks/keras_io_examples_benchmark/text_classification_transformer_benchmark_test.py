# Copyright 2020 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Text classification with Transformer. 
  https://keras.io/examples/nlp/text_classification_with_transformer/
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import six

import tensorflow as tf

from tensorflow.python.platform import benchmark
from tensorflow.python.keras.benchmarks.keras_io_examples_benchmark \
  import benchmark_util


class TextWithTransformerBenchmark(
    six.with_metaclass(benchmark.ParameterizedBenchmark, tf.test.Benchmark)):
  """Required Arguments for measure_performance:

      x: Input data, it could be Numpy or load from tfds.
      y: Target data. If `x` is a dataset, generator instance,
         `y` should not be specified.
      loss: Loss function for model.
      optimizer: Optimizer for model.
      Other details can see in `measure_performance()` method of
      benchmark_util.
  """

  def __init__(self):
    super(TextWithTransformerBenchmark, self).__init__()
    max_feature = 20000
    max_len = 200
    (self.imdb_x, self.imdb_y), _ = tf.keras.datasets.imdb.load_data(
        num_words=max_feature)
    self.imdb_x = tf.keras.preprocessing.sequence.pad_sequences(
        self.imdb_x, maxlen=max_len)

  """The parameters of each benchmark is a tuple:

     (benchmark_name_suffix, batch_size, run_iters).
     benchmark_name_suffix: The suffix of the benchmark test name with
     convention `{bs}_{batch_size}`.
     batch_size: Integer. Number of samples per gradient update.
     run_iters: Integer. Number of iterations to run the
         performance measurement.
  """
  _benchmark_parameters = [
      ('bs_64', 64, 2), ('bs_128', 128, 1), 
      ('bs_256', 256, 1), ('bs_512', 512, 3)]

  def _build_model(self):
    vocab_size = 20000
    max_len = 200
    embed_dim = 32
    num_heads = 2
    ff_dim = 32
    inputs = tf.keras.layers.Input(shape=(max_len,))
    embedding_layer = TokenAndPositionEmbedding(
        max_len,
        vocab_size,
        embed_dim)
    x = embedding_layer(inputs)
    transformer_block = TransformerBlock(
        embed_dim,
        num_heads,
        ff_dim)
    x = transformer_block(x)
    x = tf.keras.layers.GlobalAvgPool1D()(x)
    x = tf.keras.layers.Dropout(0.1)(x)
    x = tf.keras.layers.Dense(20, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.1)(x)
    outputs = tf.keras.layers.Dense(2, activation="softmax")(x)

    model = tf.keras.Model(inputs=inputs, outputs=outputs)
    return model
  
  def benchmark_text_classification(self, batch_size, run_iters):
    """Benchmark for Text classification with Transformer."""
    results = benchmark_util.measure_performance(
        self._build_model,
        x=self.imdb_x,
        y=self.imdb_y,
        batch_size=batch_size,
        run_iters=run_iters,
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy'])

    self.report_benchmark(
        iters=run_iters, wall_time=results['wall_time'], extras=results)


class MultiHeadSelfAttention(tf.keras.layers.Layer):
  """Implement multi head self attention as a Keras layer."""
  def __init__(self, embed_dim, num_heads=8):
    super(MultiHeadSelfAttention, self).__init__()
    self.embed_dim = embed_dim
    self.num_heads = num_heads
    if embed_dim % num_heads != 0:
      raise ValueError(
          f"embedding dimension = {embed_dim} should be divisible "
          f"by number of heads = {num_heads}"
      )
    self.projection_dim = embed_dim // num_heads
    self.query_dense = tf.keras.layers.Dense(embed_dim)
    self.key_dense = tf.keras.layers.Dense(embed_dim)
    self.value_dense = tf.keras.layers.Dense(embed_dim)
    self.combine_heads = tf.keras.layers.Dense(embed_dim)

  def attention(self, query, key, value):
    score = tf.matmul(query, key, transpose_b=True)
    dim_key = tf.cast(tf.shape(key)[-1], tf.float32)
    scaled_score = score / tf.math.sqrt(dim_key)
    weights = tf.nn.softmax(scaled_score, axis=-1)
    output = tf.matmul(weights, value)
    return output, weights

  def separate_heads(self, x, batch_size):
    x = tf.reshape(x, (batch_size, -1, self.num_heads, self.projection_dim))
    return tf.transpose(x, perm=[0, 2, 1, 3])

  def call(self, inputs):
    # x.shape = [batch_size, seq_len, embedding_dim]
    batch_size = tf.shape(inputs)[0]
    query = self.query_dense(inputs)  # (batch_size, seq_len, embed_dim)
    key = self.key_dense(inputs)  # (batch_size, seq_len, embed_dim)
    value = self.value_dense(inputs)  # (batch_size, seq_len, embed_dim)
    query = self.separate_heads(
        query, batch_size
    )  # (batch_size, num_heads, seq_len, projection_dim)
    key = self.separate_heads(
        key, batch_size
    )  # (batch_size, num_heads, seq_len, projection_dim)
    value = self.separate_heads(
        value, batch_size
    )  # (batch_size, num_heads, seq_len, projection_dim)
    attention, weights = self.attention(query, key, value)
    attention = tf.transpose(
        attention, perm=[0, 2, 1, 3]
    )  # (batch_size, seq_len, num_heads, projection_dim)
    concat_attention = tf.reshape(
        attention, (batch_size, -1, self.embed_dim)
    )  # (batch_size, seq_len, embed_dim)
    output = self.combine_heads(
        concat_attention
    )  # (batch_size, seq_len, embed_dim)
    return output


class TransformerBlock(tf.keras.layers.Layer):
  """Implement a Transformer block as a layer."""
  def __init__(self, embed_dim, num_heads, ff_dim, rate=0.1):
    super(TransformerBlock, self).__init__()
    self.att = MultiHeadSelfAttention(embed_dim, num_heads)
    self.ffn = tf.keras.Sequential(
        [tf.keras.layers.Dense(ff_dim, activation="relu"),
         tf.keras.layers.Dense(embed_dim)]
    )
    self.layernorm1 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
    self.layernorm2 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
    self.dropout1 = tf.keras.layers.Dropout(rate)
    self.dropout2 = tf.keras.layers.Dropout(rate)

  def call(self, inputs, training):
    attn_output = self.att(inputs)
    attn_output = self.dropout1(attn_output, training=training)
    out1 = self.layernorm1(inputs + attn_output)
    ffn_output = self.ffn(out1)
    ffn_output = self.dropout2(ffn_output, training=training)
    return self.layernorm2(out1 + ffn_output)


class TokenAndPositionEmbedding(tf.keras.layers.Layer):
  """Implement embedding layer."""
  def __init__(self, maxlen, vocab_size, embed_dim):
    super(TokenAndPositionEmbedding, self).__init__()
    self.token_emb = tf.keras.layers.Embedding(input_dim=vocab_size,
                                               output_dim=embed_dim)
    self.pos_emb = tf.keras.layers.Embedding(input_dim=maxlen,
                                             output_dim=embed_dim)

  def call(self, x):
    maxlen = tf.shape(x)[-1]
    positions = tf.range(start=0, limit=maxlen, delta=1)
    positions = self.pos_emb(positions)
    x = self.token_emb(x)
    return x + positions


if __name__ == '__main__':
  tf.test.main()
