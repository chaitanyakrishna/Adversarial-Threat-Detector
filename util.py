#!/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import string
import random
import configparser
import numpy as np
from datetime import datetime
from PIL import Image
from logging import getLogger, FileHandler, Formatter

# TensorFlow.
import tensorflow as tf
from tensorflow.keras.models import load_model
tf.compat.v1.disable_eager_execution()

# ART.
from art.estimators.classification import KerasClassifier

# Printing colors.
OK_BLUE = '\033[94m'      # [*]
NOTE_GREEN = '\033[92m'   # [+]
FAIL_RED = '\033[91m'     # [-]
WARN_YELLOW = '\033[93m'  # [!]
ENDC = '\033[0m'
PRINT_OK = OK_BLUE + '[*]' + ENDC
PRINT_NOTE = NOTE_GREEN + '[+]' + ENDC
PRINT_FAIL = FAIL_RED + '[-]' + ENDC
PRINT_WARN = WARN_YELLOW + '[!]' + ENDC

# Type of printing.
OK = 'ok'         # [*]
NOTE = 'note'     # [+]
FAIL = 'fail'     # [-]
WARNING = 'warn'  # [!]
NONE = 'none'     # No label.


# Utility class.
class Utilty:
    def __init__(self):
        # Read config.ini.
        full_path = os.path.dirname(os.path.abspath(__file__))
        config = configparser.ConfigParser()
        config.read(os.path.join(full_path, 'config.ini'))

        try:
            self.banner_delay = float(config['Common']['banner_delay'])
            self.report_date_format = config['Common']['date_format']
            self.log_dir = os.path.join(full_path, config['Common']['log_path'])
            os.makedirs(self.log_dir, exist_ok=True)
            self.log_file = config['Common']['log_file']
            self.log_path = os.path.join(self.log_dir, self.log_file)
            self.target_dir = os.path.join(full_path, config['Common']['target_path'])
            os.makedirs(self.target_dir, exist_ok=True)
        except Exception as e:
            self.print_message(FAIL, 'Reading config.ini is failure : {}'.format(e))
            sys.exit(1)

        # Setting logger.
        self.logger = getLogger('Adversarial Threat Detector')
        self.logger.setLevel(20)
        file_handler = FileHandler(self.log_path)
        self.logger.addHandler(file_handler)
        formatter = Formatter('%(levelname)s,%(message)s')
        file_handler.setFormatter(formatter)

    # Print metasploit's symbol.
    def print_message(self, type, message):
        if os.name == 'nt':
            if type == NOTE:
                print('[+] ' + message)
            elif type == FAIL:
                print('[-] ' + message)
            elif type == WARNING:
                print('[!] ' + message)
            elif type == NONE:
                print(message)
            else:
                print('[*] ' + message)
        else:
            if type == NOTE:
                print(PRINT_NOTE + ' ' + message)
            elif type == FAIL:
                print(PRINT_FAIL + ' ' + message)
            elif type == WARNING:
                print(PRINT_WARN + ' ' + message)
            elif type == NONE:
                print(NOTE_GREEN + message + ENDC)
            else:
                print(PRINT_OK + ' ' + message)

    # Print exception messages.
    def print_exception(self, e, message):
        self.print_message(WARNING, 'type:{}'.format(type(e)))
        self.print_message(WARNING, 'args:{}'.format(e.args))
        self.print_message(WARNING, '{}'.format(e))
        self.print_message(WARNING, message)

    # Normalization.
    def min_max(self, x, axis=None):
        x_min = x.min(axis=axis, keepdims=True)
        x_max = x.max(axis=axis, keepdims=True)
        return (x - x_min) / (x_max - x_min)

    # Checking one-hot-encoding for labels.
    def check_one_hot_encoding(self, labels):
        ret_status = True
        for label in labels:
            if label.sum() != 1:
                self.print_message(FAIL, 'label is not one-hot-encoding.')
                ret_status = False
                break
        return ret_status

    # Load model.
    def load_model(self, model_name):
        ret_status = True

        try:
            model_path = os.path.join(self.target_dir, model_name)
            if os.path.exists(model_path) is False:
                ret_status = False
                self.print_message(FAIL, 'Model path not Found: {}'.format(model_path))
                return ret_status, None, None
            else:
                model = load_model(model_path)
                self.print_message(OK, 'Loaded target model: {}'.format(model_path))
                return ret_status, model_path, model
        except Exception as e:
            ret_status = False
            self.print_exception(e, 'Could not load model: {}.'.format(model_path))
            return ret_status, None, None

    # Load dataset/label from npz.
    def load_dataset(self, dataset_name, label_name, use_dataset_num):
        ret_status = True

        dataset_path = os.path.join(self.target_dir, dataset_name)
        label_path = os.path.join(self.target_dir, label_name)
        if os.path.exists(dataset_path) is False or os.path.exists(label_path) is False:
            self.print_message(FAIL, 'Dataset or Label path not Found: {}/{}'.format(dataset_path, label_path))
            ret_status = False
            return ret_status, None, None, None, None
        else:
            try:
                # Load data.
                X_test = np.load(dataset_path)
                y_test = np.load(label_path)

                # Check dataset number.
                if len(X_test[X_test.files[0]]) < use_dataset_num:
                    use_dataset_num = len(X_test[X_test.files[0]])
                X_test = X_test[X_test.files[0]][:use_dataset_num]
                y_test = y_test[y_test.files[0]][:use_dataset_num]

                # Normalization.
                X_test = self.min_max(X_test)
                self.print_message(OK, 'Loaded dataset: {}'.format(dataset_path))

                # Check labels.
                if self.check_one_hot_encoding(y_test) is False:
                    ret_status = False
                    return ret_status, None, None, None, None
                else:
                    self.print_message(OK, 'Loaded label: {}'.format(label_path))

                return ret_status, dataset_path, label_path, X_test, y_test
            except Exception as e:
                ret_status = False
                self.print_exception(e, 'Could not load dataset: {}.'.format(dataset_path))
                return ret_status, None, None, None, None

    # Wrap classifier using ART.
    def wrap_classifier(self, model, X_test):
        ret_status = True
        try:
            mix_pixel_value = np.amin(X_test)
            max_pixel_value = np.amax(X_test)
            classifier = KerasClassifier(model=model,
                                         clip_values=(mix_pixel_value, max_pixel_value),
                                         use_logits=False)
            self.print_message(OK, 'Wrapped model using KerasClassifier.')
            return True, classifier
        except Exception as e:
            ret_status = False
            self.print_exception(e, 'Could not wrap classifier')
            return ret_status, None

    # Evaluate accuracy.
    def evaluate(self, model, X_test, y_test):
        ret_status = True
        try:
            preds = model.predict(X_test)
            accuracy = np.sum(np.argmax(preds, axis=1) == np.argmax(y_test, axis=1)) / len(y_test)
            return ret_status, accuracy
        except Exception as e:
            ret_status = False
            self.print_exception(e, 'Could not evaluate classifier.')
            return ret_status, None

    # Random sampling.
    def random_sampling(self, data_size=100, sample_num=5):
        sample_list = []
        for _ in range(sample_num):
            sample_list.append(random.randint(0, data_size - 1))
        return sample_list

    # Save Adversarial Examples to Image file.
    def save_adv_images(self, idx, method, X_adv, save_path):
        scale = 255.0 / np.max(X_adv)
        pil_img = Image.fromarray(np.uint8(X_adv * scale))
        save_full_path = os.path.join(save_path, 'adv_{}_{}.jpg'.format(method, idx+1))
        pil_img.save(save_full_path)
        self.print_message(OK, 'Saved Adversarial Examples to image file: {}'.format(save_full_path))
        return save_full_path

    # Save Adversarial Examples to npz format.
    def save_adv_npz(self, method, X_adv, save_path):
        save_full_path = os.path.join(save_path, 'adv_{}'.format(method))
        np.savez(save_full_path, adv=X_adv)
        self.print_message(OK, 'Saved Adversarial Examples to npz file: {}'.format(save_full_path))
        return save_full_path + '.npz'

    # Evaluation Evasion Attack.
    def evaluate_aes(self, attack_method, target_classifier, X_adv, y_test, acc_benign, sampling_idx, report_util):
        ret_status = True
        report_util.template_evasion[attack_method]['exist'] = True
        report_util.template_evasion[attack_method]['date'] = self.get_current_date()

        # Evaluation Adversarial Examples.
        ret_status, acc_adv = self.evaluate(target_classifier, X_test=X_adv, y_test=y_test)
        if ret_status is False:
            return ret_status, None

        self.print_message(WARNING, 'Accuracy on AEs ({})      : {}%'.format(attack_method, acc_adv * 100))
        aes_sample_list = report_util.make_image(X_adv, attack_method, sampling_idx)
        adv_path = self.save_adv_npz(attack_method, X_adv, report_util.report_path)
        report_util.template_evasion[attack_method]['aes_path'] = adv_path
        for (sample_path, elem) in zip(aes_sample_list, report_util.template_evasion[attack_method]['ae_img'].keys()):
            report_util.template_evasion[attack_method]['ae_img'][elem] = sample_path
        if acc_benign > acc_adv:
            report_util.template_evasion['consequence'] = 'Weak'
            report_util.template_evasion[attack_method]['consequence'] = 'Weak (Benign={}%, AEs={}%)'.format(
                acc_benign * 100,
                acc_adv * 100)
        return ret_status, report_util

    # Write logs.
    def write_log(self, loglevel, message):
        self.logger.log(loglevel, self.get_current_date() + ' ' + message)

    # Create random string.
    def get_random_token(self, length):
        chars = string.digits + string.ascii_letters
        return ''.join([random.choice(chars) for _ in range(length)])

    # Get current date.
    def get_current_date(self, indicate_format=None):
        if indicate_format is not None:
            date_format = indicate_format
        else:
            date_format = self.report_date_format
        return datetime.now().strftime(date_format)

    # Transform date from string to object.
    def transform_date_object(self, target_date, format=None):
        if format is None:
            return datetime.strptime(target_date, self.report_date_format)
        else:
            return datetime.strptime(target_date, format)

    # Transform date from object to string.
    def transform_date_string(self, target_date):
        return target_date.strftime(self.report_date_format)
