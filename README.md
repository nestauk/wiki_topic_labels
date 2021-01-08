wiki_topic_labels
=================

Suggest Wikipedia articles as possible labels
for a coherent list of terms, as produced by topic models.

Installation
------------

In lieu of putting on PyPi, please do:

```bash
	pip install git+git://github.com/nestauk/wiki_topic_labels/archive/main.zip
```

Only tested on OSX10.15.6, Python 3.7.

Usage:
------

```python
    from wiki_topic_labels import suggest_labels

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

	# Boost with Wikipedia categories. Slower, but does a slightly better job.
	suggest_labels(topics, contextual_anchors=['car'], boost_with_categories=True)
	>>> ['Volkswagen Beetle', 'Bumblebee (Transformers)', 'List of best-selling automobiles']
```

As you can see, it does an ok job - which is sufficient for my use case.
I'd be happy to see a quantitative study on this, if anyone is volunteering!

Arguments:
----------

```
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
```

How does it work?
-----------------

All combinations of the terms in the topic are used to query Wikipedia's API. Wikipedia ranking
(I believe based on Elasticsearch ranking) returns relevant page titles, which are interpretted
as "labels". Bootstrapping over combinations helps to reduce the impact of spurious labels
from any one combination of terms in the topic. Since we don't know Wikipedia's actual ranking
score (and it might not any be particularly meaningful), a score is assigned as
`2^{-i}` where `i` is relative positional ranking of the label, as returned by Wikipedia.
Topic scores are then summed over bootstraps, and the top-n results are returned.
