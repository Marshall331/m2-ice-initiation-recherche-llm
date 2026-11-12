# Initiation à la Recherche (M2 ICE) — Agent LLM & IA Frugale

Projet d'**Initiation à la recherche** (Master 2 ICE — Université Toulouse - Jean Jaurès / IRIT) simulant l'intégralité d'un workflow de recherche scientifique en Intelligence Artificielle à l'aide d'un LLM (`OpenRouter`), de schémas structurés **Pydantic**, de l'API officielle **arXiv** et d'un **Agent autonome** outillé (`Tool`).

## 🎯 Sujet de recherche étudié
> **Compression et distillation de grands modèles de langage (Small Language Models) pour l'exécution locale à faible consommation énergétique**

### Équipe de recherche (simulation IRIT — UMR 5505)
- **Doctorante :** Camille Lefèvre (Master 2 ICE)
- **Encadrants :**
  - **Brahim HAMID** — Professeur des Universités (HDR), directeur de thèse (IRIT, UMR 5505)
  - **Sophie EBERSOLD** — Maîtresse de Conférences, co-encadrante (IRIT, UMR 5505)
  - **Rémi BOULE** — Maître de Conférences, co-encadrant (IRIT, UMR 5505)
- **Conférence visée :** *MLSys — Conference on Machine Learning and Systems*

---

## 📁 Structure du dépôt

- `initiation recherche.ipynb` : Notebook principal contenant les 8 étapes du projet (création de l'équipe, sélection de la conférence, vérification et extraction des PDF sur arXiv, génération de l'introduction et de l'abstract, export PDF, analyse critique, agent autonome avec état partagé `etat`, et autoévaluation).
- `prompts/` : L'ensemble des prompts système, gabarits paramétrés (`{{...}}`) et descriptions d'outils au format Markdown (1 prompt = 1 fichier `.md`).
- `llm/` : Bibliothèque Python d'interfaçage avec OpenRouter (`OpenModel`, `ModelMessage`, `Prompt`, `Tool`).
- `article_intro.md` & `article_intro.pdf` : Article scientifique généré étape par étape (Parties 1 à 5).
- `article_agent.md` & `article_agent.pdf` : Article scientifique produit et sauvegardé de bout en bout par l'**Agent autonome** (Partie 7).
