import librosa
import numpy as np
import configparser
import pickle
"""file containing the predict functions for the DiCOVA baseline models, adapted from the DiCOVA baseline code"""


def compute_mfcc(s, config):
    """
    computes the mfcc coefficients of s and their deltas
    :param s: audio to compute
    :param config: configuration to use
    :return: concatenated mfccs and their deltas and ddeltas
    """
    # computes MFCC of s as defined in the dicova baseline code
    mfcc = librosa.feature.mfcc(s, sr=int(config['default']['sampling_rate']),
                             n_mfcc=int(config['mfcc']['n_mfcc']),
                             n_fft=int(config['default']['window_size']),
                             hop_length=int(config['default']['window_shift']),
                             n_mels=int(config['mfcc']['n_mels']),
                             fmax=int(config['mfcc']['fmax']))

    features = np.array(mfcc)
    if config['mfcc']['add_deltas'] in ['True', 'true', 'TRUE', '1']:
        deltas = librosa.feature.delta(mfcc)
        features = np.concatenate((features, deltas), axis=0)

    if config['mfcc']['add_delta_deltas'] in ['True', '∞true', 'TRUE', '1']:
        ddeltas = librosa.feature.delta(mfcc, order=2)
        features = np.concatenate((features, ddeltas), axis=0)

    return features


def predict(input_audio):
    """
    predicts the output score for a batch of audio files
    :param input_audio: list of audio files to predict
    :return: np.array(n,1) of scores for input audio
    """
    # predicts output label for batch_size audios at a time
    # based on dicova baseline code, slightly adapted for audioLIME
    # TODO: adapt paths
    this_config = '/Users/anne/Documents/Uni/Robotics/Masterarbeit/MA_Code/DICOVA/DiCOVA_baseline/conf/feature.conf'
    path_model = '/Users/anne/Documents/Uni/Robotics/Masterarbeit/MA_Code/DICOVA/DiCOVA_baseline/results_lr/fold_1/model.pkl'

    config = configparser.ConfigParser()
    config.read(this_config)

    file_model = open(path_model, 'rb')
    rf_model = pickle.load(file_model)

    if isinstance(input_audio, list) or len(np.shape(input_audio)) > 1:
        # various files, need loop
        batch_size = len(input_audio)
        labels = np.zeros((batch_size, 1))
        for i, audio in enumerate(input_audio):
            mfcc = compute_mfcc(audio, config)

            score = rf_model.validate([mfcc.T])
            score = np.mean(score[0], axis=0)[1]
            labels[i, 0] = score
    else:
        # just predict on single file
        mfcc = compute_mfcc(input_audio, config)
        score = rf_model.validate([mfcc.T])
        labels = np.mean(score[0], axis=0)[1]
    return labels
