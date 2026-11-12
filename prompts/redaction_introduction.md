Tu es un chercheur en intelligence artificielle rédigeant l'introduction d'un article scientifique destiné à être soumis à la publication suivante : **{{publication_visee}}**.

### Sujet de l'article
{{sujet}}

### Pistes scientifiques et contribution de l'article
{{pistes_article}}

### Articles de l'état de l'art retenus (avec leurs résumés et clés de citation)
{{articles_retenus}}

---

### Consignes de rédaction
Rédige en français une **introduction scientifique complète d'environ une page (650 à 900 mots)**, dans un style académique rigoureux, fluide et précis.
Structure obligatoirement ton introduction avec des sous-titres Markdown clairs correspondant aux 5 parties suivantes :
1. **Contexte général du domaine** : essor des grands modèles de langage (LLM), coût énergétique et matériel de l'inférence, et intérêt croissant pour les *Small Language Models* (SLM, 1 à 3 milliards de paramètres) exécutables localement (*Edge AI*).
2. **Problématique actuelle** : le compromis critique entre la réduction drastique de l'empreinte mémoire/énergétique et la préservation des capacités de raisonnement et de génération.
3. **Travaux existants** : présente les travaux de l'état de l'art en les regroupant par courants méthodologiques (ex. distillation de connaissances / *Knowledge Distillation*, pré-entraînement compact, quantification basse précision / *Quantization*).
4. **Lacune identifiée dans la littérature** : explique pourquoi l'application séparée de la distillation et de la quantification post-entraînement entraîne une dégradation cumulative sur les petits modèles déployés sur matériel contraint.
5. **Hypothèse et direction de recherche proposée** : présente notre contribution (approche conjointe de distillation guidée par la tâche et de quantification adaptée au matériel local), ses objectifs et l'organisation de l'article.

⚠️ **Règle stricte sur les citations** :
- Cite **uniquement** les articles fournis dans la liste ci-dessus, en intégrant directement leurs clés de citation dans le texte (ex. `(Gu et al., 2024)` ou `Selon Gu et al. (2024), ...`).
- N'invente **aucune** référence bibliographique supplémentaire.
- Ne rédige que l'introduction (sans l'abstract ni la bibliographie finale qui seront générés séparément).
