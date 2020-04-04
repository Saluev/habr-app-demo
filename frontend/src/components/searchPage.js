import React, {Component} from 'react';
import {connect} from 'react-redux'
import {fetchSearchResultsIfNeeded} from '../redux/actions'
import SearchResults from "./searchResults";

class SearchPage extends Component {

    componentWillMount() {
        this.props.dispatch(fetchSearchResultsIfNeeded())
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
        this.props.dispatch(fetchSearchResultsIfNeeded())
    }

    render() {
        const {isFetching, searchResults} = this.props;
        return (
            <div>
                {isFetching && <h2>Loading...</h2>}
                {searchResults && <SearchResults query={this.props.query} offset={this.props.offset} {...searchResults}/>}
            </div>
        );
    }
}

function mapStateToProps(state) {
    const {page} = state;
    return page;
}

export default connect(mapStateToProps)(SearchPage);
