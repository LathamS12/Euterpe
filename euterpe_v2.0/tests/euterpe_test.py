import os
import sys

modules = f'C:/Users/Scott/Dropbox/Data_Science/Portfolio/euterpe_v2/modules'
sys.path.append(modules)

import unittest
from unittest.mock import patch
import pytest

import pygame
import pygame.midi
import pandas as pd

import euterpe_v2 as et
import music as music


@pytest.fixture
def quiz():
    quiz = music.Quiz()
    return quiz

def test_chord_quiz_ask_question_true(quiz):
    quiz.ask_question = True

    assert quiz.chord_spelling is not None
    assert quiz.answer is not None

def test_quiz_ask_question_false_input_correct(quiz, monkeypatch):
    quiz.ask_question = False
    quiz.answer = 'A major'
    quiz.chord_spelling = 'A B C#'
    monkeypatch.setattr(quiz.piano, 'get_pressed_k12', lambda: ['A', 'B', 'C#'])

    assert quiz.ask_question

def test_quiz_ask_question_false_input_incorrect(quiz, monkeypatch):
    quiz.ask_question = False
    quiz.answer = 'A major'
    quiz.chord_spelling = 'A B C#'
    monkeypatch.setattr(quiz.piano, 'get_pressed_k12', lambda: ['A', 'B', 'D'])

    assert not quiz.ask_question