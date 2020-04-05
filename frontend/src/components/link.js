import React, {Component} from "react"
import {connect} from "react-redux";
import {navigate} from "../redux/actions";
import {shouldOpenLinkInNewTab} from "../utility";

class Link extends Component {

    navigate(event) {
        if (shouldOpenLinkInNewTab(event.nativeEvent)){
            return;
        }
        event.preventDefault();
        this.props.dispatch(navigate(event.target));
    }

    render() {
        return <a href={this.props.href} onClick={event => this.navigate(event)}>{this.props.children}</a>
    }
}

export default connect()(Link);

export function composeHref(pathname, params) {
    let search = "?" + Object.keys(params).map(key => key + "=" + encodeURIComponent(params[key])).join("&");
    return pathname + search;
}
