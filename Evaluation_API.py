#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  2 04:12:42 2024

@author: mateodib
"""


import os
import replicate
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from langchain import PromptTemplate

# Load the phrases and extracted sections from the file rag_results.csv
def charger_rag_results(chemin_rag_csv):
    return pd.read_csv(chemin_rag_csv)

# Save evaluation results to a CSV file
def sauvegarder_resultats_evaluation(resultats, chemin_resultats_csv):
    resultats.to_csv(chemin_resultats_csv, index=False)
    print(f"Résultats d'évaluation sauvegardés dans {chemin_resultats_csv}")

def creer_prompts():
    prompts = {
        "accuracy": PromptTemplate(
            template="""
            Vous êtes chargé de comparer un extrait d'un article de presse aux informations officielles du rapport du GIEC.
            Évaluez l'exactitude de cet extrait en fonction des sections du rapport fournies. Utilisez l'échelle suivante :

            - **Score 0** : Totalement inexact, contredit directement les informations du rapport.
            - **Score 1** : Très inexact, contient plusieurs erreurs ou omissions importantes par rapport au rapport.
            - **Score 2** : Partiellement inexact, quelques erreurs importantes, mais certaines informations sont correctes.
            - **Score 3** : Modérément exact, contient des informations correctes mais avec quelques imprécisions.
            - **Score 4** : Largement exact, avec seulement de légères imprécisions.
            - **Score 5** : Parfaitement exact, correspond pleinement aux informations du rapport.

            **Extrait de l'article** :
            "{current_phrase}"

            **Sections du rapport du GIEC** :
            "{sections_resumees}"
            
            Répondez au format suivant en JSON:
            ```json
            {{
                "score": <score_entre_0_et_5>,
                "justifications": "<votre_justification_en_une_ou_plusieurs_phrases>"
            }}
            ```
            """,
            input_variables=["current_phrase", "sections_resumees"]
        ),
        "bias": PromptTemplate(
            template="""
            Vous êtes chargé d'analyser un extrait d'un article de presse pour détecter tout biais potentiel en fonction des sections du rapport du GIEC. Utilisez l'échelle suivante :

            - **Score 0** : Fortement biaisé, présente une vision totalement exagérée ou minimisée.
            - **Score 1** : Biaisé, avec une inclinaison évidente, soit en exagérant soit en minimisant les faits.
            - **Score 2** : Modérément biaisé, certains aspects exagérés ou minimisés mais dans l’ensemble équilibré.
            - **Score 3** : Légèrement biaisé, de petites nuances de biais mais globalement équilibré.
            - **Score 4** : Largement neutre, avec très peu de biais.
            - **Score 5** : Totalement neutre, sans aucun biais détectable.

            **Extrait de l'article** :
            "{current_phrase}"

            **Sections du rapport du GIEC** :
            "{sections_resumees}"

            Répondez au format suivant en JSON:
            ```json
            {{
                "score": <score_entre_0_et_5>,
                "justifications": "<votre_justification_en_une_ou_plusieurs_phrases>"
            }}
            ```
            """,
            input_variables=["current_phrase", "sections_resumees"]
        ),
        "tone": PromptTemplate(
            template="""
            Vous êtes chargé d'analyser le ton d'un extrait d'un article de presse en le comparant aux informations du rapport du GIEC. Utilisez l'échelle suivante :

            - **Score 0** : Ton fortement alarmiste ou minimisant, très éloigné du ton neutre.
            - **Score 1** : Ton exagérément alarmiste ou minimisant.
            - **Score 2** : Ton quelque peu alarmiste ou minimisant.
            - **Score 3** : Ton modérément factuel avec une légère tendance à l'alarmisme ou à la minimisation.
            - **Score 4** : Ton largement factuel, presque totalement neutre.
            - **Score 5** : Ton complètement neutre et factuel, sans tendance perceptible.

            **Extrait de l'article** :
            "{current_phrase}"

            **Sections du rapport du GIEC** :
            "{sections_resumees}"

            Répondez au format suivant en JSON:
            ```json
            {{
                "score": <score_entre_0_et_5>,
                "justifications": "<votre_justification_en_une_ou_plusieurs_phrases>"
            }}
            ```
            """,
            input_variables=["current_phrase", "sections_resumees"]
        ),
        "clarity": PromptTemplate(
            template="""
            Vous êtes chargé d'évaluer la clarté et la lisibilité d'un extrait d'un article de presse en fonction de sa simplicité et de son accessibilité. Utilisez l'échelle suivante :

            - **Score 0** : Très confus, difficile à lire et à comprendre.
            - **Score 1** : Peu clair, nécessite beaucoup d'efforts pour comprendre.
            - **Score 2** : Assez clair, mais certaines phrases ou idées sont difficiles à suivre.
            - **Score 3** : Modérément clair, quelques passages pourraient être simplifiés.
            - **Score 4** : Largement clair, facile à lire avec une structure compréhensible.
            - **Score 5** : Parfaitement clair, très facile à lire et accessible à tous les lecteurs.

            **Extrait de l'article** :
            "{current_phrase}"

            Répondez au format suivant en JSON:
            ```json
            {{
                "score": <score_entre_0_et_5>,
                "justifications": "<votre_justification_en_une_ou_plusieurs_phrases>"
            }}
            ```
            """,
            input_variables=["current_phrase"]
        ),
        "completeness": PromptTemplate(
            template="""
            Vous êtes chargé d'évaluer la complétude de l'information contenue dans un extrait d'un article de presse par rapport aux sections du rapport du GIEC. Utilisez l'échelle suivante :

            - **Score 0** : Très incomplet, de nombreuses informations importantes sont manquantes.
            - **Score 1** : Incomplet, plusieurs points essentiels ne sont pas couverts.
            - **Score 2** : Partiellement complet, des informations importantes sont manquantes mais certains éléments sont présents.
            - **Score 3** : Modérément complet, couvre l'essentiel mais manque de détails.
            - **Score 4** : Largement complet, contient presque toutes les informations nécessaires.
            - **Score 5** : Complètement complet, toutes les informations importantes sont présentes.

            **Extrait de l'article** :
            "{current_phrase}"

            **Sections du rapport du GIEC** :
            "{sections_resumees}"

            Répondez au format suivant en JSON:
            ```json
            {{
                "score": <score_entre_0_et_5>,
                "justifications": "<votre_justification_en_une_ou_plusieurs_phrases>"
            }}
            ```
            """,
            input_variables=["current_phrase", "sections_resumees"]
        ),
        "objectivity": PromptTemplate(
            template="""
            Vous êtes chargé d'évaluer l'objectivité d'un extrait d'un article de presse en vérifiant s'il est libre de langage subjectif ou d'opinions. Utilisez l'échelle suivante :

            - **Score 0** : Très subjectif, plein d'opinions ou de langages émotifs.
            - **Score 1** : Subjectif, contient des opinions ou un langage non neutre.
            - **Score 2** : Modérément subjectif, quelques opinions ou expressions biaisées.
            - **Score 3** : Légèrement subjectif, quelques nuances de subjectivité mais largement objectif.
            - **Score 4** : Largement objectif, avec très peu de subjectivité.
            - **Score 5** : Totalement objectif, sans aucune opinion ou langage subjectif.

            **Extrait de l'article** :
            "{current_phrase}"

            **Sections du rapport du GIEC** :
            "{sections_resumees}"

            Répondez au format suivant en JSON:
            ```json
            {{
                "score": <score_entre_0_et_5>,
                "justifications": "<votre_justification_en_une_ou_plusieurs_phrases>"
            }}
            ```
            """,
            input_variables=["current_phrase", "sections_resumees"]
        ),
        "alignment": PromptTemplate(
            template="""
            Vous êtes chargé d'évaluer si cet extrait d'un article de presse reflète bien les priorités et l'importance des points soulignés dans les sections du rapport du GIEC. Utilisez l'échelle suivante :

            - **Score 0** : Complètement désaligné avec les priorités du rapport.
            - **Score 1** : Largement désaligné, manque les points principaux.
            - **Score 2** : Partiellement aligné, couvre quelques points mais ignore des éléments essentiels.
            - **Score 3** : Modérément aligné, couvre l'essentiel mais manque de priorisation.
            - **Score 4** : Largement aligné, avec une bonne couverture des priorités.
            - **Score 5** : Parfaitement aligné avec les priorités et l'importance du rapport.

            **Extrait de l'article** :
            "{current_phrase}"

            **Sections du rapport du GIEC** :
            "{sections_resumees}"

            Répondez au format suivant en JSON:
            ```json
            {{
                "score": <score_entre_0_et_5>,
                "justifications": "<votre_justification_en_une_ou_plusieurs_phrases>"
            }}
            ```
            """,
            input_variables=["current_phrase", "sections_resumees"]
        )
    }
    return prompts

# Helper function to call Replicate API for a specific metric
def appeler_replicate(prompt_text):
    input_payload = {
        "prompt": prompt_text,
        "max_tokens": 1000
    }
    try:
        output = replicate.run("meta/meta-llama-3-70b-instruct", input=input_payload)
        return "".join(output)  # Join the response segments into a single text
    except Exception as e:
        print(f"Erreur lors de l'appel à Replicate : {e}")
        return "Erreur de l'API Replicate"

# Evaluate a specific phrase for all seven metrics using dedicated models
def evaluer_phrase_toutes_metrices(phrase_id, question, current_phrase, sections_resumees, prompts):
    evaluations = {}
    
    # Iterate over each metric and apply its specific LLM prompt
    for metric, prompt_template in prompts.items():
        prompt_text = prompt_template.format(current_phrase=current_phrase, sections_resumees=sections_resumees)
        evaluations[metric] = appeler_replicate(prompt_text)

    # Return results for this phrase with id and question
    return {
        "id": phrase_id,
        "question": question,
        "current_phrase": current_phrase,
        "sections_resumees": sections_resumees,
        **evaluations
    }

# Function to evaluate phrases in parallel for all metrics
def evaluer_phrase_parallele(rag_df, prompts):
    results = []
    
    # Use ThreadPoolExecutor to execute multiple evaluations in parallel
    with ThreadPoolExecutor(max_workers=7) as executor:
        futures = []
        
        for _, row in rag_df.iterrows():
            phrase_id = row['id']
            question = row['question']
            current_phrase = row['current_phrase']
            sections_resumees = row['sections_resumees']
            
            # Submit the evaluation for all metrics
            futures.append(executor.submit(
                evaluer_phrase_toutes_metrices,
                phrase_id, question, current_phrase, sections_resumees,
                prompts
            ))
        
        # Retrieve results as tasks complete
        for future in tqdm(as_completed(futures), total=len(futures), desc="Évaluation des phrases pour toutes les métriques"):
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                print(f"Erreur lors de l'évaluation d'une phrase : {exc}")
    
    return pd.DataFrame(results)

# Main function to process evaluation
def process_evaluation_api(chemin_questions_csv, rag_csv, resultats_csv):
    # Load rag_results.csv
    rag_df = charger_rag_results(rag_csv)
    
    # Load final_climate_analysis_with_questions.csv with only 'id' and 'current_phrase' columns
    questions_df = pd.read_csv(chemin_questions_csv, usecols=['id', 'current_phrase'])
    
    # Merge rag_df with questions_df on 'id' to add the 'current_phrase' column
    rag_df = rag_df.merge(questions_df, on='id', how='left')
    
    # Create prompt templates for each metric
    prompts = creer_prompts()
    
    # Set up the Replicate API key
    os.environ["REPLICATE_API_TOKEN"] = "r8_KVdlDIHTh9T6xEuEJhDkNxvfCXleqe814zH72"
    replicate.api_token = os.getenv("REPLICATE_API_TOKEN")

    # Evaluate phrases for all metrics
    resultats = evaluer_phrase_parallele(rag_df, prompts)
    
    # Save results
    sauvegarder_resultats_evaluation(resultats, resultats_csv)


"""

