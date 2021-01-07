"""
wiki_topic_labels
=================

Suggest Wikipedia articles as possible labels
for a coherent list of terms, as produced by topic models.

Installation
------------

In lieu of putting on PyPi, please do:

    pip install wikipedia
    pip install git+git://github.com/nestauk/wiki_topic_labels/archive/master.zip

Only tested on OSX10.15.6, Python 3.7.

Usage:
------

    topic = ['beetle', 'live', 'yellow', 'strong']  # Fairly coherent, yet ambiguous topic

    # Default suggestions
    suggest_labels(topic)
    >>> ['Hercules beetle', 'Beetle', 'Livestrong Foundation']

    # Contextually anchored to "insects"
    suggest_labels(topic, contextual_anchors=['insects'])
    >>> ['Hercules beetle', 'Insect', 'Aquatic insect']

    # Contextually anchored to "music" and "band"
    suggest_labels(topic, contextual_anchors=['music', 'band'])
    >>> ['The Beatles', 'Gang of Four (band)', 'Yellow Magic Orchestra']

    # Contextually anchored to "car"
    suggest_labels(topics, topn=5, contextual_anchors=['car'])
    >>> ['Bumblebee (Transformers)', 'List of best-selling automobiles', 'Volkswagen Beetle']

As you can see, it does an ok job - which is sufficient for my use case.
I'd be happy to see a quantitative study on this, if anyone is volunteering!

Arguments:
----------

    topics (list): A list of arguments, nominally the topics from a topic model.

    contextual_anchors (list, optional): A list of extra terms to help Wikipedia disambiguate.
                                         For example, if the topic model has been trained on a corpus
                                         of scientific or research literature, the terms
                                         "science" and "research" may give better results.

    topn (int, default=3): The number of label suggestions to return, ordered by relevance. If set to `None`, all
                           available labels are returned.

    bootstrap_size (int, default=3): Size of bootstraps (number of topics per combination) to query Wikipedia with.

    boost_with_categories (list, optional): [SLOW] To boost the method a little further, this option will
                                            additionally extract Wikipedia categories for each label.
                                            Categories which are also labels are used to bolster the
                                            score of that label. In practice, this only tends to make
                                            much of a difference in a small number of cases, but improves
                                            the quality of the suggestions in those cases.

How does it work?
-----------------

All combinations of the terms in the topic are used to query Wikipedia's API. Wikipedia ranking
(I believe based on Elasticsearch ranking) returns relevant page titles, which are interpretted
as "labels". Bootstrapping over combinations helps to reduce the impact of spurious labels
from any one combination of terms in the topic. Since we don't know Wikipedia's actual ranking 
score (and it might not any be particularly meaningful), a score is assigned as
`2^{-i}` where `i` is relative positional ranking of the label, as returned by Wikipedia.
Topic scores are then summed over bootstraps, and the top-n results are returned.
"""
from collections import Counter, defaultdict
from itertools import combinations
from functools import lru_cache
import wikipedia


@lru_cache()
def rank_wiki_labels(query):
    """Return and rank Wikipedia suggestions, based on their order"""
    results = wikipedia.search(query)
    return Counter({result: 2**(-i) for i, result in enumerate(results)})


@lru_cache()
def get_wiki_cats(title):
    """Return Wikipedia categories for the given page title"""
    try:
        return wikipedia.page(title=title).categories
    except (wikipedia.PageError,
            wikipedia.DisambiguationError,
            wikipedia.WikipediaException):
        return []


def bootstrap_topic(topic, contextual_anchors, n_terms):
    """Yield topic bootstraps"""
    if n_terms > len(topic):
        n_terms = len(topic)
    for _topic in combinations(topic, n_terms):
        yield ' '.join(list(_topic) + contextual_anchors)


def bootstrap_labeller(topic, contextual_anchors, n_terms):
    """Apply the Wikipedia labeller over topics bootstraps"""    
    counts = Counter()
    for _topic in bootstrap_topic(topic, contextual_anchors, n_terms):
        ranked_labels = rank_wiki_labels(_topic)
        counts += ranked_labels
    return counts


def enrich_from_categories(counts, min_score=0.1, category_boost=2):
    """[EXPERIMENTAL] Additionally extract Wikipedia categories for each label.
    Categories which are also labels are used to bolster the score of that label."""        
    cumulator_terms = defaultdict(float)
    for term, score in counts.items():
        if score < min_score:
            continue
        for cat in get_wiki_cats(term):
            if cat == term:
                continue
            if cat not in counts:
                continue
            cumulator_terms[cat] = cumulator_terms[cat] + score
    for term, count in Counter(cumulator_terms).most_common():
        counts[term] = counts[term] + category_boost*count
    return counts


def suggest_labels(topic, contextual_anchors=[], topn=3,
                   bootstrap_size=3, boost_with_categories=False):
    """Suggest labels for the given topic"""
    counts = bootstrap_labeller(topic, contextual_anchors, bootstrap_size)
    if boost_with_categories:
        counts = enrich_from_categories(counts)
    labels = [label for label, _ in counts.most_common(topn)]
    return labels
