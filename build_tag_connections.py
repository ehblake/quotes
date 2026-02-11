#!/usr/bin/env python3
"""
Build tag connections/similarity data for tag drift navigation.

Two tags are "related" if they frequently appear together on the same quotes.
This creates natural thematic connections:
- life <-> existence, humanity, change
- creativity <-> design, art, ideas
- knowledge <-> understanding, learning, intelligence

Output: tag_connections.json with related tags for each tag, sorted by relatedness.
"""

import json
import math
from collections import Counter, defaultdict
from pathlib import Path


EXCLUDED_TAGS = {'book', 'pithy', 'quote', 'people', 'trump', 'word'}

# Curated list of approved primary tags (navigable themes)
# Only these tags will appear in tag_connections.json
ALLOWED_PRIMARY_TAGS = {
    'action', 'adventure', 'age', 'ageing', 'aim', 'america', 'anarchy',
    'architecture', 'art', 'artists', 'attitude', 'australia', 'banality',
    'beauty', 'belief', 'birth', 'books', 'the brain', 'bureaucracy',
    'calmness', 'capitalism', 'certainty', 'chance', 'change', 'chaos',
    'childhood', 'children', 'cities', 'civilisation', 'clarity',
    'collaboration', 'collapse', 'collecting', 'comfort', 'complexity',
    'connections', 'consciousness', 'consumption', 'control', 'creativity',
    'culture', 'curiosity', 'danger', 'darkness', 'death', 'decay',
    'definition', 'depth', 'design', 'destruction', 'the devil', 'devils',
    'difficulty', 'direction', 'disaster', 'discovery', 'doing', 'doom',
    'doubt', 'dreams', 'dying', 'earth', 'economics', 'education', 'emotion',
    'the end', 'end times', 'entropy', 'error', 'eschatology', 'ethics',
    'evil', 'evolution', 'existence', 'expectations', 'experience',
    'expression', 'eyes', 'facts', 'failure', 'faith', 'falsehood', 'fear',
    'fire', 'freedom', 'the future', 'gambling', 'garbage', 'god', 'good',
    'government', 'gratitude', 'happiness', 'heaven', 'hell', 'history',
    'honesty', 'humanity', 'humankind', 'humans', 'humour', 'ideas',
    'ignorance', 'imagination', 'improvement', 'individuality', 'information',
    'insanity', 'intelligence', 'interpretation', 'invention', 'jobs',
    'kings', 'knowledge', 'labour', 'language', 'laws', 'learning', 'liars',
    'libraries', 'life', 'literature', 'living', 'logic', 'looking', 'love',
    'luck', 'lying', 'machines', 'madness', 'making', 'mankind', 'mathematics',
    'meaning', 'media', 'memory', 'the mind', 'mistakes', 'money', 'monsters',
    'movement', 'museums', 'music', 'narrative', 'nature', 'the new',
    'nighttime', 'odds', 'opinion', 'order', 'originality', 'ownership',
    'pain', 'painting', 'the past', 'paths', 'patience', 'perception',
    'perfection', 'perspective', 'pessimism', 'philosophy', 'play', 'pleasure',
    'poems', 'poetry', 'politics', 'power', 'prediction', 'the present',
    'problem solving', 'problems', 'process', 'progress', 'property',
    'psychology', 'purpose', 'quotes', 'reading', 'reality', 'religion',
    'revolution', 'ruin', 'rules', 'sadness', 'satisfaction', 'science',
    'seeing', 'the sea', 'the self', 'the senses', 'serendipity', 'simplicity',
    'simplification', 'society', 'songs', 'speaking', 'spirit', 'stories',
    'storytelling', 'stupidity', 'success', 'suffering', 'talking',
    'technology', 'thinking', 'thought', 'time', 'torture', 'travel', 'truth',
    'uncertainty', 'understanding', 'uniqueness', 'the unknown', 'utopia',
    'values', 'views', 'violence', 'vision', 'walking', 'wandering', 'war',
    'why', 'wisdom', 'wit', 'wonder', 'words', 'work', 'the world', 'writing',
}


def load_quotes(path: str = 'site/quotes.json') -> list:
    with open(path) as f:
        return json.load(f)


