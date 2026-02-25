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

# Manual thematic connections for tags that don't co-occur enough in the data.
# Each entry is {tag: {related_tag: score, ...}} and bidirectional.
# Scores range 2.8-4.2: tight pairs (antonyms, near-synonyms) score higher,
# looser thematic links score lower.
MANUAL_CONNECTIONS = {
    # === 0-connection tags ===
    'architecture': {'design': 4.2, 'cities': 4.0, 'art': 3.5, 'civilisation': 3.2, 'making': 2.9},
    'attitude': {'perspective': 4.0, 'opinion': 3.8, 'values': 3.5, 'the self': 3.2},
    'australia': {'travel': 4.0, 'adventure': 3.8, 'nature': 3.5, 'the world': 3.0},
    'calmness': {'patience': 4.2, 'acceptance': 3.8, 'the mind': 3.2, 'wisdom': 2.9},
    'complexity': {'simplicity': 4.2, 'order': 3.8, 'chaos': 3.5, 'understanding': 3.2, 'science': 2.8},
    'consumption': {'capitalism': 4.2, 'modernity': 3.8, 'desire': 3.5, 'society': 3.0},
    'danger': {'fear': 4.0, 'destruction': 3.8, 'violence': 3.5, 'adventure': 3.2, 'chaos': 3.0},
    'depth': {'understanding': 4.0, 'perception': 3.8, 'the mind': 3.5, 'seeing': 3.0},
    'ethics': {'values': 4.2, 'good': 4.0, 'honesty': 3.8, 'truth': 3.5, 'philosophy': 3.2},
    'freedom': {'anarchy': 4.2, 'rebellion': 4.0, 'individuality': 3.8, 'power': 3.5, 'authority': 3.2},
    'gratitude': {'happiness': 4.0, 'acceptance': 3.5, 'wisdom': 3.0, 'life': 2.8},
    'heaven': {'hell': 4.2, 'god': 4.0, 'religion': 3.8, 'faith': 3.5, 'death': 3.2},
    'improvement': {'progress': 4.2, 'learning': 3.8, 'change': 3.5, 'process': 3.2},
    'logic': {'mathematics': 4.2, 'thinking': 3.8, 'science': 3.5, 'philosophy': 3.2, 'truth': 3.0},
    'luck': {'chance': 4.2, 'gambling': 4.0, 'serendipity': 3.8, 'odds': 3.5, 'uncertainty': 3.0},
    'museums': {'collecting': 4.2, 'art': 4.0, 'culture': 3.8, 'libraries': 3.5, 'memory': 3.2},
    'play': {'childhood': 4.2, 'imagination': 3.8, 'creativity': 3.5, 'freedom': 3.0},
    'prediction': {'the future': 4.2, 'uncertainty': 3.8, 'odds': 3.5, 'science': 3.2},
    'problems': {'problem solving': 4.2, 'difficulty': 4.0, 'thinking': 3.2, 'understanding': 2.8},
    'property': {'ownership': 4.2, 'laws': 3.8, 'capitalism': 3.5, 'society': 3.0},
    'simplification': {'simplicity': 4.2, 'complexity': 3.8, 'clarity': 3.5, 'design': 3.2},
    'success': {'failure': 4.2, 'ambition': 4.0, 'money': 3.5, 'work': 3.2},
    'the sea': {'nature': 4.0, 'travel': 3.8, 'adventure': 3.5, 'the world': 3.2, 'walking': 3.0},
    'uniqueness': {'individuality': 4.2, 'originality': 4.0, 'the self': 3.5, 'creativity': 3.0},

    # === 1-connection tags ===
    'acceptance': {'calmness': 4.0, 'patience': 3.8, 'wisdom': 3.5, 'change': 3.0},
    'beauty': {'wonder': 4.0, 'nature': 3.8, 'seeing': 3.5, 'perception': 3.2},
    'economics': {'money': 4.2, 'consumption': 3.8, 'property': 3.5, 'society': 3.0},
    'failure': {'success': 4.2, 'learning': 3.5, 'doubt': 3.0},
    'gambling': {'luck': 4.2, 'chance': 4.0, 'uncertainty': 3.5},
    'garbage': {'decay': 4.0, 'consumption': 3.8, 'modernity': 3.2},
    'good': {'values': 4.0, 'ethics': 3.8, 'truth': 3.5},
    'information': {'knowledge': 4.0, 'media': 3.8, 'technology': 3.5, 'truth': 3.0},
    'interpretation': {'meaning': 4.0, 'narrative': 3.8, 'understanding': 3.5, 'reading': 3.2},
    'laws': {'government': 4.0, 'authority': 3.8, 'order': 3.5, 'power': 3.2},
    'mathematics': {'logic': 4.2, 'science': 3.8, 'order': 3.2},
    'movement': {'walking': 4.0, 'wandering': 3.8, 'action': 3.5, 'direction': 3.2},
    'narrative': {'stories': 4.2, 'interpretation': 3.8, 'meaning': 3.5, 'literature': 3.2},
    'ownership': {'property': 4.2, 'capitalism': 3.5, 'freedom': 3.2, 'power': 3.0},
    'pleasure': {'satisfaction': 4.2, 'happiness': 4.0, 'comfort': 3.8, 'desire': 3.5},
    'politics': {'government': 4.2, 'power': 4.0, 'authority': 3.8, 'society': 3.2},
    'process': {'making': 4.0, 'doing': 3.8, 'work': 3.5, 'design': 3.0},
    'satisfaction': {'pleasure': 4.2, 'happiness': 4.0, 'comfort': 3.5},
    'spirit': {'faith': 4.0, 'the self': 3.8, 'religion': 3.5, 'freedom': 3.0},
    'talking': {'speaking': 4.2, 'language': 4.0, 'words': 3.8},
    'torture': {'suffering': 4.2, 'pain': 4.0, 'violence': 3.8, 'evil': 3.5},
    'travel': {'adventure': 4.2, 'wandering': 3.8, 'walking': 3.5, 'the world': 3.2, 'discovery': 3.0},
    'wit': {'humour': 4.2, 'words': 3.8, 'language': 3.5, 'intelligence': 3.0},

    # === 2-connection tags ===
    'adventure': {'travel': 4.0, 'discovery': 3.8, 'the unknown': 3.5, 'danger': 3.2},
    'age': {'time': 4.0, 'memory': 3.8, 'wisdom': 3.5, 'death': 3.2},
    'certainty': {'faith': 4.0, 'truth': 3.8, 'belief': 3.5, 'knowledge': 3.2},
    'chaos': {'entropy': 4.0, 'destruction': 3.8, 'the end': 3.5, 'danger': 3.2},
    'childhood': {'play': 4.0, 'education': 3.8, 'memory': 3.5, 'age': 3.2},
    'civilisation': {'culture': 4.2, 'history': 4.0, 'cities': 3.8, 'progress': 3.5, 'architecture': 3.2},
    'collaboration': {'process': 4.0, 'making': 3.8, 'ideas': 3.5},
    'comfort': {'calmness': 4.0, 'pleasure': 3.8, 'satisfaction': 3.5},
    'disaster': {'destruction': 4.2, 'chaos': 4.0, 'doom': 3.8, 'the end': 3.5, 'danger': 3.2},
    'doing': {'making': 4.0, 'process': 3.8, 'work': 3.5, 'living': 3.2},
    'dreams': {'imagination': 4.0, 'nighttime': 3.8, 'the unknown': 3.5, 'consciousness': 3.2},
    'emotion': {'sadness': 4.0, 'the mind': 3.8, 'love': 3.5, 'pain': 3.2},
    'entropy': {'chaos': 4.2, 'destruction': 3.8, 'doom': 3.5, 'time': 3.2},
    'expression': {'art': 4.0, 'language': 3.8, 'creativity': 3.5},
    'jobs': {'labour': 4.2, 'money': 3.5, 'capitalism': 3.2, 'purpose': 3.0},
    'monsters': {'fear': 4.0, 'the devil': 3.8, 'hell': 3.5, 'violence': 3.0},
    'music': {'culture': 4.0, 'art': 3.8, 'poetry': 3.5, 'beauty': 3.2},
    'nighttime': {'dreams': 4.0, 'the unknown': 3.5, 'fear': 3.2, 'death': 2.8},
    'odds': {'chance': 4.2, 'luck': 4.0, 'uncertainty': 3.8, 'prediction': 3.5},
    'originality': {'the new': 4.2, 'invention': 4.0, 'uniqueness': 3.8, 'ideas': 3.5},
    'pain': {'torture': 3.8, 'emotion': 3.5, 'living': 3.2, 'death': 3.0},
    'painting': {'seeing': 4.2, 'vision': 4.0, 'beauty': 3.8, 'design': 3.2},
    'perfection': {'simplicity': 4.0, 'beauty': 3.8, 'making': 3.2},
    'revolution': {'anarchy': 4.2, 'power': 4.0, 'freedom': 3.8, 'politics': 3.5, 'violence': 3.2},
    'sadness': {'suffering': 4.0, 'pain': 3.8, 'emotion': 3.5, 'death': 3.2},

    # === Thematic bridges: perception → art/creativity ===
    'looking': {'art': 3.8, 'wonder': 3.5, 'creativity': 3.2},
    'vision': {'art': 4.0, 'creativity': 3.5, 'wonder': 3.2},
    'wonder': {'art': 3.8, 'seeing': 3.5, 'looking': 3.2, 'creativity': 3.0},
    'the senses': {'seeing': 4.0, 'perception': 3.8, 'looking': 3.5, 'art': 3.2, 'experience': 3.0},
    'eyes': {'looking': 4.2, 'vision': 4.0, 'wonder': 3.5},

    # === Mind/philosophy cluster tightening ===
    'philosophy': {'thinking': 4.0, 'the mind': 3.8, 'consciousness': 3.5, 'knowledge': 3.2},
    'consciousness': {'the mind': 4.0, 'the brain': 3.8, 'philosophy': 3.5},
    'the mind': {'consciousness': 4.0, 'philosophy': 3.5},

    # === Poetry/language bridge ===
    'poetry': {'writing': 4.0, 'literature': 3.8, 'language': 3.5},
    'reading': {'writing': 3.8, 'language': 3.5},

    # === Darkness into its cluster ===
    'darkness': {'doom': 3.8, 'destruction': 3.5, 'death': 3.2, 'evil': 3.0},

    # === Nature cluster ===
    'earth': {'the world': 4.0, 'the sea': 3.5, 'walking': 3.0},
}

