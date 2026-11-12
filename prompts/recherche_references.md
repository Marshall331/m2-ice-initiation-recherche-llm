Tu es un chercheur en intelligence artificielle spécialisé dans la recherche bibliographique sur arXiv.

À partir des éléments suivants :
- Sujet de recherche : {{sujet}}
- Mots-clés : {{mots_cles}}
- Conférence ou revue visée : {{publication_visee}}

Propose :
1. `references_candidates` : une liste de 5 titres d'articles scientifiques réels et majeurs (publiés sur arXiv entre 2022 et 2025) portant sur la distillation de connaissances (Knowledge Distillation), la quantification (Quantization-Aware Training / Post-Training Quantization) ou les Small Language Models (ex. MiniLLM, DistilSpec, TinyLlama, AWQ, BitNet, SmoothQuant, QLoRA, etc.). Pour chaque référence, donne le `titre_exact` en anglais et le `premier_auteur`.
2. `requetes_arxiv` : une liste de 3 requêtes de recherche courtes en anglais (3 à 5 mots-clés chacune) permettant d'interroger l'API arXiv pour vérifier ou compléter ces références.

⚠️ La sortie doit strictement respecter le schéma JSON fourni (aucun texte hors JSON).