def build_cooccurrence_matrix(quotes: list) -> dict:
    """
    Build a matrix of how often each pair of tags appears together.
    Returns {tag: {other_tag: count, ...}, ...}
    """
    cooccur = defaultdict(Counter)
    tag_counts = Counter()

    for q in quotes:
        # Prefer weighted_tags (curated) over tags (original)
        if q.get('weighted_tags'):
            tags = [t['tag'] for t in q['weighted_tags']]
        else:
            tags = [t.lower() for t in q.get('tags', [])]
        # Filter excluded tags
        tags = [t for t in tags if t not in EXCLUDED_TAGS]
        # Remove author-like tags (those matching author name)
        author = q.get('author', '').lower()
        tags = [t for t in tags if t not in author and author not in t]

        # Count individual tags
        for tag in tags:
            tag_counts[tag] += 1

        # Count co-occurrences
        for i, tag1 in enumerate(tags):
            for tag2 in tags[i+1:]:
                cooccur[tag1][tag2] += 1
                cooccur[tag2][tag1] += 1

    return cooccur, tag_counts


def compute_tag_similarity(cooccur: dict, tag_counts: Counter) -> dict:
    """
    Compute similarity scores between tags using PMI (Pointwise Mutual Information).

    PMI = log(P(a,b) / (P(a) * P(b)))

    High PMI means tags appear together more than expected by chance.
    We also factor in absolute co-occurrence count to avoid rare tag pairs
    dominating due to statistical noise.
    """
    total_quotes = sum(tag_counts.values()) / 2  # Rough estimate
    similarities = defaultdict(dict)

    for tag1, cooccur_tags in cooccur.items():
        if tag_counts[tag1] < 3:  # Skip very rare tags
            continue

        for tag2, count in cooccur_tags.items():
            if tag_counts[tag2] < 3:
                continue
            if count < 2:  # Need at least 2 co-occurrences
                continue

            # Calculate PMI-like score
            p_tag1 = tag_counts[tag1] / total_quotes
            p_tag2 = tag_counts[tag2] / total_quotes
            p_both = count / total_quotes

            # Avoid log(0) and very small values
            if p_tag1 * p_tag2 > 0:
                pmi = math.log(p_both / (p_tag1 * p_tag2) + 0.001)
            else:
                pmi = 0

            # Combine PMI with raw count (both matter)
            # PMI tells us if association is meaningful
            # Count tells us if it's reliable
            score = pmi * math.log(count + 1)

            if score > 0:
                similarities[tag1][tag2] = round(score, 4)

    return similarities


def build_tag_connections(quotes: list) -> dict:
    """
    Build the final tag connections structure.

    Returns: {
        tag: {
            related: [{tag: "...", score: 0.xx}, ...],  // sorted by score desc
            quote_count: N,  // how many quotes have this tag
        },
        ...
    }
    """
    cooccur, tag_counts = build_cooccurrence_matrix(quotes)
    similarities = compute_tag_similarity(cooccur, tag_counts)

    connections = {}

    for tag, count in tag_counts.items():
        if count < 3:  # Skip very rare tags
            continue
        if tag not in ALLOWED_PRIMARY_TAGS:  # Only include curated primary tags
            continue

        related = []
        if tag in similarities:
            for other_tag, score in similarities[tag].items():
                # Only include related tags that are also in the allowed list
                if other_tag in ALLOWED_PRIMARY_TAGS:
                    related.append({'tag': other_tag, 'score': score})

        # Sort by score descending
        related.sort(key=lambda x: x['score'], reverse=True)

        connections[tag] = {
            'related': related[:15],  # Top 15 related tags
            'quote_count': count
        }

    return connections


def main():
    quotes = load_quotes()
    print(f"Loaded {len(quotes)} quotes")

    connections = build_tag_connections(quotes)
    print(f"Built connections for {len(connections)} tags")

    # Show some examples
    print("\n" + "=" * 60)
    print("EXAMPLE TAG CONNECTIONS")
    print("=" * 60)

    example_tags = ['life', 'creativity', 'understanding', 'city', 'time', 'knowledge', 'design', 'existence']
    for tag in example_tags:
        if tag in connections:
            print(f"\n{tag} ({connections[tag]['quote_count']} quotes):")
            for r in connections[tag]['related'][:5]:
                print(f"  -> {r['tag']}: {r['score']:.3f}")

    # Save
    output_path = Path('site/tag_connections.json')
    with open(output_path, 'w') as f:
        json.dump(connections, f, indent=2)
    print(f"\nSaved to {output_path}")


if __name__ == '__main__':
    main()
