# Copyright 2019 The Sonnet Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or  implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================

"""Tests for sonnet.v2.src.momentum."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl.testing import parameterized
from sonnet.src import momentum as opt
from sonnet.src import test_utils
import tensorflow as tf


class MomentumTest(test_utils.TestCase, parameterized.TestCase):

  @parameterized.parameters(opt.Momentum, opt.FastMomentum)
  def testDense(self, opt_class):
    parameters = [tf.Variable([1., 2.]), tf.Variable([3., 4.])]
    updates = [tf.constant([5., 5.]), tf.constant([3., 3.])]
    optimizer = opt_class(learning_rate=0.1, momentum=0.9)
    # Step 1 of Momentum
    optimizer.apply(updates, parameters)
    self.assertAllClose([[0.5, 1.5], [2.7, 3.7]],
                        [x.numpy() for x in parameters])
    # Step 2 of Momentum
    optimizer.apply(updates, parameters)
    self.assertAllClose([[-0.45, 0.55], [2.13, 3.13]],
                        [x.numpy() for x in parameters])
    # Step 3 of Momentum
    optimizer.apply(updates, parameters)
    self.assertAllClose([[-1.805, -0.805], [1.317, 2.317]],
                        [x.numpy() for x in parameters])

  @parameterized.parameters(opt.Momentum, opt.FastMomentum)
  def testDenseNesterov(self, opt_class):
    parameters = [tf.Variable([1., 2.]), tf.Variable([3., 4.])]
    updates = [tf.constant([5., 5.]), tf.constant([3., 3.])]
    optimizer = opt_class(learning_rate=0.1, momentum=0.9, use_nesterov=True)
    # Step 1 of Momentum
    optimizer.apply(updates, parameters)
    self.assertAllClose([[0.05, 1.05], [2.43, 3.43]],
                        [x.numpy() for x in parameters])
    # Step 2 of Momentum
    optimizer.apply(updates, parameters)
    self.assertAllClose([[-1.305, -0.305], [1.617, 2.617]],
                        [x.numpy() for x in parameters])
    # Step 3 of Momentum
    optimizer.apply(updates, parameters)
    self.assertAllClose([[-3.0245, -2.0245], [0.5853, 1.5853]],
                        [x.numpy() for x in parameters])

  @parameterized.parameters(opt.Momentum, opt.FastMomentum)
  def testSparse(self, opt_class):
    if self.primary_device in ("GPU", "TPU"):
      self.skipTest("IndexedSlices not supported on {}.".format(
          self.primary_device))

    parameters = [tf.Variable([[1.], [2.]]), tf.Variable([[3.], [4.]])]
    updates = [tf.IndexedSlices(tf.constant([0.1], shape=[1, 1]),
                                tf.constant([0]), tf.constant([2, 1])),
               tf.IndexedSlices(tf.constant([0.01], shape=[1, 1]),
                                tf.constant([1]), tf.constant([2, 1]))]
    optimizer = opt_class(learning_rate=3., momentum=0.9)
    # Step 1 of Momentum
    optimizer.apply(updates, parameters)
    self.assertAllClose([[1.0 - 3.0 * 0.1], [2.0]], parameters[0].numpy())
    self.assertAllClose([[3.0], [4.0 - 3.0 * 0.01]], parameters[1].numpy())
    # Step 2 of Momentum
    optimizer.apply(updates, parameters)
    self.assertAllClose([[0.7 - 3.0 * 0.19], [2.0]], parameters[0].numpy())
    self.assertAllClose([[3.0], [3.97 - 3.0 * 0.019]], parameters[1].numpy())
    # Step 3 of Momentum
    optimizer.apply(updates, parameters)
    self.assertAllClose([[0.13 - 3.0 * 0.271], [2.0]], parameters[0].numpy())
    self.assertAllClose([[3.0], [3.913 - 3.0 * 0.0271]], parameters[1].numpy())

  @parameterized.parameters(opt.Momentum, opt.FastMomentum)
  def testSparseNesterov(self, opt_class):
    if self.primary_device in ("GPU", "TPU"):
      self.skipTest("IndexedSlices not supported on {}.".format(
          self.primary_device))

    parameters = [tf.Variable([[1.], [2.]]), tf.Variable([[3.], [4.]])]
    updates = [tf.IndexedSlices(tf.constant([0.1], shape=[1, 1]),
                                tf.constant([0]), tf.constant([2, 1])),
               tf.IndexedSlices(tf.constant([0.01], shape=[1, 1]),
                                tf.constant([1]), tf.constant([2, 1]))]
    optimizer = opt_class(learning_rate=3., momentum=0.9, use_nesterov=True)
    # Step 1 of Momentum
    optimizer.apply(updates, parameters)
    self.assertAllClose([[0.43], [2.0]], parameters[0].numpy())
    self.assertAllClose([[3.0], [3.943]], parameters[1].numpy())
    # Step 2 of Momentum
    optimizer.apply(updates, parameters)
    self.assertAllClose([[-0.383], [2.0]], parameters[0].numpy())
    self.assertAllClose([[3.0], [3.8617]], parameters[1].numpy())
    # Step 3 of Momentum
    optimizer.apply(updates, parameters)
    self.assertAllClose([[-1.4147], [2.0]], parameters[0].numpy())
    self.assertAllClose([[3.0], [3.75853]], parameters[1].numpy())

  @parameterized.parameters(opt.Momentum, opt.FastMomentum)
  def testNoneUpdate(self, opt_class):
    parameters = [tf.Variable([1., 2.])]
    updates = [None]
    optimizer = opt_class(learning_rate=0.1, momentum=0.9)
    optimizer.apply(updates, parameters)
    self.assertAllClose([[1., 2.]], [x.numpy() for x in parameters])

  @parameterized.parameters(opt.Momentum, opt.FastMomentum)
  def testVariableHyperParams(self, opt_class):
    parameters = [tf.Variable([1., 2.]), tf.Variable([3., 4.])]
    updates = [tf.constant([5., 5.]), tf.constant([3., 3.])]
    learning_rate = tf.Variable(0.1)
    momentum = tf.Variable(0.9)
    optimizer = opt_class(learning_rate=learning_rate, momentum=momentum)
    optimizer.apply(updates, parameters)
    self.assertAllClose([[0.5, 1.5], [2.7, 3.7]],
                        [x.numpy() for x in parameters])
    learning_rate.assign(0.01)
    momentum.assign(0.09)
    self.assertAlmostEqual(0.01, optimizer.learning_rate.numpy())
    self.assertAlmostEqual(0.09, optimizer.momentum.numpy())
    optimizer.apply(updates, parameters)
    self.assertAllClose([[0.4455, 1.4455], [2.6673, 3.6673]],
                        [x.numpy() for x in parameters])

  @parameterized.parameters(opt.Momentum, opt.FastMomentum)
  def testHyperParamDTypeConversion(self, opt_class):
    parameters = [tf.Variable([1., 2.]), tf.Variable([3., 4.])]
    updates = [tf.constant([5., 5.]), tf.constant([3., 3.])]
    dtype = tf.float32 if self.primary_device == "TPU" else tf.float64
    learning_rate = tf.Variable(0.1, dtype=dtype)
    momentum = tf.Variable(0.9, dtype=dtype)
    optimizer = opt_class(learning_rate=learning_rate, momentum=momentum)
    optimizer.apply(updates, parameters)
    self.assertAllClose([[0.5, 1.5], [2.7, 3.7]],
                        [x.numpy() for x in parameters])

  @parameterized.parameters(opt.Momentum, opt.FastMomentum)
  def testDifferentLengthUpdatesParams(self, opt_class):
    parameters = [tf.Variable([1., 2.]), tf.Variable([3., 4.])]
    updates = [tf.constant([5., 5.])]
    optimizer = opt_class(learning_rate=0.1, momentum=0.9)
    with self.assertRaisesRegexp(
        ValueError, "`updates` and `parameters` must be the same length."):
      optimizer.apply(updates, parameters)

  @parameterized.parameters(opt.Momentum, opt.FastMomentum)
  def testEmptyParams(self, opt_class):
    optimizer = opt_class(learning_rate=0.1, momentum=0.9)
    with self.assertRaisesRegexp(ValueError, "`parameters` cannot be empty."):
      optimizer.apply([], [])

  @parameterized.parameters(opt.Momentum, opt.FastMomentum)
  def testInconsistentDTypes(self, opt_class):
    parameters = [tf.Variable([1., 2.], name="param0")]
    updates = [tf.constant([5, 5])]
    optimizer = opt_class(learning_rate=0.1, momentum=0.9)
    with self.assertRaisesRegexp(
        ValueError, "DType of .* is not equal to that of parameter .*param0.*"):
      optimizer.apply(updates, parameters)

  @parameterized.parameters(opt.Momentum, opt.FastMomentum)
  def testAccumulatorVariablesColocatedWithOriginal(self, opt_class):
    optimizer = opt_class(learning_rate=0.1, momentum=0.9)
    with tf.device("CPU:0"):
      var = tf.Variable(1.0)
    optimizer.apply([tf.constant(0.1)], [var])
    self.assertEqual(optimizer.accumulated_momentum[0].device, var.device)

  @parameterized.parameters(opt.Momentum, opt.FastMomentum)
  def testUnsuppportedStrategyError(self, opt_class):
    strategy = tf.distribute.MirroredStrategy()
    with strategy.scope():
      var = tf.Variable(1.0)
      optimizer = opt_class(learning_rate=0.1, momentum=0.9)
    step = lambda: optimizer.apply([tf.constant(0.1)], [var])
    with self.assertRaisesRegexp(
        ValueError,
        "Sonnet optimizers are not compatible with `MirroredStrategy`"):
      strategy.experimental_run_v2(step)

if __name__ == "__main__":
  # tf.enable_v2_behavior()
  tf.test.main()
