from dataclasses import dataclass
from typing import List
from game import Direction

class CardInfo:
    '''
    Information about a card in the game.

    Attributes:
        name: The name of the card.
        attack: The attack value of the card.
        defense: The defense value of the card.
        directions: The directions this card "overpowers". 
            When attacking: the card ignores the defense of the cards in these directions. If the card being attacked doesn't have a defense in the opposite direction, the attack is automatically successful. Otherwise, the outcome depends on a coin toss.
            When defending: the card ignores the attack of the cards in these directions. If the card being attacked doesn't have an attack in the opposite direction, the attack is automatically failed. Otherwise, the outcome depends on a coin toss.
    '''
    def __init__(self, name: str = "Unknown", attack: int = -1, defense: int = -1, directions: List[Direction] = []):
        self.name = name
        self.attack = attack
        self.defense = defense
        self.directions = directions

    def __str__(self):
        return f"{self.name} (🗡️{self.attack}/🛡️{self.defense})"

    def __repr__(self):
        return str(self)


# Engineer

# Tetraodd

# Itica

# Scarabara

# Mysterious Dagger

# Irontalon

# Dark Troopers

# Spiderbot

# Kaktos

# Gillman Warriors

# Galactoss

# Arcadian Soldiers

# Owru Bandit

# Security Drone

# The Flute

# Dropship

# Knight

# Bot Warriors

# Cepede

# Ghost

# Chief of the Eye Clan

# Prototype Spiderbot

# Caster Gun

# Dark Commander

# Paradigm Hourglass

# Shield of Chronos

# Steelscale

# Guardian

# Princess Fin

# Yellow Bird

# Dark Apostle

# Yurmala Turtle

# Thunderstone

# Firebird

# Gen

# Astroblade

# The Shadow

# Master Mayfair

# Sealurk

# Dark Chariot

# The Great Chronicler

# Hero

# Everturso

# Archimedes

# Mesmeroth

# Trin

# Oceanhorn

# TRILOTH

# Sacred Emblems

ALL_CARDS = [
    CardInfo(name="Training Dummy", attack=1, defense=6),
    CardInfo(name="Engineer", attack=4, defense=3),
    CardInfo(name="Tetrapod", attack=3, defense=4),
    CardInfo(name="Itica", attack=2, defense=4),
    CardInfo(name="Scarabara", attack=5, defense=2),
    CardInfo(name="Irontalon", attack=4, defense=6),
    CardInfo(name="Dark Troopers", attack=5, defense=4),
    CardInfo(name="Spiderbot", attack=3, defense=7),
    CardInfo(name="Kaktos", attack=5, defense=4, directions=[Direction.UP]),
    CardInfo(name="Gillman Warriors", attack=4, defense=7),
    CardInfo(name="Galactoss", attack=6, defense=4, directions=[Direction.DOWN]),
    CardInfo(name="Arcadian Soldiers", attack=5, defense=6),
    CardInfo(name="Owru Bandit", attack=6, defense=5),
    CardInfo(name="Security Drone", attack=7, defense=4),
    CardInfo(name="Ghost", attack=6, defense=7),
]

name_to_cardinfo = {card.name: card for card in ALL_CARDS}