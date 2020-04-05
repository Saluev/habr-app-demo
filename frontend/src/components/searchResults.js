import React, {Component} from 'react';
import Link, {composeHref} from "./link";

class SearchResults extends Component {
    render() {
        let composeSearchLink = (tags, offset) => composeHref("/search", {
            "query": this.props.query,
            ...offset && {"offset": offset},
            ...tags && {"tags": tags.join(",")}
        });
        let currentTags = this.props.tags;
        let currentTagsSet = new Set(currentTags);
        let nextPageURL = composeSearchLink(currentTags, this.props.nextCardOffset);
        let urlWithTag = (tag) => composeSearchLink([tag, ...currentTags || []].sort());
        let urlWithoutTag = (tag) => composeSearchLink(currentTags.filter(t => t !== tag));
        return (
            <div>
                {this.props.totalCount} results<br/>
                {this.props.tagStats.map(stat =>
                    currentTagsSet.has(stat.tag)
                        ? <b key={stat.tag}><Link href={urlWithoutTag(stat.tag)}>{stat.tag}</Link> </b>
                        : <span key={stat.tag}><Link href={urlWithTag(stat.tag)}>{stat.tag}</Link> ({stat.cardCount}) </span>
                )}
                <ul>
                    {this.props.cards.map(card =>
                        <li key={card.id}>
                            <Link href={"/card/" + card.slug}>{card.name}</Link>
                        </li>
                    )}
                </ul>
                {this.props.nextCardOffset && <Link href={nextPageURL}>Next page...</Link>}
            </div>
        );
    }
}

export default SearchResults;
