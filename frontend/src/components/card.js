import React, {Component} from 'react';
import {connect} from "react-redux";
import {navigate} from "../redux/actions";

class Card extends Component {

    componentDidMount() {
        document.title = this.props.name
    }

    navigate(event) {
        if (event.target.tagName === 'A'
            && event.target.hostname === window.location.hostname) {
            event.preventDefault();
            this.props.dispatch(navigate(event.target));
        }
    }

    render() {
        const {name, html} = this.props;
        return (
            <div>
                <h1>{name}</h1>
                <div
                    dangerouslySetInnerHTML={{__html: html}}
                    onClick={event => this.navigate(event)}
                />
            </div>
        );
    }

}

export default connect()(Card);
