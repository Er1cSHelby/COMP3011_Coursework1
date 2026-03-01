# PokeVault API - COMP3011 Coursework 1

## Project Overview
**Student Name:** Yichen Huang
**Student ID:** 201656189

This project is a RESTful Web API designed for the *COMP3011: Web Services and Web Data* module. It serves as a backend system for a Pokémon Trading Card Game (TCG) collection manager.

The API allows users to:
* Manage a personal collection of cards (Create, Read, Update, Delete).
* View reference data for Pokémon cards (fetched from external sources).
* Filter cards by set or name.
* Track specific details like card condition (e.g., Mint, Played) and quantity.

I chose **Django** and **Django REST Framework (DRF)** for this project because they provide a robust, standard architecture for handling relational databases and object serialization, which aligns with the module's teaching on Model-View-Controller (MVC/MVT) patterns.

## Tech Stack
* **Language:** Python 3.10+
* **Framework:** Django 5.0, Django REST Framework 3.14
* **Database:** SQLite (default for local development)
* **External Integration:** `requests` library used to fetch real card data from the Pokémon TCG IO API.