# Create prompt templates for each metric with enhanced evaluation criteria
def creer_prompts():
    prompts = {
        "tone_and_relevance": PromptTemplate(
            template=""
            Vous êtes chargé d'évaluer le ton et la pertinence d'un extrait d'un article de presse en fonction des informations du rapport du GIEC. Cette évaluation inclut à la fois le type de ton (alarmiste, minimisant, ou neutre) et la pertinence du contenu par rapport aux priorités du rapport.

            **Évaluation du type de ton** :
            - **Alarmiste** : Le texte utilise un ton qui pourrait inquiéter ou alarmer les lecteurs, plus que nécessaire.
            - **Minimisant** : Le texte utilise un ton qui minimise les faits ou les risques, les rendant moins importants qu'ils ne le sont.
            - **Neutre** : Le texte présente les informations de manière équilibrée, sans exagération ni minimisation.

            **Évaluation de la pertinence** (séparément du type de ton) :
            - **Score 0** : Totalement hors de propos par rapport aux priorités du rapport.
            - **Score 1** : Très éloigné des priorités, manquant les points essentiels.
            - **Score 2** : Partiellement pertinent, couvre certains aspects mais ignore des points importants.
            - **Score 3** : Modérément pertinent, avec quelques priorités bien couvertes.
            - **Score 4** : Largement pertinent, aligné avec les points principaux du rapport.
            - **Score 5** : Parfaitement pertinent, en parfaite adéquation avec les priorités du rapport.

            **Extrait de l'article** :
            "{current_phrase}"

            **Sections du rapport du GIEC** :
            "{sections_resumees}"

            Répondez au format suivant en JSON:
            ```json
            {{
                "tone_type": "<alarmiste | minimisant | neutre>",
                "relevance_score": <score_entre_0_et_5>,
                "justifications": "<votre_justification_en_une_ou_plusieurs_phrases>"
            }}
            ```
            "",
            input_variables=["current_phrase", "sections_resumees"]
        ),
        "impartiality": PromptTemplate(
            template=""
            Vous êtes chargé d'analyser l'impartialité d'un extrait d'un article de presse par rapport aux informations du rapport du GIEC. Cette évaluation inclut la détection de biais, le cas échéant, et la direction de ce biais.

            **Évaluation de la direction du biais** :
            - **Exagération** : Le texte présente les faits de manière à les rendre plus significatifs ou graves qu'ils ne le sont.
            - **Minimisation** : Le texte présente les faits de manière à en réduire l'importance ou la gravité.
            - **Neutre** : Le texte est objectif et ne contient aucune exagération ou minimisation.

            **Évaluation de l'impartialité** :
            - **Score 0** : Fortement biaisé, avec de nombreuses expressions partiales.
            - **Score 1** : Biaisé, avec un langage manifestement partial.
            - **Score 2** : Modérément biaisé, quelques opinions subtiles ou une tendance à l'exagération ou à la minimisation.
            - **Score 3** : Légèrement biaisé, mais globalement objectif.
            - **Score 4** : Largement objectif, très peu de biais.
            - **Score 5** : Totalement objectif, sans aucune subjectivité.

            **Extrait de l'article** :
            "{current_phrase}"

            **Sections du rapport du GIEC** :
            "{sections_resumees}"

            Répondez au format suivant en JSON:
            ```json
            {{
                "bias_direction": "<exagération | minimisation | neutre>",
                "impartiality_score": <score_entre_0_et_5>,
                "justifications": "<votre_justification_en_une_ou_plusieurs_phrases>"
            }}
            ```
            "",
            input_variables=["current_phrase", "sections_resumees"]
        ),
        "information_quality": PromptTemplate(
            template=""
            Vous êtes chargé d'évaluer la qualité de l'information dans un extrait d'un article de presse en fonction des informations du rapport du GIEC. Cette évaluation inclut à la fois l'exactitude et la complétude des informations présentées.

            **Évaluation de l'exactitude** :
            - **Score 0** : Information totalement inexacte.
            - **Score 1** : Information largement inexacte, avec de nombreuses erreurs.
            - **Score 2** : Information partiellement inexacte, avec quelques erreurs significatives.
            - **Score 3** : Information modérément exacte, quelques imprécisions.
            - **Score 4** : Information largement exacte, avec seulement de légères imprécisions.
            - **Score 5** : Information parfaitement exacte.

            **Évaluation de la complétude** :
            - **Score 0** : Très incomplet, de nombreuses informations importantes sont manquantes.
            - **Score 1** : Incomplet, plusieurs points essentiels manquent.
            - **Score 2** : Partiellement complet, avec des informations importantes manquantes.
            - **Score 3** : Modérément complet, couvre l'essentiel.
            - **Score 4** : Largement complet, presque toutes les informations nécessaires sont présentes.
            - **Score 5** : Complètement complet, toutes les informations importantes sont présentes.

            **Extrait de l'article** :
            "{current_phrase}"

            **Sections du rapport du GIEC** :
            "{sections_resumees}"

            Répondez au format suivant en JSON:
            ```json
            {{
                "accuracy_score": <score_entre_0_et_5>,
                "completeness_score": <score_entre_0_et_5>,
                "justifications": "<votre_justification_en_une_ou_plusieurs_phrases>"
            }}
            ```
            "",
            input_variables=["current_phrase", "sections_resumees"]
        ),
        "clarity": PromptTemplate(
            template=""
            Vous êtes chargé d'évaluer la clarté et la lisibilité d'un extrait d'un article de presse en fonction de sa simplicité et de son accessibilité pour un public général.

            - **Score 0** : Très confus, difficile à lire et à comprendre.
            - **Score 1** : Peu clair, nécessite beaucoup d'efforts pour comprendre.
            - **Score 2** : Assez clair, mais certaines phrases ou idées sont difficiles à suivre.
            - **Score 3** : Modérément clair, quelques passages pourraient être simplifiés.
            - **Score 4** : Largement clair, facile à lire avec une structure compréhensible.
            - **Score 5** : Parfaitement clair, très facile à lire et accessible à tous les lecteurs.

            **Extrait de l'article** :
            "{current_phrase}"

            Répondez au format suivant en JSON:
            ```json
            {{
                "clarity_score": <score_entre_0_et_5>,
                "justifications": "<votre_justification_en_une_ou_plusieurs_phrases>"
            }}
            ```
            ",
            input_variables=["current_phrase"]
        )
    }
    return prompts

"""