# Curated list of approved primary tags (navigable themes)
# Only these tags will appear in tag_connections.json
ALLOWED_PRIMARY_TAGS = {
    'acceptance', 'action', 'adventure', 'age', 'ageing', 'aim', 'ambition',
    'america', 'anarchy',
    'architecture', 'art', 'artists', 'attitude', 'authority', 'australia',
    'banality', 'beauty', 'belief', 'birth', 'books', 'the brain', 'bureaucracy',
    'calmness', 'capitalism', 'certainty', 'chance', 'change', 'chaos',
    'childhood', 'children', 'cities', 'civilisation', 'clarity',
    'collaboration', 'collapse', 'collecting', 'comfort', 'complexity',
    'connections', 'consciousness', 'consumption', 'control', 'creativity',
    'culture', 'curiosity', 'danger', 'darkness', 'death', 'decay',
    'definition', 'depth', 'design', 'desire', 'destruction', 'the devil', 'devils',
    'difficulty', 'direction', 'disaster', 'discovery', 'doing', 'doom',
    'doubt', 'dreams', 'dying', 'earth', 'economics', 'education', 'emotion',
    'the end', 'end times', 'entropy', 'error', 'eschatology', 'ethics',
    'evil', 'evolution', 'existence', 'expectations', 'experience',
    'expression', 'eyes', 'facts', 'failure', 'faith', 'falsehood', 'fear',
    'fire', 'freedom', 'the future', 'gambling', 'garbage', 'god', 'good',
    'government', 'gratitude', 'happiness', 'heaven', 'hell', 'history',
    'honesty', 'humanity', 'humankind', 'humans', 'humility', 'humour', 'ideas',
    'ignorance', 'imagination', 'improvement', 'individuality', 'information',
    'insanity', 'intelligence', 'interpretation', 'invention', 'jobs',
    'kings', 'knowledge', 'labour', 'language', 'laws', 'learning', 'liars',
    'libraries', 'life', 'literature', 'living', 'logic', 'looking', 'love',
    'luck', 'lying', 'machines', 'madness', 'making', 'mankind', 'mathematics',
    'meaning', 'media', 'memory', 'the mind', 'mistakes', 'modernity', 'money',
    'monsters',
    'movement', 'museums', 'music', 'narrative', 'nature', 'the new',
    'nighttime', 'odds', 'opinion', 'order', 'originality', 'ownership',
    'pain', 'painting', 'the past', 'paths', 'patience', 'perception',
    'perfection', 'perspective', 'pessimism', 'philosophy', 'play', 'pleasure',
    'poems', 'poetry', 'politics', 'power', 'prediction', 'the present',
    'problem solving', 'problems', 'process', 'progress', 'property',
    'psychology', 'purpose', 'quotes', 'reading', 'reality', 'rebellion', 'religion',
    'revolution', 'ruin', 'rules', 'sadness', 'satisfaction', 'science',
    'seeing', 'the sea', 'the self', 'the senses', 'serendipity', 'simplicity',
    'simplification', 'society', 'songs', 'speaking', 'spirit', 'stories',
    'storytelling', 'stupidity', 'success', 'suffering', 'talking',
    'technology', 'thinking', 'thought', 'time', 'torture', 'travel', 'truth',
    'uncertainty', 'understanding', 'uniqueness', 'the unknown', 'utopia',
    'values', 'views', 'violence', 'vision', 'walking', 'wandering', 'war',
    'weakness', 'why', 'wisdom', 'wit', 'wonder', 'words', 'work', 'the world',
    'writing',
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


def expand_manual_connections() -> dict:
    """
    Expand MANUAL_CONNECTIONS into a bidirectional map with scores.
    If A lists B at score S, then B also gets A at score S.
    Returns {tag: {other_tag: score, ...}}.
    """
    bidir = defaultdict(dict)
    for tag, targets in MANUAL_CONNECTIONS.items():
        for target, score in targets.items():
            if target in ALLOWED_PRIMARY_TAGS and tag in ALLOWED_PRIMARY_TAGS:
                bidir[tag][target] = score
                if target not in bidir or tag not in bidir[target]:
                    bidir[target][tag] = score
    return bidir


def build_tag_connections(quotes: list) -> dict:
    """
    Build the final tag connections structure.
    Combines co-occurrence data with manual thematic connections.

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
    manual = expand_manual_connections()

    connections = {}

    for tag, count in tag_counts.items():
        if count < 3:  # Skip very rare tags
            continue
        if tag not in ALLOWED_PRIMARY_TAGS:  # Only include curated primary tags
            continue

        related = {}
        # Add co-occurrence connections
        if tag in similarities:
            for other_tag, score in similarities[tag].items():
                if other_tag in ALLOWED_PRIMARY_TAGS:
                    related[other_tag] = score

        # Merge manual connections (only if not already present with higher score)
        if tag in manual:
            for other_tag, mscore in manual[tag].items():
                if other_tag not in related:
                    related[other_tag] = mscore

        # Convert to sorted list
        related_list = [{'tag': t, 'score': s} for t, s in related.items()]
        related_list.sort(key=lambda x: x['score'], reverse=True)

        connections[tag] = {
            'related': related_list[:15],  # Top 15 related tags
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
