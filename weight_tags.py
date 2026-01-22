#!/usr/bin/env python3
"""
Calculate weighted tag scores for quotes to enable thematic connections.

Weight factors:
1. Corpus frequency - how often the tag appears across all quotes (good for connections)
2. Quote relevance - how central the tag is to this specific quote

Excluded tags: 'book', 'pithy', 'quote' (too common/generic to provide meaning)
"""

import json
import math
import re
from collections import Counter
from pathlib import Path


EXCLUDED_TAGS = {'book', 'pithy', 'quote', 'people', 'trump', 'word'}


def load_quotes(path: str = 'site/quotes.json') -> list:
    with open(path) as f:
        return json.load(f)


def compute_tag_frequencies(quotes: list) -> Counter:
    """Count how often each tag appears across all quotes.

    Uses weighted_tags if available (curated), falls back to tags field.
    """
    all_tags = []
    for q in quotes:
        # Prefer weighted_tags (curated) over tags (original)
        if q.get('weighted_tags'):
            tags = [t['tag'] for t in q['weighted_tags']]
        else:
            tags = [t.lower() for t in q.get('tags', [])]

        # Exclude generic tags
        all_tags.extend([
            t for t in tags
            if t not in EXCLUDED_TAGS
        ])
    return Counter(all_tags)


def compute_corpus_frequency_score(tag_counts: Counter) -> dict:
    """
    Convert raw counts to a 0-1 score.
    Uses log scaling to prevent very common tags from dominating.
    """
    if not tag_counts:
        return {}

    max_count = max(tag_counts.values())
    scores = {}
    for tag, count in tag_counts.items():
        # Log-scaled score, normalized to 0-1
        scores[tag] = math.log(count + 1) / math.log(max_count + 1)
    return scores


def compute_quote_relevance(quote: dict, tag: str) -> float:
    """
    Compute how relevant a tag is to this specific quote.

    Factors:
    - Tag appears in quote text: high relevance (1.0)
    - Tag appears in author name: lower relevance (0.3)
    - Tag position in list: earlier = curator thought it was more important

    Returns a score between 0 and 1.
    """
    tag_lower = tag.lower()
    quote_text = quote.get('quote', '').lower()
    author = quote.get('author', '').lower()
    tags_list = [t.lower() for t in quote.get('tags', [])]

    score = 0.5  # Base score for being tagged

    # Check if tag (or its stem/variants) appears in quote text
    # Handle multi-word tags and common variations
    tag_words = tag_lower.split()
    tag_pattern = r'\b' + r'\b.*\b'.join(re.escape(w) for w in tag_words) + r'\b'

    if re.search(tag_pattern, quote_text):
        score += 0.4  # Significant boost for appearing in quote
    elif any(word in quote_text for word in tag_words if len(word) > 3):
        score += 0.2  # Partial boost for related word appearing

    # Reduce score if tag is just the author name
    if tag_lower in author or author in tag_lower:
        score *= 0.5  # Author tags less useful for thematic connections

    # Position bonus: earlier tags get slight boost
    if tag_lower in tags_list:
        position = tags_list.index(tag_lower)
        position_bonus = 0.1 * (1 - position / len(tags_list))
        score += position_bonus

    return min(score, 1.0)  # Cap at 1.0


def compute_weighted_tags(quotes: list) -> list:
    """
    For each quote, compute weighted scores for all its tags.
    Returns quotes with a new 'weighted_tags' field.
    """
    # First pass: compute corpus-wide tag frequencies
    tag_counts = compute_tag_frequencies(quotes)
    corpus_scores = compute_corpus_frequency_score(tag_counts)

    print(f"Total unique tags (after exclusions): {len(tag_counts)}")
    print(f"Top 10 tags by frequency:")
    for tag, count in tag_counts.most_common(10):
        print(f"  {tag}: {count} (corpus score: {corpus_scores[tag]:.3f})")
    print()

    # Second pass: compute weighted tags for each quote
    results = []
    for quote in quotes:
        # Prefer weighted_tags (curated) over tags (original)
        if quote.get('weighted_tags'):
            tags = [t['tag'] for t in quote['weighted_tags']]
        else:
            tags = [t.lower() for t in quote.get('tags', [])]

        weighted = []

        for tag in tags:
            if tag in EXCLUDED_TAGS:
                continue

            # Get corpus frequency score (0 if tag only appears in this quote)
            corpus_score = corpus_scores.get(tag, 0.1)

            # Get relevance to this quote
            relevance = compute_quote_relevance(quote, tag)

            # Combined weight: both factors matter
            # Corpus score ensures we can make connections
            # Relevance ensures the tag actually fits this quote
            # Use sqrt of corpus_score to reduce its dominance over relevance
            weight = math.sqrt(corpus_score) * relevance

            weighted.append({
                'tag': tag,
                'weight': round(weight, 4),
                'corpus_score': round(corpus_score, 4),
                'relevance': round(relevance, 4)
            })

        # Sort by weight descending
        weighted.sort(key=lambda x: x['weight'], reverse=True)

        # Create result with weighted_tags added
        result = quote.copy()
        result['weighted_tags'] = weighted
        results.append(result)

    return results


def print_example(quote: dict, n_tags: int = 5):
    """Pretty print a quote with its top weighted tags."""
    print(f"Quote: \"{quote['quote'][:80]}...\"" if len(quote.get('quote', '')) > 80 else f"Quote: \"{quote.get('quote')}\"")
    print(f"Author: {quote.get('author')}")
    print(f"Top {n_tags} weighted tags:")
    for t in quote.get('weighted_tags', [])[:n_tags]:
        print(f"  {t['tag']}: {t['weight']:.3f} (corpus: {t['corpus_score']:.3f}, relevance: {t['relevance']:.3f})")
    print()


def main():
    quotes = load_quotes()
    print(f"Loaded {len(quotes)} quotes\n")

    results = compute_weighted_tags(quotes)

    # Show examples
    print("=" * 60)
    print("EXAMPLE RESULTS")
    print("=" * 60)

    # Find specific example quotes
    for r in results:
        if 'globe by combat' in r.get('quote', '').lower():
            print("\nExample 1 - Networking quote:")
            print_example(r)
        if 'buildings in good repair' in r.get('quote', '').lower():
            print("\nExample 2 - Buildings quote:")
            print_example(r)

    # Show a few random examples
    import random
    print("\nRandom samples:")
    for r in random.sample(results, 3):
        print_example(r)

    # Save results - update main quotes.json with weighted_tags added
    output_path = Path('site/quotes.json')
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nUpdated {output_path} with weighted_tags")


if __name__ == '__main__':
    main()
