#!/usr/bin/env python3  
# -*- coding: utf-8 -*-
# Filename: quiz.py
# Author: Osei- Agyei Rosemond Sarpongmaa (Rose Agyei)
#Collaborators:Tetteh Wayo Willhermina,Sallah Prince Selasi, Agbenyegah Gabriel, Agbaglo Romeo
# Date: 10-08-2025

"""
Project: Quizy Pop Quiz (Quiz Web Application Project)
A modern, responsive web-based quiz application built with Python and Flask.
Test your knowledge across various topics including general knowledge, sports,history,
geography, and programming with an intuitive interface and comprehensive feedback system.
"""

class Question:
    def __init__(self, text,options,correct_option):
        self.text = text
        self.options = options
        self.correct_option = correct_option 

class Quiz:
    def __init__(self):
        self.questions=[]     

    def add_question(self,question):
        self.questions.append(question)  
