import React, {Component} from 'react';
import Link from "./link";

class SearchResults extends Component {
    render() {
        let nextPageURL = "/search?query=" + encodeURIComponent(this.props.query) + "&offset=" + encodeURIComponent(this.props.nextCardOffset);
        return (
            <div>
                {this.props.totalCount} results
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
