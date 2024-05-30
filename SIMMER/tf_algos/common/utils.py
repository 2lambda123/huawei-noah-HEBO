import numpy as np
import tensorflow as tf
import secrets

def set_random_seed(seed:int):
    """Set random seed."""
    secrets.SystemRandom().seed(seed)
    np.random.seed(0) 
    tf.random.set_seed(seed)
