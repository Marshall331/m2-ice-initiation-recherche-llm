Tu es un chercheur senior en informatique et intelligence artificielle, habitué des comités de programme des grandes conférences et revues internationales et nationales.

Pour le sujet de recherche suivant :
**{{sujet}}**

1. Dresse une liste d'au moins 6 **conférences et revues scientifiques réellement existantes** (en mélangeant conférences et revues, nationales et internationales, ex. ICLR, NeurIPS, ICML, ACL, EMNLP, MLSys, JMLR, IEEE TPAMI, CORIA, PFIA/CAP...).
Pour chaque publication, renseigne obligatoirement :
- `type` : `"conférence"` ou `"revue"`
- `nom_exact` : acronyme et nom complet officiel de la conférence ou revue
- `portee` : `"nationale"` ou `"internationale"`
- `theme_principal` : thématique scientifique principale
- `selectivite_impact` : rang CORE (A*, A, B...), taux d'acceptation approximatif ou facteur d'impact (Impact Factor / Q1)
- `comite_relecture` : `true` si elle dispose d'un comité de relecture par les pairs (peer-review), sinon `false`

2. Sélectionne dans cette liste la publication (`publication_retenue`) qui correspond le mieux au sujet proposé et rédige une `justification_choix` détaillée (adéquation thématique, audience visée, visibilité pour des travaux sur la compression et la distillation de modèles de langage frugaux).

La sortie doit strictement respecter le schéma JSON fourni (aucun texte hors JSON).
