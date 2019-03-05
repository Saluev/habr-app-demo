import React, {Component} from 'react'
import {connect} from "react-redux";

import CardPage from "./cardPage"
import {navigate} from "../redux/actions";

class App extends Component {

    componentDidMount() {
        history.replaceState({
            pathname: location.pathname,
            href: location.href
        }, "");
        window.addEventListener("popstate", event => this.navigate(event));
    }

    navigate(event) {
        if (event.state && event.state.pathname) {
            event.preventDefault();
            event.stopPropagation();
            this.props.dispatch(navigate(event.state, true));
        }
    }

    render() {
        const {pageType} = this.props;
        return (
            <div>
                {pageType === "card" && <CardPage/>}
            </div>
        );
    }
}

function mapStateToProps(state) {
    const {page} = state;
    const {type} = page;
    return {
        pageType: type
    };
}

export default connect(mapStateToProps)(App);
