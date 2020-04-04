import React, {Component} from 'react';
import {connect} from "react-redux";
import {navigate} from "../redux/actions";

class SearchForm extends Component {

    constructor(props) {
        super(props);
        this.queryInputRef = React.createRef();
    }

    submit(event) {
        event.preventDefault();
        let link = document.createElement("a");
        link.href = "/search?query=" + encodeURIComponent(this.queryInputRef.current.value);
        this.props.dispatch(navigate(link));
    }

    render() {
        return (
            <form onSubmit={event => this.submit(event)}>
                <input name="query" type="text" ref={this.queryInputRef}/>
                <input type="submit" value="Search!"/>
            </form>
        );
    }
}

export default connect()(SearchForm)
